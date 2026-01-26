# import asyncio
# import logging
# from unittest.mock import patch
# from bot.error_analyzer import analyze_error
# from bot.fixer import apply_patch, commit_and_push
# from bot.github_client import GitHubClient
# from bot.memory import save_patch, load_patch

# logger = logging.getLogger(__name__)

# class BotRunner:
#     def __init__(self):
#         import os
#         self.client = GitHubClient(
#             app_id=os.getenv("GITHUB_APP_ID"),
#             private_key=os.getenv("GITHUB_PRIVATE_KEY")
#         )
    
#     async def handle_github_event(self, event_type: str, payload: dict):
#         """Handle GitHub webhook events"""
#         try:
#             if event_type == "workflow_run":
#                 action = payload.get("action")
#                 if action == "completed":
#                     conclusion = payload.get("workflow_run", {}).get("conclusion")
#                     if conclusion == "failure":
#                         await self.analyze_and_fix(
#                             repo=payload["repository"]["full_name"],
#                             run_id=payload["workflow_run"]["id"],
#                             installation_id=payload["installation"]["id"]
#                         )
#             elif event_type == "pull_request":
#                 action = payload.get("action")
#                 if action == "opened":
#                     repo_name = payload.get("repository", {}).get("full_name", "unknown")
#                     logger.info(f"PR opened in {repo_name}")
        
#         except KeyError as e:
#             logger.error(f"Missing required field in payload: {str(e)}")
        
#         except Exception as e:
#             logger.error(f"Error handling event {event_type}: {str(e)}", exc_info=True)
    
#     async def analyze_and_fix(self, repo: str, run_id: int, installation_id: int):
#         """Analyze CI failure and post fix comment"""
#         try:
#             # Fetch workflow logs
#             logs = self.client.get_workflow_logs(repo, run_id, installation_id)

#             # Analyze the error
#             analysis, patch = analyze_error(logs)

#             # Get PR number dynamically
#             pr_number = self.client.get_pr_from_run(repo, run_id, installation_id)
#             if not pr_number:
#                 logger.info("No PR associated with this workflow run")
#                 return
            
#             # Save patch for later use
#             save_patch(repo, pr_number, patch)

#             if not patch:
#                 self.client.comment_on_pr(
#                     repo, pr_number,
#                     "🤖 I analyzed the failure but could not generate a safe fix.",
#                     installation_id
#                 )
#                 return

#             # 🔥 APPLY FIX
#             if apply_patch(patch) and commit_and_push():
#                 self.client.comment_on_pr(
#                     repo, pr_number,
#                     f"""✅ **Auto-fix applied**
#                     **Root cause** {analysis}
#                     I have pushed a fix commit. Please review the changes.""",
#                     installation_id
#                 )
            
#             else:
#                 self.client.comment_on_pr(
#                     repo, pr_number,
#                     "⚠️ Fix was generated but could not be applied automatically.",
#                     installation_id
#                 )
            
#             # Post comment on PR
#             self.client.comment_on_pr(
#                 repo, pr_number,
#                 f"""🤖 **CI Analysis**\n\n**Root Cause:**\n{analysis}\n\n**Auto-Fix Ready**\nI can apply a fix. React with ✅ to approve.""",
#                 installation_id
#             )
#         except Exception as e:
#             logger.error(f"Error analyzing {repo}: {str(e)}")

# bot = BotRunner()

# async def handle_github_event(event_type: str, payload: dict):
#     await bot.handle_github_event(event_type, payload)

# async def process_workflow_run(payload: dict):
#     await bot.analyze_and_fix(
#         repo=payload["repository"]["full_name"],
#         run_id=payload["workflow_run"]["id"],
#         installation_id=payload["installation"]["id"]
#     )






import os
import asyncio
import logging
import subprocess

from bot.error_analyzer import analyze_error
from bot.fixer import apply_patch, commit_and_push
from bot.github_client import GitHubClient
from bot.memory import save_patch

logger = logging.getLogger(__name__)


class BotRunner:
    def __init__(self):
        self.client = GitHubClient(
            app_id=os.getenv("GITHUB_APP_ID"),
            private_key=os.getenv("GITHUB_PRIVATE_KEY"),
            GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
        )

    async def handle_github_event(self, event_type: str, payload: dict):
        try:
            if event_type == "workflow_run":
                action = payload.get("action")
                if action == "completed":
                    conclusion = payload.get("workflow_run", {}).get("conclusion")
                    if conclusion == "failure":
                        await self.analyze_and_fix(
                            repo=payload["repository"]["full_name"],
                            run_id=payload["workflow_run"]["id"],
                            installation_id=payload["installation"]["id"]
                        )

            elif event_type == "pull_request":
                action = payload.get("action")
                if action == "opened":
                    repo_name = payload.get("repository", {}).get("full_name", "unknown")
                    logger.info(f"PR opened in {repo_name}")

        except Exception as e:
            logger.error(f"Error handling event {event_type}: {str(e)}", exc_info=True)

    async def analyze_and_fix(self, repo: str, run_id: int, installation_id: int):
        try:
            logger.info(f"Fetching workflow logs for {repo} run {run_id}")

            # 1️⃣ Get real workflow logs
            logs = self.client.get_workflow_logs(repo, run_id, installation_id)

            # 2️⃣ Analyze logs with LLM
            analysis, patch = analyze_error(logs)

            # 3️⃣ Get PR number from workflow run
            pr_number = self.client.get_pr_from_run(repo, run_id, installation_id)
            if not pr_number:
                logger.warning("No PR associated with this workflow run")
                return

            # Save patch for audit/debug
            save_patch(repo, pr_number, patch)

            # 4️⃣ If no patch generated
            if not patch:
                self.client.comment_on_pr(
                    repo, pr_number,
                    "🤖 I analyzed the failure but could not generate a safe fix.",
                    installation_id
                )
                return

            # 5️⃣ Basic patch validation
            if "diff --git" not in patch:
                self.client.comment_on_pr(
                    repo, pr_number,
                    "⚠️ Generated patch was invalid and was not applied.",
                    installation_id
                )
                return

            # 6️⃣ Clone repo if not present
            repo_dir = repo.split("/")[-1]
            if not os.path.isdir(repo_dir):
                subprocess.run(["git", "clone", f"https://github.com/{repo}.git"], check=True)

            os.chdir(repo_dir)

            # 7️⃣ Apply + commit + push
            applied = apply_patch(patch)
            pushed = commit_and_push() if applied else False

            # 8️⃣ Comment back with correct status
            if applied and pushed:
                self.client.comment_on_pr(
                    repo, pr_number,
                    f"""✅ **Auto-fix applied**

**Root cause**
{analysis}

I have pushed a fix commit. Please review the changes.""",
                    installation_id
                )

            elif applied and not pushed:
                self.client.comment_on_pr(
                    repo, pr_number,
                    "⚠️ Fix was applied locally but could not be pushed. Check permissions or branch protection.",
                    installation_id
                )

            else:
                self.client.comment_on_pr(
                    repo, pr_number,
                    "⚠️ Fix was generated but could not be applied automatically.",
                    installation_id
                )

        except Exception as e:
            logger.error(f"Error analyzing/fixing {repo}: {str(e)}", exc_info=True)

bot = BotRunner()

async def handle_github_event(event_type: str, payload: dict):
    await bot.handle_github_event(event_type, payload)