# import os
# import logging
# import subprocess

# from bot.error_analyzer import analyze_error
# from bot.fixer import apply_patch, commit_and_push
# from bot.github_client import GitHubClient
# from bot.memory import save_patch

# logger = logging.getLogger(__name__)


# class BotRunner:
#     def __init__(self):
#         self.client = GitHubClient(
#             app_id=os.getenv("GITHUB_APP_ID"),
#             private_key=os.getenv("GITHUB_PRIVATE_KEY"),
#         )

#     async def handle_github_event(self, event_type: str, payload: dict):
#         try:
#             if event_type == "workflow_run":
#                 if payload.get("workflow_run", {}).get("conclusion") == "failure":
#                     await self.analyze_and_fix(
#                         repo=payload["repository"]["full_name"],
#                         run_id=payload["workflow_run"]["id"],
#                         installation_id=payload["installation"]["id"]
#                     )

#             elif event_type == "pull_request_review":
#                 if payload["review"]["state"] == "approved":
#                     self.client.merge_pr(
#                         payload["repository"]["full_name"],
#                         payload["pull_request"]["number"],
#                         payload["installation"]["id"]
#                     )

#         except Exception as e:
#             logger.error(f"Webhook handling failed: {e}", exc_info=True)

#     async def analyze_and_fix(self, repo, run_id, installation_id):
#         logger.info(f"Analyzing CI failure: {repo} #{run_id}")

#         logs = self.client.get_workflow_logs(repo, run_id, installation_id)
#         analysis, patch = analyze_error(logs)

#         if not patch or "diff --git" not in patch:
#             logger.warning("Invalid patch generated")
#             return

#         branch = f"ci-fix-{run_id}"

#         if not os.path.isdir(repo.split("/")[-1]):
#             subprocess.run(["git", "clone", f"https://github.com/{repo}.git"], check=True)

#         os.chdir(repo.split("/")[-1])
#         subprocess.run(["git", "checkout", "-b", branch], check=True)

#         if not apply_patch(patch):
#             return

#         if not commit_and_push(branch):
#             return

#         pr = self.client.create_pull_request(
#             repo=repo,
#             head=branch,
#             base="main",
#             title="🤖 Auto CI Fix",
#             body=f"**Root Cause**\n{analysis}",
#             installation_id=installation_id
#         )

#         self.client.comment_on_pr(
#             repo,
#             pr.number,
#             "✅ Fix applied automatically. Please review & approve.",
#             installation_id
#         )

#     def commit_and_push(self, branch, msg="CI Bot auto-fix"):
#         subprocess.run(["git", "add", "."], check=True)
#         subprocess.run(["git", "commit", "-m", msg], check=True)
#         subprocess.run(["git", "push", "-u", "origin", branch], check=True)
#         return True
    

import os
import logging
import subprocess
import tempfile
from unittest import result

from bot.error_analyzer import analyze_error
from bot.fixer import apply_patch, commit_and_push
from bot.github_client import GitHubClient

logger = logging.getLogger(__name__)


class BotRunner:
    def __init__(self):
        self.client = GitHubClient(
            app_id=os.getenv("GITHUB_APP_ID"),
            private_key=os.getenv("GITHUB_PRIVATE_KEY"),
        )

    async def handle_github_event(self, event_type: str, payload: dict):
        try:
            if event_type == "workflow_run":
                if payload.get("workflow_run", {}).get("conclusion") == "failure":
                    await self.analyze_and_fix(
                        repo=payload["repository"]["full_name"],
                        run_id=payload["workflow_run"]["id"],
                        installation_id=payload["installation"]["id"]
                    )

            elif event_type == "ci_failure":
                result = await self.analyze_and_fix(
                repo=payload["repo"],
                run_id=payload["run_id"],
                installation_id=payload["installation_id"],
                logs=payload["logs"],
            )

            elif event_type == "pull_request_review":
                if payload["review"]["state"] == "approved":
                    self.client.merge_pr(
                        payload["repository"]["full_name"],
                        payload["pull_request"]["number"],
                        payload["installation_id"],
                    )

            return {
                "suggestion": result or "No automated fix could be generated."
            }

        except Exception as e:
            logger.error("BotRunner failed", exc_info=True)
            return f"CI analysis failed due to internal error: {str(e)}"


    
    async def analyze_and_fix(self, repo, run_id, installation_id, logs):
        analysis, patch = analyze_error(logs)
        result_text = analysis
        logger.info(f"Analyzing CI failure for {repo} run {run_id}")

        if not patch or "diff --git" not in patch:
            logger.error("Invalid or empty patch from LLM")
            return result_text

        repo_name = repo.split("/")[-1]
        workdir = tempfile.mkdtemp()
        os.chdir(workdir)

        token = self.client.get_installation_token(installation_id)

        subprocess.run(
            [
                "git",
                "clone",
                f"https://x-access-token:{token}@github.com/{repo}.git",
            ],
            check=True,
        )

        os.chdir(repo_name)
        branch = f"ci-fix-{run_id}"
        subprocess.run(["git", "checkout", "-b", branch], check=True)

        if not apply_patch(patch):
            return

        if not commit_and_push():
            return

        pr = self.client.create_pull_request(
            repo=repo,
            head=branch,
            base="main",
            title="🤖 Auto CI Fix",
            body=f"### Root Cause\n{analysis}",
            installation_id=installation_id,
        )

        self.client.comment_on_pr(
            repo,
            pr.number,
            "✅ CI issue fixed automatically. Please review & approve.",
            installation_id,
        )