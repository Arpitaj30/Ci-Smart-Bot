from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
from bot.bot_runner import handle_github_event
from .logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="AI CI Fix Bot")


@app.get("/health")
def health():
    return {"status": "running"}


@app.post("/analyze")
async def analyze_ci_failure(request: Request):
    try:
        payload = await request.json()

        required = ["repo", "run_id", "logs", "installation_id"]
        for key in required:
            if key not in payload:
                return JSONResponse(
                    status_code=400,
                    content={"error": f"Missing {key}"}
                )

        await handle_github_event("ci_failure", payload)

        return {"status": "processing_started"}

    except Exception as e:
        logger.error(e, exc_info=True)
        return JSONResponse(status_code=500, content={"error": "Internal error"})

