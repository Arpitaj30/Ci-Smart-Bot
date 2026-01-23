import asyncio
import logging
from .error_analyzer import analyze_error
from .fixer import apply_patch, commit_and_push
from .github_client import GitHubClient
from .memory import save_patch, load_patch

logger = logging.getLogger(__name__)

class BotRunner:
    def __init__(self):
        import os
        self.client = GitHubClient(
            app_id=os.getenv("GITHUB_APP_ID"),
            private_key=os.getenv("GITHUB_PRIVATE_KEY")
        )
    
    async def handle_github_event(self, event_type: str, payload: dict):
        """Handle GitHub webhook events"""
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
        except KeyError as e:
            logger.error(f"Missing required field in payload: {str(e)}")
        except Exception as e:
            logger.error(f"Error handling event {event_type}: {str(e)}", exc_info=True)
    
    async def analyze_and_fix(self, repo: str, run_id: int, installation_id: int):
        """Analyze CI failure and post fix comment"""
        try:
            # Analyze the error
            analysis, patch = analyze_error(f"Run ID: {run_id}")
            
            # Get PR number from run
            pr_number = 1  # Would extract from workflow run details
            
            # Save patch for later use
            save_patch(repo, pr_number, patch)
            
            # Post comment on PR
            self.client.comment_on_pr(
                repo, pr_number,
                f"""🤖 **CI Analysis**\n\n**Root Cause:**\n{analysis}\n\n**Auto-Fix Ready**\nI can apply a fix. React with ✅ to approve.""",
                installation_id
            )
        except Exception as e:
            logger.error(f"Error analyzing {repo}: {str(e)}")

bot = BotRunner()

async def handle_github_event(event_type: str, payload: dict):
    await bot.handle_github_event(event_type, payload)

async def process_workflow_run(payload: dict):
    await bot.analyze_and_fix(
        repo=payload["repository"]["full_name"],
        run_id=payload["workflow_run"]["id"],
        installation_id=payload["installation"]["id"]
    )
