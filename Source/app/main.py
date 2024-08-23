import logging
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.webhook import set_webhook, webhook


# Manage the lifecycle of the app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure the correct webhook is set on Telegram server when the app starts
    await set_webhook()
    yield


# Create a FastAPI application
app = FastAPI(lifespan=lifespan)

# Handle webhook POST request at root domain
app.add_api_route("/", webhook, methods=["POST"])

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)

    # Run Uvicorn to start a server
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="error")
