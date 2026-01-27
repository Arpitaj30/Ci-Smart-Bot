from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

from bot.bot_runner import BotRunner
from .logging_config import setup_logging

# ----------------- logging -----------------
setup_logging()
logger = logging.getLogger(__name__)

# ----------------- app -----------------
app = FastAPI(title="AI CI Fix Bot")

# 🔥 SINGLE bot runner instance
runner = BotRunner()


# ----------------- health -----------------
@app.get("/health")
def health():
    return {"status": "running"}


# ----------------- GitHub webhook -----------------
@app.post("/webhook")
async def github_webhook(request: Request):
    """
    GitHub webhook entry point
    """
    try:
        event_type = request.headers.get("X-GitHub-Event")

        if not event_type:
            return JSONResponse(
                status_code=400,
                content={"error": "Missing X-GitHub-Event header"}
            )

        payload = await request.json()

        logger.info(f"Received GitHub event: {event_type}")

        await runner.handle_github_event(event_type, payload)

        return {"status": "processed", "event": event_type}

    except Exception as e:
        logger.error("Webhook processing failed", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )


# ----------------- CI analyze (manual / Actions) -----------------
@app.post("/analyze")
async def analyze_ci_failure(request: Request):
    """
    Called manually or by GitHub Actions
    """
    try:
        payload = await request.json()

        required = ["repo", "run_id", "logs", "installation_id"]
        for key in required:
            if key not in payload:
                return JSONResponse(
                    status_code=400,
                    content={"error": f"Missing {key}"}
                )

        logger.info(
            f"Analyze request: repo={payload['repo']} run_id={payload['run_id']}"
        )

        # 👇 route into SAME bot brain
        await runner.handle_github_event(
            "ci_failure",
            payload
        )

        return {"status": "processing_started"}

    except Exception:
        logger.error("Analyze endpoint failed", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )