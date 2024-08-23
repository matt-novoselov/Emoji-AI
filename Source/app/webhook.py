import logging
from fastapi import APIRouter, Request, HTTPException
from aiogram.types import Update
from app.bot import bot, dp
from app.config import WEBHOOK_DOMAIN


# Create a new router
webhook_route = APIRouter()


# Set up a webhook on Telegram server
async def set_webhook():
    webhook_info = await bot.get_webhook_info()
    current_webhook_url = webhook_info.url

    # Local variable to store the modified URL
    webhook_url = WEBHOOK_DOMAIN

    # Enforce domain certificate to be https://
    if not webhook_url.startswith("https://"):
        # Remove any existing scheme (http://, https://, etc.) and prepend https://
        if "://" in webhook_url:
            webhook_url = "https://" + webhook_url.split("://", 1)[1]
        else:
            webhook_url = "https://" + webhook_url

    # Check if the webhook is already set to the desired domain
    if current_webhook_url != webhook_url:
        await bot.set_webhook(url=webhook_url,
                              allowed_updates=dp.resolve_used_update_types(),
                              drop_pending_updates=True)
        logging.info(f"Webhook updated to: {webhook_url}")
    else:
        logging.info("Webhook is already correctly set.")


# Webhook processing
async def webhook(request: Request) -> None:
    try:
        # Parse the incoming JSON payload from the request
        update = Update.model_validate(await request.json(), context={"bot": bot})
        await dp.feed_update(bot, update)
    except Exception as e:
        # Log any errors that occur while processing the update
        logging.error(f"Error handling update: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
