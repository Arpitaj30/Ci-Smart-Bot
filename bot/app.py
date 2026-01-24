from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
from bot.bot_runner import handle_github_event
from .logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="AI CI Fix Bot")


@app.get("/health")
def health():
    return {"status": "running"}


@app.get("/")
def root():
    return {
        "status": "running",
        "endpoints": {
            "health": "/health",
            "webhook": "/github/webhook",
            "docs": "/docs"
        }
    }


@app.post("/webhook")
async def github_webhook(request: Request):
    """
    GitHub webhook endpoint (NO signature verification)
    """
    try:
        event = request.headers.get("X-GitHub-Event")

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

        if event in ["workflow_run", "pull_request"]:
            await handle_github_event(event, payload)
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


















# from fastapi import FastAPI, Request, HTTPException
# from fastapi.responses import JSONResponse
# import logging
# from bot.bot_runner import handle_github_event
# import hmac, hashlib, os
# # from .bot_runner import handle_github_event
# from .logging_config import setup_logging

# # Setup logging
# setup_logging()
# logger = logging.getLogger(__name__)

# app = FastAPI(title="AI CI Fix Bot")

# GITHUB_WEBHOOK_SECRET = os.getenv("CI AGENT")

# # def verify_signature(payload_body, signature):
# #     mac = hmac.new(GITHUB_WEBHOOK_SECRET.encode(), msg=payload_body, digestmod=hashlib.sha256)
# #     return hmac.compare_digest(f"sha256={mac.hexdigest()}", signature)

# @app.get("/health")
# def health():
#     return {"status": "running"}

# @app.get("/")
# def root():
#     return {
#         "status": "running",
#         "endpoints": {
#             "health": "/health",
#             "webhook": "/github/webhook",
#             "docs": "/docs"
#         }
#     }

# @app.post("/github/webhook")
# async def github_webhook(request: Request):
#     """GitHub App webhook endpoint for workflow run events"""
#     try:
#         # Get event type from headers
#         event = request.headers.get("X-GitHub-Event")
        
#         # Parse JSON payload
#         try:
#             payload = await request.json()
#         except Exception as e:
#             logger.warning(f"Invalid JSON payload: {str(e)}")
#             return JSONResponse(
#                 status_code=400,
#                 content={
#                     "status": "error",
#                     "message": "Invalid JSON payload. Please send valid JSON data."
#                 }
#             )
        
#         # Validate event type
#         if not event:
#             logger.warning("No X-GitHub-Event header provided")
#             return JSONResponse(
#                 status_code=400,
#                 content={
#                     "status": "error",
#                     "message": "Missing X-GitHub-Event header"
#                 }
#             )
        
#         logger.info(f"Received GitHub event: {event}")
        
#         # Handle workflow_run and pull_request events
#         if event in ["workflow_run", "pull_request"]:
#             await handle_github_event(event, payload)
#             return {"status": "processed", "event": event}
#         else:
#             logger.info(f"Ignoring event type: {event}")
#             return {"status": "ignored", "event": event}
    
#     except Exception as e:
#         logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
#         return JSONResponse(
#             status_code=500,
#             content={
#                 "status": "error",
#                 "message": "Internal server error"
#             }
#         )
    
# @app.post("/github/webhook")
# async def github_webhook(request: Request):
#     event = request.headers.get("X-GitHub-Event")
#     payload = await request.json()

#     logger.info(f"Received GitHub event: {event}")

#     if event in ["workflow_run", "pull_request"]:
#         await handle_github_event(event, payload)
#         return {"status": "processed", "event": event}

#     return {"status": "ignored", "event": event}

    

# # bot/app.py
# # from fastapi import FastAPI, Request, Header
# # from bot.bot_runner import handle_github_event
# # import hmac, hashlib, os

# # app = FastAPI()

# # GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")

# # def verify_signature(payload_body, signature):
# #     mac = hmac.new(GITHUB_WEBHOOK_SECRET.encode(), msg=payload_body, digestmod=hashlib.sha256)
# #     return hmac.compare_digest(f"sha256={mac.hexdigest()}", signature)

# # @app.post("/github/webhook")
# # async def github_webhook(request: Request, x_hub_signature_256: str = Header(None)):
# #     body = await request.body()
# #     if not verify_signature(body, x_hub_signature_256):
# #         return {"status": "invalid signature"}
# #     event = await request.json()
# #     # Forward event to bot_runner for processing
# #     await handle_github_event(event)
# #     return {"status": "received"}