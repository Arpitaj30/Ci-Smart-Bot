from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
from bot.bot_runner import handle_github_event
from .logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)       # Get a logger for this module, method called here from logging_config.py

app = FastAPI(title="AI CI Fix Bot")


@app.get("/health")       #it is decorator by fastAPI GitHub Actions, ngrok testing, Docker, Kubernetes - to check if server is alive
def health():
    return {"status": "running"}


@app.get("/")
def root():
    return {
        "status": "running",
        "endpoints": {                #endpoint is url+http method where another system can send a request and your server listens and reacts.
            "health": "/health",
            "webhook": "/webhook",
            "docs": "/docs"
        }
    }


@app.post("/webhook")
async def github_webhook(request: Request):              # this function is bot’s brain entry point
    """
    GitHub webhook endpoint (NO signature verification)
    """
    try:
        event = request.headers.get("X-GitHub-Event")      # X-GitHub-Event: Get the event type from headers ie workflow run, push, pull_request, check_run

        try:
            payload = await request.json()
        except Exception as e:
            logger.warning(f"Invalid JSON payload: {e}")
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Invalid JSON payload"
                }
            )

        if not event:
            logger.warning("Missing X-GitHub-Event header")
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Missing X-GitHub-Event header"
                }
            )

        logger.info(f"Received GitHub event: {event}")

        if event in ["workflow_run", "pull_request", "check_run"]:
            await handle_github_event(event, payload)               #Calling bot brain      
            return {"status": "processed", "event": event}

        return {"status": "ignored", "event": event}

    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error"
            }
        )

@app.post("/analyze")
async def analyze_ci_failure(request: Request):
    """
    Endpoint called by GitHub Actions.
    Receives CI logs and triggers AI fix logic.
    """
    try:
        payload = await request.json()

        repo = payload.get("repo")
        run_id = payload.get("run_id")
        logs = payload.get("logs")

        if not repo or not logs:
            logger.warning("Missing repo or logs in /analyze payload")
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Missing repo or logs"
                }
            )

        logger.info(
            f"Received CI logs for repo={repo}, run_id={run_id}"
        )

        # 🔥 Reuse your existing bot brain
        await handle_github_event(
            event="ci_failure",
            payload={
                "repo": repo,
                "run_id": run_id,
                "logs": logs
            }
        )

        return {
            "status": "analysis_started",
            "repo": repo,
            "run_id": run_id
        }

    except Exception as e:
        logger.error(f"Error in /analyze endpoint: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error"
            }
        )
