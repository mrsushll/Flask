#!/usr/bin/env python3
"""
Standalone script to run the Ravyn.ai Telegram bot.
"""

import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram_bot.bot import TelegramBot

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Main function to run the bot."""
    try:
        # Initialize the bot
        bot = TelegramBot()
        
        # Set the webhook URL
        webhook_url = os.environ.get('WEBHOOK_URL', 'https://work-1-agbdcklhstakqvwk.prod-runtime.all-hands.dev')
        if not webhook_url.endswith('/'):
            webhook_url += '/'
        webhook_url += 'webhook'
        
        logger.info(f"Setting webhook to {webhook_url}")
        
        # Start the bot
        await bot.start()
        
        # Explicitly set webhook after bot starts
        logger.info("Bot started, now setting webhook...")
        await bot.client.send_request('setWebhook', {
            'url': webhook_url,
            'max_connections': 100,
            'allowed_updates': ['message', 'callback_query', 'inline_query']
        })
        logger.info(f"Webhook set to {webhook_url}")
        
        # Get webhook info to verify
        webhook_info = await bot.get_webhook_info()
        logger.info(f"Webhook info: {webhook_info}")
        
        # Keep the bot running
        logger.info("Bot is now running. Press Ctrl+C to stop.")
        while True:
            await asyncio.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Error running bot: {e}")

if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())