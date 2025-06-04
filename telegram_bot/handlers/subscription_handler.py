"""
Subscription handler for the Telegram bot.
Handles all subscription-related functionality including Telegram Stars integration.
"""

import logging
import i18n
from datetime import datetime, timedelta
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
        
        # Define subscription tiers
        self.subscription_tiers = {
            "basic": {
                "name": "Basic",
                "price": 5,
                "tokens": 50,
                "monthly_bonus": 10,
                "benefits": ["Access to all AI models", "Basic image generation"]
            },
            "standard": {
                "name": "Standard",
                "price": 10,
                "tokens": 150,
                "monthly_bonus": 30,
                "benefits": ["Access to all AI models", "HD image generation", "Priority support"]
            },
            "premium": {
                "name": "Premium",
                "price": 25,
                "tokens": 500,
                "monthly_bonus": 100,
                "benefits": ["Access to all AI models", "HD image generation", "Priority support", "Exclusive features"]
            }
        }
    
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
        # Get callback data
        data = event.data.decode('utf-8')
        user_id = user['user_id']
        language = user.get('language', 'en')
        
        if data.startswith('subscribe_'):
            # Parse subscription data
            parts = data.split('_')
            if len(parts) >= 3:
                tokens = int(parts[1])
                price = int(parts[2])
                
                # Process payment
                await event.answer("Processing payment...")
                
                # Simulate payment processing
                success = await self.process_telegram_stars_payment(user_id, tokens, price)
                
                if success:
                    # Determine subscription tier
                    tier = "basic"
                    for tier_id, tier_data in self.subscription_tiers.items():
                        if tier_data["tokens"] == tokens:
                            tier = tier_id
                            break
                    
                    # Update user's subscription status
                    await self.bot.db.update_user(user_id, {
                        'is_premium': True,
                        'subscription_tier': tier,
                        'subscription_date': datetime.now(),
                        'subscription_expires': datetime.now() + timedelta(days=30)
                    })
                    
                    # Send confirmation message
                    confirmation_message = f"✅ **Payment Successful!**\n\n"
                    confirmation_message += f"You have purchased {tokens} tokens for ${price}.\n"
                    confirmation_message += f"Your new balance: {user.get('tokens', 0) + tokens} tokens\n\n"
                    confirmation_message += f"Subscription tier: {self.subscription_tiers[tier]['name']}\n"
                    confirmation_message += f"Expires: {(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')}\n\n"
                    confirmation_message += "Thank you for your support!"
                    
                    await event.edit(confirmation_message)
                else:
                    # Send error message
                    error_message = "❌ **Payment Failed**\n\n"
                    error_message += "Sorry, we couldn't process your payment. Please try again later."
                    
                    await event.edit(error_message)
            else:
                await self._show_subscription_options(event, language)
        else:
            await self._show_subscription_options(event, language)
    
    async def _show_subscription_options(self, event, language):
        """Show subscription options.
        
        Args:
            event: Telegram event
            language: User's language
        """
        # Create subscription message with inline keyboard
        subscription_message = i18n.t('subscription_options', locale=language)
        
        # Create inline keyboard with subscription options
        keyboard = []
        
        for tier_id, tier in self.subscription_tiers.items():
            # Create button text with tier details
            button_text = f"{tier['name']} - {tier['tokens']} {i18n.t('tokens', locale=language)} (${tier['price']})"
            button_data = f"subscribe_{tier['tokens']}_{tier['price']}"
            keyboard.append([Button.inline(button_text, button_data.encode())])
            
            # Add tier details to message
            subscription_message += f"\n\n**{tier['name']} Plan (${tier['price']})**\n"
            subscription_message += f"• {tier['tokens']} tokens\n"
            subscription_message += f"• {tier['monthly_bonus']} monthly bonus tokens\n"
            
            # Add benefits
            for benefit in tier['benefits']:
                subscription_message += f"• {benefit}\n"
        
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
    
    async def check_monthly_bonuses(self):
        """Check and distribute monthly bonuses to subscribers.
        
        This should be called periodically, e.g., daily, to check for users
        who should receive their monthly bonus tokens.
        """
        try:
            # Get all premium users
            premium_users = await self.bot.db.get_premium_users()
            
            for user in premium_users:
                # Check if it's time for monthly bonus
                subscription_date = user.get('subscription_date')
                last_bonus_date = user.get('last_bonus_date')
                
                if not subscription_date:
                    continue
                
                # Convert to datetime if needed
                if isinstance(subscription_date, str):
                    subscription_date = datetime.fromisoformat(subscription_date)
                
                # Calculate next bonus date
                if last_bonus_date:
                    if isinstance(last_bonus_date, str):
                        last_bonus_date = datetime.fromisoformat(last_bonus_date)
                    next_bonus_date = last_bonus_date + timedelta(days=30)
                else:
                    next_bonus_date = subscription_date + timedelta(days=30)
                
                # Check if it's time for bonus
                if datetime.now() >= next_bonus_date:
                    # Get user's subscription tier
                    tier = user.get('subscription_tier', 'basic')
                    
                    # Get bonus amount
                    bonus_amount = self.subscription_tiers[tier]['monthly_bonus']
                    
                    # Add bonus tokens
                    success = await self.bot.db.add_tokens(user['user_id'], bonus_amount)
                    
                    if success:
                        # Update last bonus date
                        await self.bot.db.update_user(user['user_id'], {
                            'last_bonus_date': datetime.now()
                        })
                        
                        # Log the bonus
                        await self.bot.db.log_interaction(user['user_id'], 'bonus', 'monthly', bonus_amount)
                        
                        # Notify user
                        try:
                            await self.bot.client.send_message(
                                user['user_id'],
                                f"🎁 **Monthly Bonus!**\n\n"
                                f"You've received {bonus_amount} bonus tokens as part of your "
                                f"{self.subscription_tiers[tier]['name']} subscription.\n\n"
                                f"Thank you for your continued support!"
                            )
                        except Exception as e:
                            logger.error(f"Failed to notify user {user['user_id']} about monthly bonus: {e}")
                        
                        logger.info(f"Added {bonus_amount} monthly bonus tokens to user {user['user_id']}")
        
        except Exception as e:
            logger.error(f"Error checking monthly bonuses: {e}")
    
    async def show_usage_history(self, event, user):
        """Show token usage history for a user.
        
        Args:
            event: Telegram event
            user: User document
        """
        user_id = user['user_id']
        language = user.get('language', 'en')
        
        # Get user's token usage history
        history = await self.bot.db.get_token_history(user_id)
        
        if not history or len(history) == 0:
            await event.respond(i18n.t('no_history', locale=language))
            return
        
        # Create history message
        history_message = f"📊 **Token Usage History**\n\n"
        
        # Group by date
        date_groups = {}
        for entry in history:
            date = entry.get('timestamp').strftime('%Y-%m-%d')
            if date not in date_groups:
                date_groups[date] = []
            date_groups[date].append(entry)
        
        # Add history entries
        for date, entries in sorted(date_groups.items(), reverse=True):
            history_message += f"**{date}**\n"
            
            # Calculate daily total
            daily_total = sum(entry.get('tokens_used', 0) for entry in entries)
            
            # Add entries
            for entry in entries:
                entry_type = entry.get('type', 'unknown')
                model = entry.get('model', 'unknown')
                tokens = entry.get('tokens_used', 0)
                time = entry.get('timestamp').strftime('%H:%M')
                
                if entry_type == 'purchase':
                    history_message += f"💰 {time} - Purchased {tokens} tokens\n"
                elif entry_type == 'bonus':
                    history_message += f"🎁 {time} - Received {tokens} bonus tokens\n"
                elif entry_type == 'chat':
                    history_message += f"💬 {time} - Used {tokens} tokens with {model.upper()}\n"
                elif entry_type == 'image':
                    history_message += f"🖼️ {time} - Used {tokens} tokens for image generation\n"
                else:
                    history_message += f"⚙️ {time} - Used {tokens} tokens for {entry_type}\n"
            
            history_message += f"Total for {date}: {daily_total} tokens\n\n"
        
        # Add current balance
        history_message += f"\nCurrent balance: {user.get('tokens', 0)} tokens"
        
        # Create inline keyboard
        keyboard = [
            [Button.inline(i18n.t('back_button', locale=language), b'back')]
        ]
        
        await event.respond(history_message, buttons=keyboard)