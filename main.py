# """
# Entry point for the CI/CD Bot application.
# Run with: python -m main
# Or: uvicorn main:app --host 0.0.0.0 --port 8000
# """

# import os
# from bot.app import app

# if __name__ == "__main__":
#     import uvicorn
    
#     port = int(os.getenv("PORT", "8000"))
#     host = os.getenv("HOST", "0.0.0.0")
    
#     uvicorn.run(
#         "main:app",
#         host=host,
#         port=port,
#         reload=os.getenv("ENV", "production") == "development"
#     )





"""
Entry point for the CI/CD Bot application.

Usage:
1️ Run FastAPI server:
   uvicorn main:app --host 0.0.0.0 --port 8000
"""

import os
import asyncio
import logging

from bot.app import app
from bot.bot_runner import BotRunner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_bot():
    """
    Run the BotRunner for dynamic CI log analysis and automated fixes.
    Works for any GitHub repo.
    """
    repo = os.getenv("GITHUB_REPOSITORY")
    run_id = os.getenv("GITHUB_RUN_ID")
    installation_id = int(os.getenv("GITHUB_INSTALLATION_ID", "1"))
    logs_path = os.getenv("CI_LOGS_PATH")

    # Load logs from file if provided
    logs = None
    if logs_path and os.path.exists(logs_path):
        with open(logs_path, "r") as f:
            logs = f.read()

    runner = BotRunner()

    suggestion = await runner.analyze_and_fix(
        repo=repo,
        run_id=run_id,
        installation_id=installation_id,
        logs=logs  # If None, BotRunner fetches logs dynamically
    )

    logger.info("LLM Suggestion / Analysis:\n%s", suggestion)
    print("LLM Suggestion / Analysis:\n", suggestion)


if __name__ == "__main__":
    import sys
    import uvicorn

    # Check if the bot should run or server should start
    if len(sys.argv) > 1 and sys.argv[1] == "bot":
        # Run the bot (async)
        asyncio.run(run_bot())
    else:
        # Start FastAPI server
        port = int(os.getenv("PORT", "8000"))
        host = os.getenv("HOST", "0.0.0.0")
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=os.getenv("ENV", "production") == "development"
        )
