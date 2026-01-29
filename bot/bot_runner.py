import os
import logging
import subprocess
import tempfile
import asyncio
import json
from unittest import result

from bot.error_analyzer import analyze_error
from bot.fixer import apply_patch, commit_and_push
from bot.github_client import GitHubClient
from bot.llm_engine import ask_llm

logger = logging.getLogger(__name__)


class BotRunner:
    def __init__(self):
        self.client = GitHubClient(
            app_id=os.getenv("GITHUB_APP_ID"),
            private_key=os.getenv("GITHUB_PRIVATE_KEY"),
        )

    async def handle_github_event(self, event_type: str, payload: dict):
        result = None
        try:
            if event_type == "workflow_run":
                if payload.get("workflow_run", {}).get("conclusion") == "failure":
                    # Fetch logs dynamically using GitHubClient
                    repo = payload["repository"]["full_name"]
                    run_id = payload["workflow_run"]["id"]
                    installation_id = payload["installation"]["id"]
                    logs = await self.client.get_workflow_run_logs(repo, run_id, installation_id)

                    result = await self.analyze_and_fix(
                        repo=repo,
                        run_id=run_id,
                        installation_id=installation_id,
                        logs=logs
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
        logger.info(f"Analyzing CI failure for {repo} run {run_id}")

        # Ask LLM to analyze logs and suggest a fix
        # Wrap synchronous ask_llm in asyncio.to_thread to not block event loop
        llm_response = await asyncio.to_thread(ask_llm, logs)

        # Parse structured JSON
        result = json.loads(llm_response)
        analysis = result.get("analysis", "")
        patch = result.get("patch", "")

        # Expect LLM to return combined string with analysis + patch suggestion
        # If you want structured output, you can parse it here
        # For now, let's split patch from analysis using a separator (optional)
        # Example: assume LLM returns "---PATCH---" before git diff
        # if "---PATCH---" in analysis_result:
        #     analysis, patch = analysis_result.split("---PATCH---", 1)
        # else:
        #     analysis = analysis_result
        #     patch = ""

        if not patch or "diff --git" not in patch:
            logger.error("Invalid or empty patch from LLM")
            return analysis

        repo_name = repo.split("/")[-1]
        workdir = tempfile.mkdtemp()
        os.chdir(workdir)

        token = self.client.get_installation_token(installation_id)

        # subprocess.run(
        #     [
        #         "git",
        #         "clone",
        #         f"https://x-access-token:{token}@github.com/{repo}.git",
        #     ],
        #     check=True,
        # )

        os.chdir(repo_name)
        branch = f"ci-fix-{run_id}"
        subprocess.run(["git", "checkout", "-b", branch], check=True)

        if not apply_patch(patch):
            return analysis

        if not commit_and_push():
            return analysis

        pr = self.client.create_pull_request(
            repo=repo,
            head=branch,
            base="main",
            title="🤖 Auto CI Fix",
            body=f"### Root Cause\n{analysis}\n\n### Suggested Fix\n{patch}",
            installation_id=installation_id,
        )

        self.client.comment_on_pr(
            repo,
            pr.number,
            "✅ CI issue fixed automatically. Please review & approve.",
            installation_id,
        )

        return analysis