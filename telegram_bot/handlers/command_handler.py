"""
Command handler for the Telegram bot.
Handles all regular user commands.
"""

import logging
import i18n
from telethon.tl.custom import Button

logger = logging.getLogger('bot.handlers.command')

class CommandHandler:
    """Handler for regular user commands."""
    
    def __init__(self, bot):
        """Initialize the command handler.
        
        Args:
            bot: Main bot instance
        """
        self.bot = bot
    
    async def start_command(self, event):
        """Handle /start command.
        
        Args:
            event: Telegram event
        """
        user_id = event.sender_id
        
        # Check if user exists in database, if not create a new user
        user = await self.bot.db.get_user(user_id)
        if not user:
            username = event.sender.username or "Unknown"
            await self.bot.db.create_user(user_id, username)
            user = await self.bot.db.get_user(user_id)
        
        # Get user's language
        language = user.get('language', 'en')
        
        # Create welcome message with inline keyboard
        welcome_message = i18n.t('welcome_message', locale=language)
        
        keyboard = [
            [Button.inline(i18n.t('models_button', locale=language), b'models')],
            [Button.inline(i18n.t('settings_button', locale=language), b'settings')],
            [Button.inline(i18n.t('balance_button', locale=language), b'balance')]
        ]
        
        await event.respond(welcome_message, buttons=keyboard)
    
    async def help_command(self, event):
        """Handle /help command.
        
        Args:
            event: Telegram event
        """
        user_id = event.sender_id
        
        # Get user from database
        user = await self.bot.db.get_user(user_id)
        if not user:
            username = event.sender.username or "Unknown"
            await self.bot.db.create_user(user_id, username)
            user = await self.bot.db.get_user(user_id)
        
        # Get user's language
        language = user.get('language', 'en')
        
        # Create help message
        help_message = i18n.t('help_message', locale=language)
        
        await event.respond(help_message)
    
    async def settings_command(self, event):
        """Handle /settings command.
        
        Args:
            event: Telegram event
        """
        user_id = event.sender_id
        
        # Get user from database
        user = await self.bot.db.get_user(user_id)
        if not user:
            username = event.sender.username or "Unknown"
            await self.bot.db.create_user(user_id, username)
            user = await self.bot.db.get_user(user_id)
        
        # Get user's language
        language = user.get('language', 'en')
        
        # Create settings message with inline keyboard
        settings_message = i18n.t('settings_message', locale=language)
        
        # Add current settings to the message
        memory_status = "Enabled" if user.get('memory_enabled', True) else "Disabled"
        model = user.get('preferred_model', 'gpt').upper()
        preferences = user.get('preferences', {})
        image_style = preferences.get('image_style', 'realistic').capitalize()
        
        settings_message += f"\n\n**Current Settings:**\n"
        settings_message += f"• Language: {language.upper()}\n"
        settings_message += f"• AI Model: {model}\n"
        settings_message += f"• Memory: {memory_status}\n"
        settings_message += f"• Default Image Style: {image_style}\n"
        
        keyboard = [
            [Button.inline(i18n.t('language_button', locale=language), b'language')],
            [Button.inline(i18n.t('model_button', locale=language), b'model')],
            [Button.inline(i18n.t('memory_button', locale=language), b'memory')],
            [Button.inline(i18n.t('styles_button', locale=language), b'styles')],
            [Button.inline(i18n.t('back_button', locale=language), b'back')]
        ]
        
        await event.respond(settings_message, buttons=keyboard)
    
    async def balance_command(self, event):
        """Handle /balance command.
        
        Args:
            event: Telegram event
        """
        user_id = event.sender_id
        
        # Get user from database
        user = await self.bot.db.get_user(user_id)
        if not user:
            username = event.sender.username or "Unknown"
            await self.bot.db.create_user(user_id, username)
            user = await self.bot.db.get_user(user_id)
        
        # Get user's language
        language = user.get('language', 'en')
        
        # Get user's token balance
        tokens = user.get('tokens', 0)
        
        # Create balance message with inline keyboard
        balance_message = i18n.t('balance_message', locale=language, tokens=tokens)
        
        keyboard = [
            [Button.inline(i18n.t('subscribe_button', locale=language), b'subscribe')],
            [Button.inline(i18n.t('back_button', locale=language), b'back')]
        ]
        
        await event.respond(balance_message, buttons=keyboard)
    
    async def models_command(self, event):
        """Handle /models command.
        
        Args:
            event: Telegram event
        """
        user_id = event.sender_id
        
        # Get user from database
        user = await self.bot.db.get_user(user_id)
        if not user:
            username = event.sender.username or "Unknown"
            await self.bot.db.create_user(user_id, username)
            user = await self.bot.db.get_user(user_id)
        
        # Get user's language
        language = user.get('language', 'en')
        
        # Get user's preferred model
        preferred_model = user.get('preferred_model', 'gpt')
        
        # Create models message with inline keyboard
        models_message = i18n.t('models_message', locale=language, model=preferred_model.upper())
        
        keyboard = [
            [Button.inline("GPT (OpenAI)", b'model_gpt')],
            [Button.inline("Claude (Anthropic)", b'model_claude')],
            [Button.inline("Mistral", b'model_mistral')],
            [Button.inline(i18n.t('back_button', locale=language), b'back')]
        ]
        
        await event.respond(models_message, buttons=keyboard)
    
    async def language_command(self, event):
        """Handle /language command.
        
        Args:
            event: Telegram event
        """
        user_id = event.sender_id
        
        # Get user from database
        user = await self.bot.db.get_user(user_id)
        if not user:
            username = event.sender.username or "Unknown"
            await self.bot.db.create_user(user_id, username)
            user = await self.bot.db.get_user(user_id)
        
        # Get user's language
        language = user.get('language', 'en')
        
        # Create language message with inline keyboard
        language_message = i18n.t('language_message', locale=language)
        
        keyboard = [
            [Button.inline("English 🇬🇧", b'lang_en')],
            [Button.inline("العربية 🇸🇦", b'lang_ar')],
            [Button.inline(i18n.t('back_button', locale=language), b'back')]
        ]
        
        await event.respond(language_message, buttons=keyboard)