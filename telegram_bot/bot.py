#!/usr/bin/env python3
"""
ChatGpt Claude Mistral Telegram Bot
A highly advanced Telegram bot that integrates multiple AI models for chat and image generation.
Developed by: @MLBOR
"""

import asyncio
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

import i18n
from telethon import TelegramClient, events
from telethon.tl import types
from telethon.tl.custom import Button

# Import local modules
from database.mongodb import MongoDB
from ai_models.openai_handler import OpenAIHandler
from ai_models.claude_handler import ClaudeHandler
from ai_models.mistral_handler import MistralHandler
from ai_models.image_generator import ImageGenerator
from handlers.command_handler import CommandHandler
from handlers.admin_handler import AdminHandler
from handlers.subscription_handler import SubscriptionHandler
from utils.rate_limiter import RateLimiter
from utils.logger import setup_logger

# Load environment variables
load_dotenv()

# Configure logging
logger = setup_logger('bot')

# Configure internationalization
i18n.load_path.append('./locales')
i18n.set('fallback', 'en')

class TelegramBot:
    """Main Telegram Bot class that handles all interactions."""
    
    def __init__(self):
        """Initialize the bot with all required components."""
        # Telegram API credentials
        self.api_id = int(os.getenv('TELEGRAM_API_ID'))
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        
        # Admin username
        self.admin_username = 'MLBOR'
        
        # Initialize the Telegram client
        self.client = TelegramClient('chatgpt_claude_mistral_bot', self.api_id, self.api_hash)
        
        # Initialize database connection
        self.db = MongoDB(os.getenv('MONGODB_URI', 'mongodb+srv://mrsushi:7Fcbd82ae7@cluster0.zok5y5d.mongodb.net/'))
        
        # Initialize AI model handlers
        self.openai_handler = OpenAIHandler(os.getenv('OPENAI_API_KEY'))
        self.claude_handler = ClaudeHandler(os.getenv('ANTHROPIC_API_KEY'))
        self.mistral_handler = MistralHandler(os.getenv('MISTRAL_API_KEY'))
        self.image_generator = ImageGenerator(os.getenv('OPENAI_API_KEY'))
        
        # Initialize handlers
        self.command_handler = CommandHandler(self)
        self.admin_handler = AdminHandler(self)
        self.subscription_handler = SubscriptionHandler(self)
        
        # Initialize rate limiter
        self.rate_limiter = RateLimiter()
        
        # User session storage
        self.user_sessions = {}
        
    async def start(self):
        """Start the bot and register all event handlers."""
        await self.client.start(bot_token=self.bot_token)
        
        # Register event handlers
        self.register_handlers()
        
        logger.info("Bot started successfully!")
        
        # Run the client until disconnected
        await self.client.run_until_disconnected()
    
    def register_handlers(self):
        """Register all event handlers for the bot."""
        # Command handlers
        self.client.add_event_handler(self.command_handler.start_command, events.NewMessage(pattern='/start'))
        self.client.add_event_handler(self.command_handler.help_command, events.NewMessage(pattern='/help'))
        self.client.add_event_handler(self.command_handler.settings_command, events.NewMessage(pattern='/settings'))
        self.client.add_event_handler(self.command_handler.balance_command, events.NewMessage(pattern='/balance'))
        self.client.add_event_handler(self.command_handler.models_command, events.NewMessage(pattern='/models'))
        self.client.add_event_handler(self.command_handler.language_command, events.NewMessage(pattern='/language'))
        
        # Admin command handlers
        self.client.add_event_handler(self.admin_handler.admin_command, events.NewMessage(pattern='/admin'))
        self.client.add_event_handler(self.admin_handler.add_tokens_command, events.NewMessage(pattern='/add_tokens'))
        self.client.add_event_handler(self.admin_handler.user_info_command, events.NewMessage(pattern='/user_info'))
        self.client.add_event_handler(self.admin_handler.broadcast_command, events.NewMessage(pattern='/broadcast'))
        self.client.add_event_handler(self.admin_handler.stats_command, events.NewMessage(pattern='/stats'))
        
        # Subscription handlers
        self.client.add_event_handler(self.subscription_handler.subscribe_command, events.NewMessage(pattern='/subscribe'))
        
        # AI chat handlers
        self.client.add_event_handler(self.handle_chat_message, events.NewMessage(func=lambda e: e.is_private and not e.message.text.startswith('/')))
        
        # Callback query handlers
        self.client.add_event_handler(self.handle_callback, events.CallbackQuery())
    
    async def handle_chat_message(self, event):
        """Handle regular chat messages from users."""
        user_id = event.sender_id
        message = event.message.text
        
        # Check if user exists in database, if not create a new user
        user = await self.db.get_user(user_id)
        if not user:
            username = event.sender.username or "Unknown"
            await self.db.create_user(user_id, username)
            user = await self.db.get_user(user_id)
        
        # Check rate limits
        if not self.rate_limiter.check_rate_limit(user_id):
            await event.respond(i18n.t('rate_limit_exceeded', locale=user.get('language', 'en')))
            return
        
        # Check if user has enough tokens
        if user.get('tokens', 0) <= 0:
            keyboard = [
                [Button.inline(i18n.t('subscribe_button', locale=user.get('language', 'en')), b'subscribe')]
            ]
            await event.respond(
                i18n.t('no_tokens', locale=user.get('language', 'en')),
                buttons=keyboard
            )
            return
        
        # Get user's preferred AI model
        model = user.get('preferred_model', 'gpt')
        
        # Send typing indicator
        async with self.client.action(event.chat_id, 'typing'):
            try:
                # Process message with the appropriate AI model
                if model == 'gpt':
                    response = await self.openai_handler.generate_response(message, user.get('conversation_history', []))
                elif model == 'claude':
                    response = await self.claude_handler.generate_response(message, user.get('conversation_history', []))
                elif model == 'mistral':
                    response = await self.mistral_handler.generate_response(message, user.get('conversation_history', []))
                else:
                    # Default to GPT if model preference is invalid
                    response = await self.openai_handler.generate_response(message, user.get('conversation_history', []))
                
                # Update conversation history
                conversation_history = user.get('conversation_history', [])
                conversation_history.append({'role': 'user', 'content': message})
                conversation_history.append({'role': 'assistant', 'content': response})
                
                # Limit conversation history to last 10 exchanges
                if len(conversation_history) > 20:
                    conversation_history = conversation_history[-20:]
                
                # Update user's conversation history in database
                await self.db.update_user(user_id, {
                    'conversation_history': conversation_history,
                    'tokens': user.get('tokens', 0) - 1,  # Deduct one token for the chat
                    'last_activity': datetime.now()
                })
                
                # Log the interaction
                await self.db.log_interaction(user_id, 'chat', model, 1)
                
                # Send the response
                await event.respond(response)
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await event.respond(i18n.t('error_processing', locale=user.get('language', 'en')))
    
    async def handle_callback(self, event):
        """Handle callback queries from inline buttons."""
        user_id = event.sender_id
        data = event.data.decode('utf-8')
        
        # Get user from database
        user = await self.db.get_user(user_id)
        if not user:
            username = event.sender.username or "Unknown"
            await self.db.create_user(user_id, username)
            user = await self.db.get_user(user_id)
        
        # Handle different callback types
        if data.startswith('model_'):
            # Change AI model preference
            model = data.split('_')[1]
            await self.db.update_user(user_id, {'preferred_model': model})
            await event.answer(i18n.t('model_changed', locale=user.get('language', 'en'), model=model.upper()))
            
        elif data.startswith('lang_'):
            # Change language preference
            lang = data.split('_')[1]
            await self.db.update_user(user_id, {'language': lang})
            await event.answer(i18n.t('language_changed', locale=lang))
            
        elif data == 'subscribe':
            # Handle subscription request
            await self.subscription_handler.handle_subscription(event, user)
            
        elif data.startswith('admin_'):
            # Handle admin panel actions
            if event.sender.username == self.admin_username:
                await self.admin_handler.handle_admin_callback(event, data)
            else:
                await event.answer(i18n.t('not_authorized', locale=user.get('language', 'en')))
        
        # Update the message if needed
        if not event.answered:
            await event.answer()

async def main():
    """Main function to start the bot."""
    bot = TelegramBot()
    await bot.start()

if __name__ == "__main__":
    asyncio.run(main())