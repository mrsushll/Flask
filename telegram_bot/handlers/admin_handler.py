"""
Admin handler for the Telegram bot.
Handles all admin commands and functionality.
"""

import logging
import i18n
from telethon.tl.custom import Button

logger = logging.getLogger('bot.handlers.admin')

class AdminHandler:
    """Handler for admin commands and functionality."""
    
    def __init__(self, bot):
        """Initialize the admin handler.
        
        Args:
            bot: Main bot instance
        """
        self.bot = bot
    
    async def admin_command(self, event):
        """Handle /admin command.
        
        Args:
            event: Telegram event
        """
        # Check if user is admin
        if event.sender.username != self.bot.admin_username:
            await event.respond("You are not authorized to use admin commands.")
            return
        
        # Create admin panel message with inline keyboard
        admin_message = "🔐 **Admin Panel**\n\nWelcome to the admin panel. What would you like to do?"
        
        keyboard = [
            [Button.inline("User Management", b'admin_users')],
            [Button.inline("Token Management", b'admin_tokens')],
            [Button.inline("Statistics", b'admin_stats')],
            [Button.inline("Settings", b'admin_settings')],
            [Button.inline("Broadcast Message", b'admin_broadcast')]
        ]
        
        await event.respond(admin_message, buttons=keyboard)
    
    async def add_tokens_command(self, event):
        """Handle /add_tokens command.
        
        Args:
            event: Telegram event
        """
        # Check if user is admin
        if event.sender.username != self.bot.admin_username:
            await event.respond("You are not authorized to use admin commands.")
            return
        
        # Parse command arguments
        args = event.message.text.split()
        if len(args) != 3:
            await event.respond("Usage: /add_tokens <user_id> <amount>")
            return
        
        try:
            user_id = int(args[1])
            amount = int(args[2])
        except ValueError:
            await event.respond("Invalid arguments. Usage: /add_tokens <user_id> <amount>")
            return
        
        # Check if user exists
        user = await self.bot.db.get_user(user_id)
        if not user:
            await event.respond(f"User with ID {user_id} not found.")
            return
        
        # Add tokens to user
        success = await self.bot.db.add_tokens(user_id, amount)
        if success:
            await event.respond(f"Successfully added {amount} tokens to user {user_id}.")
        else:
            await event.respond(f"Failed to add tokens to user {user_id}.")
    
    async def user_info_command(self, event):
        """Handle /user_info command.
        
        Args:
            event: Telegram event
        """
        # Check if user is admin
        if event.sender.username != self.bot.admin_username:
            await event.respond("You are not authorized to use admin commands.")
            return
        
        # Parse command arguments
        args = event.message.text.split()
        if len(args) != 2:
            await event.respond("Usage: /user_info <user_id>")
            return
        
        try:
            user_id = int(args[1])
        except ValueError:
            await event.respond("Invalid user ID. Usage: /user_info <user_id>")
            return
        
        # Get user from database
        user = await self.bot.db.get_user(user_id)
        if not user:
            await event.respond(f"User with ID {user_id} not found.")
            return
        
        # Get user stats
        stats = await self.bot.db.get_user_stats(user_id)
        
        # Create user info message
        info_message = f"📊 **User Information**\n\n"
        info_message += f"User ID: {user['user_id']}\n"
        info_message += f"Username: @{user.get('username', 'Unknown')}\n"
        info_message += f"Language: {user.get('language', 'en')}\n"
        info_message += f"Tokens: {user.get('tokens', 0)}\n"
        info_message += f"Preferred Model: {user.get('preferred_model', 'gpt').upper()}\n"
        info_message += f"Created At: {user.get('created_at', 'Unknown')}\n"
        info_message += f"Last Activity: {user.get('last_activity', 'Unknown')}\n"
        info_message += f"Premium: {'Yes' if user.get('is_premium', False) else 'No'}\n"
        info_message += f"Banned: {'Yes' if user.get('is_banned', False) else 'No'}\n\n"
        
        if stats:
            info_message += f"Total Interactions: {stats.get('total_interactions', 0)}\n"
            info_message += f"Total Tokens Used: {stats.get('total_tokens_used', 0)}\n\n"
            
            info_message += "**Model Usage:**\n"
            for model, count in stats.get('model_usage', {}).items():
                info_message += f"- {model.upper()}: {count}\n"
            
            info_message += "\n**Interaction Types:**\n"
            for type_name, count in stats.get('type_usage', {}).items():
                info_message += f"- {type_name.capitalize()}: {count}\n"
        
        # Create inline keyboard for user management
        keyboard = [
            [Button.inline("Add Tokens", f"admin_add_tokens_{user_id}")],
            [Button.inline("Ban User" if not user.get('is_banned', False) else "Unban User", f"admin_toggle_ban_{user_id}")],
            [Button.inline("Back to Admin Panel", b"admin_back")]
        ]
        
        await event.respond(info_message, buttons=keyboard)
    
    async def broadcast_command(self, event):
        """Handle /broadcast command.
        
        Args:
            event: Telegram event
        """
        # Check if user is admin
        if event.sender.username != self.bot.admin_username:
            await event.respond("You are not authorized to use admin commands.")
            return
        
        # Parse command arguments
        message_text = event.message.text.replace('/broadcast ', '', 1)
        if message_text == '/broadcast':
            await event.respond("Usage: /broadcast <message>")
            return
        
        # Get all users
        users = await self.bot.db.get_all_users()
        
        # Send broadcast message to all users
        sent_count = 0
        for user in users:
            try:
                await self.bot.client.send_message(user['user_id'], f"📢 **Broadcast Message**\n\n{message_text}")
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send broadcast message to user {user['user_id']}: {e}")
        
        await event.respond(f"Broadcast message sent to {sent_count} out of {len(users)} users.")
    
    async def stats_command(self, event):
        """Handle /stats command.
        
        Args:
            event: Telegram event
        """
        # Check if user is admin
        if event.sender.username != self.bot.admin_username:
            await event.respond("You are not authorized to use admin commands.")
            return
        
        # Get global stats
        stats = await self.bot.db.get_global_stats()
        if not stats:
            await event.respond("Failed to retrieve global statistics.")
            return
        
        # Create stats message
        stats_message = f"📊 **Global Statistics**\n\n"
        stats_message += f"Total Users: {stats.get('total_users', 0)}\n"
        stats_message += f"Active Users (24h): {stats.get('active_users', 0)}\n"
        stats_message += f"Total Interactions: {stats.get('total_interactions', 0)}\n"
        stats_message += f"Total Tokens Used: {stats.get('total_tokens_used', 0)}\n\n"
        
        stats_message += "**Model Usage:**\n"
        for model, count in stats.get('model_usage', {}).items():
            stats_message += f"- {model.upper()}: {count}\n"
        
        stats_message += "\n**Interaction Types:**\n"
        for type_name, count in stats.get('type_usage', {}).items():
            stats_message += f"- {type_name.capitalize()}: {count}\n"
        
        await event.respond(stats_message)
    
    async def handle_admin_callback(self, event, data):
        """Handle admin panel callback queries.
        
        Args:
            event: Telegram event
            data: Callback data
        """
        if data == 'admin_users':
            # Show user management panel
            await self._show_user_management(event)
        
        elif data == 'admin_tokens':
            # Show token management panel
            await self._show_token_management(event)
        
        elif data == 'admin_stats':
            # Show statistics panel
            await self._show_statistics(event)
        
        elif data == 'admin_settings':
            # Show settings panel
            await self._show_admin_settings(event)
        
        elif data == 'admin_broadcast':
            # Show broadcast panel
            await self._show_broadcast_panel(event)
        
        elif data == 'admin_back':
            # Go back to admin panel
            await self.admin_command(event)
        
        elif data.startswith('admin_add_tokens_'):
            # Add tokens to user
            user_id = int(data.split('_')[-1])
            await self._show_add_tokens_panel(event, user_id)
        
        elif data.startswith('admin_toggle_ban_'):
            # Toggle user ban status
            user_id = int(data.split('_')[-1])
            await self._toggle_user_ban(event, user_id)
    
    async def _show_user_management(self, event):
        """Show user management panel.
        
        Args:
            event: Telegram event
        """
        # Get all users (limited to 10 for display)
        users = await self.bot.db.get_all_users(limit=10)
        
        # Create user management message
        message = "👥 **User Management**\n\n"
        message += "Recent users:\n\n"
        
        for user in users:
            message += f"ID: {user['user_id']} | @{user.get('username', 'Unknown')} | Tokens: {user.get('tokens', 0)}\n"
        
        message += "\nUse /user_info <user_id> to view detailed user information."
        
        # Create inline keyboard
        keyboard = [
            [Button.inline("Back to Admin Panel", b"admin_back")]
        ]
        
        await event.edit(message, buttons=keyboard)
    
    async def _show_token_management(self, event):
        """Show token management panel.
        
        Args:
            event: Telegram event
        """
        # Create token management message
        message = "🪙 **Token Management**\n\n"
        message += "Use /add_tokens <user_id> <amount> to add tokens to a user.\n\n"
        message += "Example: /add_tokens 123456789 10"
        
        # Create inline keyboard
        keyboard = [
            [Button.inline("Back to Admin Panel", b"admin_back")]
        ]
        
        await event.edit(message, buttons=keyboard)
    
    async def _show_statistics(self, event):
        """Show statistics panel.
        
        Args:
            event: Telegram event
        """
        # Get global stats
        stats = await self.bot.db.get_global_stats()
        if not stats:
            await event.edit("Failed to retrieve global statistics.")
            return
        
        # Create stats message
        stats_message = f"📊 **Global Statistics**\n\n"
        stats_message += f"Total Users: {stats.get('total_users', 0)}\n"
        stats_message += f"Active Users (24h): {stats.get('active_users', 0)}\n"
        stats_message += f"Total Interactions: {stats.get('total_interactions', 0)}\n"
        stats_message += f"Total Tokens Used: {stats.get('total_tokens_used', 0)}\n\n"
        
        stats_message += "**Model Usage:**\n"
        for model, count in stats.get('model_usage', {}).items():
            stats_message += f"- {model.upper()}: {count}\n"
        
        stats_message += "\n**Interaction Types:**\n"
        for type_name, count in stats.get('type_usage', {}).items():
            stats_message += f"- {type_name.capitalize()}: {count}\n"
        
        # Create inline keyboard
        keyboard = [
            [Button.inline("Back to Admin Panel", b"admin_back")]
        ]
        
        await event.edit(stats_message, buttons=keyboard)
    
    async def _show_admin_settings(self, event):
        """Show admin settings panel.
        
        Args:
            event: Telegram event
        """
        # Create settings message
        message = "⚙️ **Admin Settings**\n\n"
        message += "Here you can configure global bot settings."
        
        # Create inline keyboard
        keyboard = [
            [Button.inline("Default Token Cost", b"admin_setting_token_cost")],
            [Button.inline("Rate Limit Settings", b"admin_setting_rate_limit")],
            [Button.inline("Back to Admin Panel", b"admin_back")]
        ]
        
        await event.edit(message, buttons=keyboard)
    
    async def _show_broadcast_panel(self, event):
        """Show broadcast panel.
        
        Args:
            event: Telegram event
        """
        # Create broadcast message
        message = "📢 **Broadcast Message**\n\n"
        message += "Use /broadcast <message> to send a message to all users.\n\n"
        message += "Example: /broadcast Hello everyone! We have updated our bot with new features."
        
        # Create inline keyboard
        keyboard = [
            [Button.inline("Back to Admin Panel", b"admin_back")]
        ]
        
        await event.edit(message, buttons=keyboard)
    
    async def _show_add_tokens_panel(self, event, user_id):
        """Show add tokens panel for a specific user.
        
        Args:
            event: Telegram event
            user_id: User ID
        """
        # Get user from database
        user = await self.bot.db.get_user(user_id)
        if not user:
            await event.edit(f"User with ID {user_id} not found.")
            return
        
        # Create add tokens message
        message = f"🪙 **Add Tokens to User**\n\n"
        message += f"User ID: {user_id}\n"
        message += f"Username: @{user.get('username', 'Unknown')}\n"
        message += f"Current Tokens: {user.get('tokens', 0)}\n\n"
        message += "Use /add_tokens <user_id> <amount> to add tokens to this user.\n\n"
        message += f"Example: /add_tokens {user_id} 10"
        
        # Create inline keyboard
        keyboard = [
            [Button.inline("Back to User Info", f"admin_user_info_{user_id}")],
            [Button.inline("Back to Admin Panel", b"admin_back")]
        ]
        
        await event.edit(message, buttons=keyboard)
    
    async def _toggle_user_ban(self, event, user_id):
        """Toggle ban status for a specific user.
        
        Args:
            event: Telegram event
            user_id: User ID
        """
        # Get user from database
        user = await self.bot.db.get_user(user_id)
        if not user:
            await event.edit(f"User with ID {user_id} not found.")
            return
        
        # Toggle ban status
        is_banned = user.get('is_banned', False)
        if is_banned:
            success = await self.bot.db.unban_user(user_id)
            action = "unbanned"
        else:
            success = await self.bot.db.ban_user(user_id)
            action = "banned"
        
        if success:
            await event.answer(f"User {user_id} has been {action}.")
            # Refresh user info
            await self.user_info_command(event)
        else:
            await event.answer(f"Failed to {action} user {user_id}.")