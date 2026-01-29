import os
import logging
import subprocess
import tempfile
import asyncio
import json

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
        """
        Handles different GitHub webhook events dynamically.
        """
        result = None
        try:
            if event_type == "workflow_run":
                if payload.get("workflow_run", {}).get("conclusion") == "failure":
                    repo = payload["repository"]["full_name"]
                    
                    # Fetch logs dynamically using GitHubClient
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
                    logs=payload.get("logs"),
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

    async def analyze_and_fix(self, repo, run_id, installation_id, logs=None):
        """
        Analyze CI logs with LLM and apply automatic fixes.
        """
        logger.info(f"Analyzing CI failure for {repo} run {run_id}")

        # If logs not provided, fetch dynamically from GitHub
        if not logs:
            logs = await self.client.get_workflow_run_logs(repo, run_id, installation_id)

        # Ask LLM asynchronously (wrap synchronous call)
        llm_response = await asyncio.to_thread(ask_llm, logs)

        # Parse structured JSON from LLM
        try:
            result = json.loads(llm_response)
            analysis = result.get("analysis", "")
            patch = result.get("patch", "")
        except Exception:
            analysis = llm_response
            patch = ""

        if not patch or "diff --git" not in patch:
            logger.warning("LLM returned no valid patch")
            return analysis

        # Create temp working directory
        repo_name = repo.split("/")[-1]
        workdir = tempfile.mkdtemp()
        os.chdir(workdir)

        # Get installation token
        token = self.client.get_installation_token(installation_id)

        # Clone repo
        # subprocess.run(
        #     ["git", "clone", f"https://x-access-token:{token}@github.com/{repo}.git"],
        #     check=True,
        # )

        os.chdir(repo_name)
        branch = f"ci-fix-{run_id}"
        subprocess.run(["git", "checkout", "-b", branch], check=True)

        # Apply patch
        if not apply_patch(patch):
            logger.error("Failed to apply patch")
            return analysis

        # Commit and push
        if not commit_and_push():
            logger.error("Failed to commit and push patch")
            return analysis

        # Create PR
        pr = self.client.create_pull_request(
            repo=repo,
            head=branch,
            base="main",
            title="🤖 Auto CI Fix",
            body=f"### Root Cause\n{analysis}\n\n### Suggested Fix\n{patch}",
            installation_id=installation_id,
        )

        # Comment on PR
        self.client.comment_on_pr(
            repo,
            pr.number,
            "✅ CI issue fixed automatically. Please review & approve.",
            installation_id,
        )

        return analysis