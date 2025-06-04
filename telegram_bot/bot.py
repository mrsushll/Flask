#!/usr/bin/env python3
"""
ChatGpt Claude Mistral Telegram Bot
A highly advanced Telegram bot that integrates multiple AI models for chat and image generation.
Developed by: @MLBOR
"""

import asyncio
import logging
import os
import random
import re
import socket
from datetime import datetime, timedelta
from dotenv import load_dotenv
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

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
        
        # Daily tips/quotes
        self.daily_tips = [
            "You can generate images by starting your message with '/image'.",
            "Try different AI models to see which one works best for your questions.",
            "Premium subscribers get monthly token bonuses!",
            "Use '/memory reset' to clear your conversation history.",
            "You can toggle memory on/off with '/memory toggle'.",
            "Different image styles are available: realistic, anime, pixel-art, and sketch.",
            "Check your token balance with '/balance'.",
            "Subscribe to get more tokens and premium features.",
            "Use '/help' to see all available commands.",
            "You can change your language with '/language'."
        ]
        
    async def start(self):
        """Start the bot and register all event handlers."""
        await self.client.start(bot_token=self.bot_token)
        
        # Register event handlers
        self.register_handlers()
        
        logger.info("Bot started successfully!")
        
        # Start background tasks
        asyncio.create_task(self.check_monthly_bonuses())
        asyncio.create_task(self.send_daily_tips())
        
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
        
        # Memory handlers
        self.client.add_event_handler(self.handle_memory_command, events.NewMessage(pattern='/memory'))
        
        # Image handlers
        self.client.add_event_handler(self.handle_image_command, events.NewMessage(pattern='/image'))
        self.client.add_event_handler(self.handle_image_styles_command, events.NewMessage(pattern='/styles'))
        
        # Admin command handlers
        self.client.add_event_handler(self.admin_handler.admin_command, events.NewMessage(pattern='/admin'))
        self.client.add_event_handler(self.admin_handler.add_tokens_command, events.NewMessage(pattern='/add_tokens'))
        self.client.add_event_handler(self.admin_handler.user_info_command, events.NewMessage(pattern='/user_info'))
        self.client.add_event_handler(self.admin_handler.broadcast_command, events.NewMessage(pattern='/broadcast'))
        self.client.add_event_handler(self.admin_handler.stats_command, events.NewMessage(pattern='/stats'))
        
        # Subscription handlers
        self.client.add_event_handler(self.subscription_handler.subscribe_command, events.NewMessage(pattern='/subscribe'))
        
        # History handlers
        self.client.add_event_handler(self.handle_history_command, events.NewMessage(pattern='/history'))
        
        # Feedback handlers
        self.client.add_event_handler(self.handle_feedback_command, events.NewMessage(pattern='/feedback'))
        
        # AI chat handlers
        self.client.add_event_handler(self.handle_chat_message, events.NewMessage(func=lambda e: e.is_private and not e.message.text.startswith('/')))
        
        # Callback query handlers
        self.client.add_event_handler(self.handle_callback, events.CallbackQuery())
        
        # Easter egg commands
        self.client.add_event_handler(self.handle_easter_egg, events.NewMessage(pattern='/secret'))
    
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
        
        # Check if user is banned
        if user.get('is_banned', False):
            await event.respond("You have been banned from using this bot. Please contact the administrator.")
            return
        
        # Check rate limits
        if not self.rate_limiter.check_rate_limit(user_id):
            await event.respond(i18n.t('rate_limit_exceeded', locale=user.get('language', 'en')))
            return
        
        # Check if user has enough tokens
        token_costs = await self.db.get_token_costs()
        chat_cost = token_costs.get('chat', 1)
        
        if user.get('tokens', 0) < chat_cost:
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
                # Get conversation history if memory is enabled
                conversation_history = []
                if user.get('memory_enabled', True):
                    conversation_history = user.get('conversation_history', [])
                
                # Process message with the appropriate AI model
                if model == 'gpt':
                    response = await self.openai_handler.generate_response(message, conversation_history)
                elif model == 'claude':
                    response = await self.claude_handler.generate_response(message, conversation_history)
                elif model == 'mistral':
                    response = await self.mistral_handler.generate_response(message, conversation_history)
                else:
                    # Default to GPT if model preference is invalid
                    response = await self.openai_handler.generate_response(message, conversation_history)
                
                # Update conversation history if memory is enabled
                if user.get('memory_enabled', True):
                    conversation_history.append({'role': 'user', 'content': message})
                    conversation_history.append({'role': 'assistant', 'content': response})
                    
                    # Limit conversation history to last 10 exchanges (20 messages)
                    if len(conversation_history) > 20:
                        conversation_history = conversation_history[-20:]
                    
                    # Update user's conversation history in database
                    await self.db.update_user(user_id, {
                        'conversation_history': conversation_history
                    })
                
                # Deduct tokens and update last activity
                await self.db.deduct_tokens(user_id, chat_cost)
                await self.db.update_user(user_id, {
                    'last_activity': datetime.now()
                })
                
                # Log the interaction
                await self.db.log_interaction(user_id, 'chat', model, chat_cost)
                
                # Add feedback buttons
                keyboard = [
                    [
                        Button.inline("👍", f"feedback_like_{event.message.id}"),
                        Button.inline("👎", f"feedback_dislike_{event.message.id}")
                    ]
                ]
                
                # Send the response
                await event.respond(response, buttons=keyboard)
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await event.respond(i18n.t('error_processing', locale=user.get('language', 'en')))
    
    async def handle_image_command(self, event):
        """Handle image generation commands."""
        user_id = event.sender_id
        
        # Extract the prompt from the message
        prompt = event.message.text.replace('/image', '', 1).strip()
        
        if not prompt:
            await event.respond("Please provide a description for the image you want to generate.\n\nExample: `/image a beautiful sunset over mountains`")
            return
        
        # Check if user exists in database, if not create a new user
        user = await self.db.get_user(user_id)
        if not user:
            username = event.sender.username or "Unknown"
            await self.db.create_user(user_id, username)
            user = await self.db.get_user(user_id)
        
        # Check if user is banned
        if user.get('is_banned', False):
            await event.respond("You have been banned from using this bot. Please contact the administrator.")
            return
        
        # Check rate limits
        if not self.rate_limiter.check_rate_limit(user_id):
            await event.respond(i18n.t('rate_limit_exceeded', locale=user.get('language', 'en')))
            return
        
        # Check if user has enough tokens
        token_costs = await self.db.get_token_costs()
        image_cost = token_costs.get('image', 5)
        
        if user.get('tokens', 0) < image_cost:
            keyboard = [
                [Button.inline(i18n.t('subscribe_button', locale=user.get('language', 'en')), b'subscribe')]
            ]
            await event.respond(
                i18n.t('no_tokens', locale=user.get('language', 'en')),
                buttons=keyboard
            )
            return
        
        # Get user preferences
        preferences = user.get('preferences', {})
        style = preferences.get('image_style', 'realistic')
        size = preferences.get('image_size', '1024x1024')
        quality = preferences.get('image_quality', 'standard')
        
        # Check for style in the prompt
        style_match = re.search(r'--style\s+(\w+)', prompt)
        if style_match:
            requested_style = style_match.group(1).lower()
            if requested_style in self.image_generator.get_available_styles():
                style = requested_style
                # Remove the style flag from the prompt
                prompt = re.sub(r'--style\s+\w+', '', prompt).strip()
        
        # Send a message indicating that the image is being generated
        processing_message = await event.respond("🖼️ Generating your image... Please wait.")
        
        try:
            # Generate the image
            image_path = await self.image_generator.generate_image(prompt, size, style, quality)
            
            if not image_path:
                await processing_message.edit("Sorry, I couldn't generate an image. Please try again with a different prompt.")
                return
            
            # Deduct tokens and update last activity
            await self.db.deduct_tokens(user_id, image_cost)
            await self.db.update_user(user_id, {
                'last_activity': datetime.now()
            })
            
            # Log the interaction
            await self.db.log_interaction(user_id, 'image', 'dall-e', image_cost)
            
            # Log the image
            await self.db.log_image(user_id, prompt, image_path, style, image_cost)
            
            # Create buttons for image options
            keyboard = [
                [
                    Button.inline("🔍 Upscale", f"image_upscale_{os.path.basename(image_path)}"),
                    Button.inline("🎨 Variation", f"image_variation_{os.path.basename(image_path)}")
                ],
                [
                    Button.inline("💾 Save to Gallery", f"image_save_{os.path.basename(image_path)}"),
                    Button.inline("👍 Like", f"feedback_like_image_{os.path.basename(image_path)}")
                ]
            ]
            
            # Delete the processing message
            await processing_message.delete()
            
            # Send the image with caption and buttons
            await self.client.send_file(
                event.chat_id,
                image_path,
                caption=f"🖼️ **Generated Image**\n\n**Prompt:** {prompt}\n**Style:** {style}\n**Tokens used:** {image_cost}",
                buttons=keyboard
            )
            
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            await processing_message.edit("Sorry, I encountered an error while generating your image. Please try again later.")
    
    async def handle_image_styles_command(self, event):
        """Handle image styles command."""
        user_id = event.sender_id
        
        # Check if user exists in database, if not create a new user
        user = await self.db.get_user(user_id)
        if not user:
            username = event.sender.username or "Unknown"
            await self.db.create_user(user_id, username)
            user = await self.db.get_user(user_id)
        
        # Get user's language
        language = user.get('language', 'en')
        
        # Get available styles
        styles = self.image_generator.get_available_styles()
        
        # Create message with available styles
        styles_message = "🎨 **Available Image Styles**\n\n"
        styles_message += "You can use these styles when generating images by adding `--style style_name` to your prompt.\n\n"
        
        for style in styles:
            styles_message += f"• **{style}**: `/image a beautiful landscape --style {style}`\n"
        
        styles_message += "\nYou can also set a default style in your settings."
        
        # Create keyboard with style buttons
        keyboard = []
        for style in styles:
            keyboard.append([Button.inline(f"Set {style.capitalize()} as default", f"set_style_{style}")])
        
        keyboard.append([Button.inline(i18n.t('back_button', locale=language), b'back')])
        
        await event.respond(styles_message, buttons=keyboard)
    
    async def handle_memory_command(self, event):
        """Handle memory-related commands."""
        user_id = event.sender_id
        
        # Check if user exists in database, if not create a new user
        user = await self.db.get_user(user_id)
        if not user:
            username = event.sender.username or "Unknown"
            await self.db.create_user(user_id, username)
            user = await self.db.get_user(user_id)
        
        # Get user's language
        language = user.get('language', 'en')
        
        # Parse the command
        command_parts = event.message.text.split()
        if len(command_parts) < 2:
            # Show memory status and options
            memory_enabled = user.get('memory_enabled', True)
            status = "enabled" if memory_enabled else "disabled"
            
            memory_message = f"🧠 **Memory System**\n\nMemory is currently **{status}**.\n\n"
            memory_message += "With memory enabled, the bot remembers your conversation history and can refer to previous messages.\n\n"
            memory_message += "Commands:\n"
            memory_message += "• `/memory toggle` - Toggle memory on/off\n"
            memory_message += "• `/memory reset` - Clear your conversation history\n"
            memory_message += "• `/memory status` - Check memory status"
            
            await event.respond(memory_message)
            return
        
        action = command_parts[1].lower()
        
        if action == "toggle":
            # Toggle memory on/off
            new_state = await self.db.toggle_user_memory(user_id)
            status = "enabled" if new_state else "disabled"
            await event.respond(f"Memory has been {status}.")
            
        elif action == "reset":
            # Reset conversation history
            success = await self.db.reset_user_memory(user_id)
            if success:
                await event.respond("Your conversation history has been cleared.")
            else:
                await event.respond("Failed to clear your conversation history. Please try again later.")
                
        elif action == "status":
            # Show memory status
            memory_enabled = user.get('memory_enabled', True)
            status = "enabled" if memory_enabled else "disabled"
            
            # Count messages in conversation history
            conversation_history = user.get('conversation_history', [])
            message_count = len(conversation_history) // 2  # Each exchange has 2 messages (user + assistant)
            
            await event.respond(f"Memory is currently **{status}**.\n\nYou have {message_count} exchanges in your conversation history.")
    
    async def handle_history_command(self, event):
        """Handle token usage history command."""
        user_id = event.sender_id
        
        # Check if user exists in database, if not create a new user
        user = await self.db.get_user(user_id)
        if not user:
            username = event.sender.username or "Unknown"
            await self.db.create_user(user_id, username)
            user = await self.db.get_user(user_id)
        
        # Show token usage history
        await self.subscription_handler.show_usage_history(event, user)
    
    async def handle_feedback_command(self, event):
        """Handle feedback command."""
        user_id = event.sender_id
        
        # Check if user exists in database, if not create a new user
        user = await self.db.get_user(user_id)
        if not user:
            username = event.sender.username or "Unknown"
            await self.db.create_user(user_id, username)
            user = await self.db.get_user(user_id)
        
        # Get user's language
        language = user.get('language', 'en')
        
        # Create feedback message with rating buttons
        feedback_message = "⭐ **Feedback**\n\nHow would you rate your experience with this bot? Your feedback helps us improve!"
        
        # Create keyboard with rating buttons
        keyboard = [
            [
                Button.inline("⭐", "feedback_rating_1"),
                Button.inline("⭐⭐", "feedback_rating_2"),
                Button.inline("⭐⭐⭐", "feedback_rating_3"),
                Button.inline("⭐⭐⭐⭐", "feedback_rating_4"),
                Button.inline("⭐⭐⭐⭐⭐", "feedback_rating_5")
            ],
            [Button.inline(i18n.t('back_button', locale=language), b'back')]
        ]
        
        await event.respond(feedback_message, buttons=keyboard)
    
    async def handle_easter_egg(self, event):
        """Handle secret easter egg command."""
        user_id = event.sender_id
        
        # Check if user exists in database, if not create a new user
        user = await self.db.get_user(user_id)
        if not user:
            username = event.sender.username or "Unknown"
            await self.db.create_user(user_id, username)
            user = await self.db.get_user(user_id)
        
        # Add some bonus tokens as a reward for finding the easter egg
        bonus_tokens = 3
        await self.db.add_tokens(user_id, bonus_tokens)
        
        # Log the interaction
        await self.db.log_interaction(user_id, 'easter_egg', 'secret', 0)
        
        # Send a fun message
        easter_egg_message = "🎉 **You found a secret!**\n\n"
        easter_egg_message += f"As a reward, you've been granted {bonus_tokens} bonus tokens.\n\n"
        easter_egg_message += "Keep this between us... there might be more secrets to discover! 🤫"
        
        await event.respond(easter_egg_message)
    
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
                
        elif data.startswith('set_style_'):
            # Set default image style
            style = data.split('_')[-1]
            preferences = user.get('preferences', {})
            preferences['image_style'] = style
            await self.db.update_user(user_id, {'preferences': preferences})
            await event.answer(f"Default style set to {style.capitalize()}")
            
        elif data.startswith('image_upscale_'):
            # Upscale an image
            image_filename = data.split('_')[-1]
            await self.handle_image_upscale(event, user, image_filename)
            
        elif data.startswith('image_variation_'):
            # Generate a variation of an image
            image_filename = data.split('_')[-1]
            await self.handle_image_variation(event, user, image_filename)
            
        elif data.startswith('feedback_like_'):
            # Handle positive feedback
            message_id = data.split('_')[-1]
            await self.db.log_feedback(user_id, message_id, 5)
            await event.answer("Thanks for your feedback! 👍")
            
        elif data.startswith('feedback_dislike_'):
            # Handle negative feedback
            message_id = data.split('_')[-1]
            await self.db.log_feedback(user_id, message_id, 1)
            
            # Ask for more detailed feedback
            feedback_message = "Sorry to hear that. Could you tell us how we can improve?"
            
            # Create keyboard for feedback options
            keyboard = [
                [Button.inline("Response was incorrect", f"feedback_reason_incorrect_{message_id}")],
                [Button.inline("Response was incomplete", f"feedback_reason_incomplete_{message_id}")],
                [Button.inline("Response was inappropriate", f"feedback_reason_inappropriate_{message_id}")],
                [Button.inline("Other reason", f"feedback_reason_other_{message_id}")]
            ]
            
            await event.edit(feedback_message, buttons=keyboard)
            
        elif data.startswith('feedback_rating_'):
            # Handle rating feedback
            rating = int(data.split('_')[-1])
            await self.db.log_feedback(user_id, 0, rating)
            
            if rating >= 4:
                await event.edit("Thank you for your positive feedback! We're glad you're enjoying the bot.")
            else:
                # Ask for more detailed feedback
                feedback_message = "Thank you for your feedback. Could you tell us how we can improve?"
                
                # Create keyboard for feedback options
                keyboard = [
                    [Button.inline("Improve response quality", "feedback_improve_quality")],
                    [Button.inline("Add more features", "feedback_improve_features")],
                    [Button.inline("Improve user interface", "feedback_improve_ui")],
                    [Button.inline("Other suggestions", "feedback_improve_other")]
                ]
                
                await event.edit(feedback_message, buttons=keyboard)
        
        # Update the message if needed
        if not event.answered:
            await event.answer()
    
    async def handle_image_upscale(self, event, user, image_filename):
        """Handle image upscaling."""
        user_id = user['user_id']
        language = user.get('language', 'en')
        
        # Check if user has enough tokens
        token_costs = await self.db.get_token_costs()
        upscale_cost = token_costs.get('image', 5) // 2  # Half the cost of a new image
        
        if user.get('tokens', 0) < upscale_cost:
            await event.answer("Not enough tokens for upscaling.")
            return
        
        # Find the original image path
        image_path = f"/tmp/{image_filename}"
        if not os.path.exists(image_path):
            await event.answer("Image not found. It may have expired.")
            return
        
        # Send a message indicating that the image is being upscaled
        await event.answer("Upscaling your image...")
        
        try:
            # Upscale the image
            upscaled_path = await self.image_generator.upscale_image(image_path)
            
            if not upscaled_path:
                await event.respond("Sorry, I couldn't upscale the image. Please try again later.")
                return
            
            # Deduct tokens and update last activity
            await self.db.deduct_tokens(user_id, upscale_cost)
            await self.db.update_user(user_id, {
                'last_activity': datetime.now()
            })
            
            # Log the interaction
            await self.db.log_interaction(user_id, 'upscale', 'image', upscale_cost)
            
            # Send the upscaled image
            await self.client.send_file(
                event.chat_id,
                upscaled_path,
                caption=f"🔍 **Upscaled Image**\n\n**Tokens used:** {upscale_cost}"
            )
            
        except Exception as e:
            logger.error(f"Error upscaling image: {e}")
            await event.respond("Sorry, I encountered an error while upscaling your image. Please try again later.")
    
    async def handle_image_variation(self, event, user, image_filename):
        """Handle image variation generation."""
        user_id = user['user_id']
        
        # Check if user has enough tokens
        token_costs = await self.db.get_token_costs()
        variation_cost = token_costs.get('image', 5)
        
        if user.get('tokens', 0) < variation_cost:
            await event.answer("Not enough tokens for generating a variation.")
            return
        
        # Find the original image path
        image_path = f"/tmp/{image_filename}"
        if not os.path.exists(image_path):
            await event.answer("Image not found. It may have expired.")
            return
        
        # Ask for variation prompt
        await event.edit("Please describe how you want to modify the image:")
        
        # Store the request in user sessions
        self.user_sessions[user_id] = {
            'action': 'image_variation',
            'image_path': image_path,
            'timestamp': datetime.now()
        }
        
        # The actual variation will be handled when the user sends the prompt
    
    async def process_image_variation(self, event, user, prompt):
        """Process image variation request."""
        user_id = user['user_id']
        session = self.user_sessions.get(user_id)
        
        if not session or session.get('action') != 'image_variation':
            await event.respond("Your variation request has expired. Please try again.")
            return
        
        # Get the image path from the session
        image_path = session.get('image_path')
        if not os.path.exists(image_path):
            await event.respond("The original image has expired. Please generate a new image.")
            return
        
        # Get user preferences
        preferences = user.get('preferences', {})
        style = preferences.get('image_style', 'realistic')
        
        # Check for style in the prompt
        style_match = re.search(r'--style\s+(\w+)', prompt)
        if style_match:
            requested_style = style_match.group(1).lower()
            if requested_style in self.image_generator.get_available_styles():
                style = requested_style
                # Remove the style flag from the prompt
                prompt = re.sub(r'--style\s+\w+', '', prompt).strip()
        
        # Check if user has enough tokens
        token_costs = await self.db.get_token_costs()
        variation_cost = token_costs.get('image', 5)
        
        if user.get('tokens', 0) < variation_cost:
            await event.respond("You don't have enough tokens to generate a variation.")
            return
        
        # Send a message indicating that the variation is being generated
        processing_message = await event.respond("🖼️ Generating variation... Please wait.")
        
        try:
            # Generate the variation
            variation_path = await self.image_generator.generate_variation(prompt, image_path, style)
            
            if not variation_path:
                await processing_message.edit("Sorry, I couldn't generate a variation. Please try again with a different prompt.")
                return
            
            # Deduct tokens and update last activity
            await self.db.deduct_tokens(user_id, variation_cost)
            await self.db.update_user(user_id, {
                'last_activity': datetime.now()
            })
            
            # Log the interaction
            await self.db.log_interaction(user_id, 'variation', 'dall-e', variation_cost)
            
            # Log the image
            await self.db.log_image(user_id, prompt, variation_path, style, variation_cost)
            
            # Delete the processing message
            await processing_message.delete()
            
            # Send the variation
            await self.client.send_file(
                event.chat_id,
                variation_path,
                caption=f"🎨 **Image Variation**\n\n**Prompt:** {prompt}\n**Style:** {style}\n**Tokens used:** {variation_cost}"
            )
            
            # Clear the session
            del self.user_sessions[user_id]
            
        except Exception as e:
            logger.error(f"Error generating image variation: {e}")
            await processing_message.edit("Sorry, I encountered an error while generating your variation. Please try again later.")
    
    async def check_monthly_bonuses(self):
        """Check and distribute monthly bonuses to subscribers."""
        while True:
            try:
                await self.subscription_handler.check_monthly_bonuses()
                # Check once a day
                await asyncio.sleep(86400)  # 24 hours
            except Exception as e:
                logger.error(f"Error in check_monthly_bonuses: {e}")
                await asyncio.sleep(3600)  # Retry after 1 hour on error
    
    async def send_daily_tips(self):
        """Send daily tips to active users."""
        while True:
            try:
                # Get active users (active in the last 7 days)
                active_users = await self.db.get_all_users()
                active_users = [user for user in active_users if user.get('last_activity') and 
                               (datetime.now() - user.get('last_activity')).days < 7]
                
                if active_users:
                    # Select a random tip
                    tip = random.choice(self.daily_tips)
                    
                    # Send the tip to active users
                    for user in active_users:
                        try:
                            # Get user's language
                            language = user.get('language', 'en')
                            
                            # Create tip message
                            tip_message = f"💡 **Daily Tip**\n\n{tip}"
                            
                            # Send the tip
                            await self.client.send_message(user['user_id'], tip_message)
                            
                            # Add a small delay between messages to avoid rate limits
                            await asyncio.sleep(0.5)
                        except Exception as e:
                            logger.error(f"Error sending daily tip to user {user['user_id']}: {e}")
                
                # Send tips once a day at a random time
                await asyncio.sleep(86400 + random.randint(-3600, 3600))  # 24 hours ± 1 hour
            except Exception as e:
                logger.error(f"Error in send_daily_tips: {e}")
                await asyncio.sleep(3600)  # Retry after 1 hour on error

# Health check server for Render
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        # Suppress HTTP server logs
        return

def start_health_server(port=8080):
    """Start a simple HTTP server for health checks."""
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server_thread = Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    logger.info(f"Health check server started on port {port}")

async def main():
    """Main function to start the bot."""
    # Start health check server for Render
    port = int(os.environ.get('PORT', 8080))
    start_health_server(port)
    
    # Start the bot
    bot = TelegramBot()
    await bot.start()

if __name__ == "__main__":
    asyncio.run(main())