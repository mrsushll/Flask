"""
Subscription handler for the Telegram bot.
Handles all subscription-related functionality.
"""

import logging
import i18n
from telethon.tl.custom import Button

logger = logging.getLogger('bot.handlers.subscription')

class SubscriptionHandler:
    """Handler for subscription-related functionality."""
    
    def __init__(self, bot):
        """Initialize the subscription handler.
        
        Args:
            bot: Main bot instance
        """
        self.bot = bot
    
    async def subscribe_command(self, event):
        """Handle /subscribe command.
        
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
        
        # Show subscription options
        await self._show_subscription_options(event, language)
    
    async def handle_subscription(self, event, user):
        """Handle subscription callback.
        
        Args:
            event: Telegram event
            user: User document
        """
        # Get user's language
        language = user.get('language', 'en')
        
        # Show subscription options
        await self._show_subscription_options(event, language)
    
    async def _show_subscription_options(self, event, language):
        """Show subscription options.
        
        Args:
            event: Telegram event
            language: User's language
        """
        # Create subscription message with inline keyboard
        subscription_message = i18n.t('subscription_options', locale=language)
        
        # Create subscription packages
        packages = [
            {"name": "Basic", "tokens": 50, "price": 5},
            {"name": "Standard", "tokens": 150, "price": 10},
            {"name": "Premium", "tokens": 500, "price": 25}
        ]
        
        # Create inline keyboard with subscription options
        keyboard = []
        for package in packages:
            button_text = f"{package['name']} - {package['tokens']} {i18n.t('tokens', locale=language)} (${package['price']})"
            button_data = f"subscribe_{package['tokens']}_{package['price']}"
            keyboard.append([Button.inline(button_text, button_data.encode())])
        
        # Add back button
        keyboard.append([Button.inline(i18n.t('back_button', locale=language), b'back')])
        
        # Check if this is a new message or an edit
        if hasattr(event, 'edit') and callable(event.edit):
            await event.edit(subscription_message, buttons=keyboard)
        else:
            await event.respond(subscription_message, buttons=keyboard)
    
    async def process_telegram_stars_payment(self, user_id, tokens, price):
        """Process a Telegram Stars payment.
        
        Args:
            user_id: User ID
            tokens: Number of tokens
            price: Price in USD
            
        Returns:
            bool: True if payment was successful, False otherwise
        """
        # In a real implementation, this would integrate with Telegram's payment API
        # For now, we'll simulate a successful payment
        
        # Add tokens to user's account
        success = await self.bot.db.add_tokens(user_id, tokens)
        
        if success:
            logger.info(f"Added {tokens} tokens to user {user_id} for ${price}")
            
            # Log the transaction
            await self.bot.db.log_interaction(user_id, 'purchase', 'telegram_stars', tokens)
            
            return True
        else:
            logger.error(f"Failed to add tokens to user {user_id}")
            return False