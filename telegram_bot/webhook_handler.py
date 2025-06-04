#!/usr/bin/env python3
"""
Webhook Handler for Telegram Bot
Handles incoming webhook requests from Telegram
"""

import json
import logging
import os
from aiohttp import web
from telethon import TelegramClient, events

from telegram_bot.utils.logger import setup_logger

# Configure logging
logger = setup_logger('webhook_handler')

class WebhookHandler:
    """Handles webhook requests from Telegram."""
    
    def __init__(self, bot):
        """Initialize the webhook handler.
        
        Args:
            bot: The TelegramBot instance
        """
        self.bot = bot
        self.webhook_url = os.environ.get('WEBHOOK_URL', '')
        self.webhook_path = self.webhook_url.split('/')[-1] if self.webhook_url else 'webhook'
        
        # Create web app
        self.app = web.Application()
        self.setup_routes()
    
    def setup_routes(self):
        """Set up the routes for the web app."""
        self.app.router.add_post(f'/{self.webhook_path}', self.handle_webhook)
        self.app.router.add_get('/health', self.health_check)
    
    async def start(self, host='0.0.0.0', port=8080):
        """Start the webhook server.
        
        Args:
            host: The host to bind to
            port: The port to bind to
        """
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        logger.info(f"Webhook server started at {host}:{port}")
    
    async def handle_webhook(self, request):
        """Handle incoming webhook requests from Telegram.
        
        Args:
            request: The request object
        
        Returns:
            A web response
        """
        try:
            data = await request.json()
            logger.debug(f"Received webhook data: {data}")
            
            # Process the update
            await self.bot.process_update(data)
            
            return web.Response(text='OK')
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            return web.Response(text='Error', status=500)
    
    async def health_check(self, request):
        """Handle health check requests.
        
        Args:
            request: The request object
        
        Returns:
            A web response
        """
        return web.Response(text='OK')