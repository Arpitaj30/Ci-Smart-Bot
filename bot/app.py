from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/")
def root():
    return {"status": "CI/CD Smart Bot running"}

@app.post("/webhook")
async def github_webhook(request: Request):
    payload = await request.json()
    event = request.headers.get("X-GitHub-Event")

    print("GitHub Event:", event)
    print("Payload received")

    return {"message": "Webhook received"}