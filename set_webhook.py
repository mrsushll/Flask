#!/usr/bin/env python3
"""
Script to set the webhook for the Ravyn.ai Telegram bot.
"""

import os
import asyncio
import logging
import json
import requests
from dotenv import load_dotenv
from telegram_bot.bot import TelegramBot

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Set the webhook for the bot."""
    bot = None
    try:
        # Initialize the bot
        bot = TelegramBot()
        
        # Start the client
        await bot.client.start(bot_token=bot.bot_token)
        
        # Set the webhook URL
        webhook_url = os.environ.get('WEBHOOK_URL', 'https://work-1-agbdcklhstakqvwk.prod-runtime.all-hands.dev')
        if not webhook_url.endswith('/'):
            webhook_url += '/'
        webhook_url += 'webhook'
        
        logger.info(f"Setting webhook to {webhook_url}")
        
        # Set the webhook with Telegram API using requests
        import requests
        
        # Get the bot token
        bot_token = bot.bot_token
        
        # Set the webhook
        set_webhook_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        params = {
            'url': webhook_url,
            'max_connections': 100,
            'allowed_updates': json.dumps(['message', 'callback_query', 'inline_query'])
        }
        
        response = requests.post(set_webhook_url, params=params)
        result = response.json()
        
        logger.info(f"Webhook set result: {result}")
        
        # Get webhook info to verify
        get_webhook_info_url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
        response = requests.get(get_webhook_info_url)
        webhook_info = response.json()
        
        logger.info(f"Webhook info: {webhook_info}")
        
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
    finally:
        # Disconnect the client
        if bot and bot.client:
            await bot.client.disconnect()

if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())