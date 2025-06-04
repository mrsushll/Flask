"""
MongoDB database handler for the Telegram bot.
Handles all database operations including user management, token tracking, and logging.
"""

import logging
from datetime import datetime, timedelta
from pymongo import MongoClient, DESCENDING
from pymongo.errors import ConnectionFailure, OperationFailure

logger = logging.getLogger('bot.database')

class MongoDB:
    """MongoDB database handler for the Telegram bot."""
    
    def __init__(self, connection_string):
        """Initialize MongoDB connection.
        
        Args:
            connection_string (str): MongoDB connection string
        """
        self.client = MongoClient(connection_string)
        self.db = self.client['telegram_bot']
        
        # Collections
        self.users = self.db['users']
        self.interactions = self.db['interactions']
        self.settings = self.db['settings']
        self.images = self.db['images']
        self.feedback = self.db['feedback']
        
        # Create indexes
        self._create_indexes()
        
        # Test connection
        try:
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
        except ConnectionFailure:
            logger.error("Failed to connect to MongoDB")
    
    def _create_indexes(self):
        """Create necessary indexes for the collections."""
        try:
            # Create unique index on user_id for users collection
            self.users.create_index('user_id', unique=True)
            
            # Create index on timestamp for interactions collection
            self.interactions.create_index('timestamp')
            
            # Create index on user_id for interactions collection
            self.interactions.create_index('user_id')
            
            # Create index on user_id for images collection
            self.images.create_index('user_id')
            
            # Create index on timestamp for images collection
            self.images.create_index('timestamp')
            
            # Create index on user_id for feedback collection
            self.feedback.create_index('user_id')
            
            logger.info("Database indexes created successfully")
        except OperationFailure as e:
            logger.error(f"Failed to create indexes: {e}")
    
    async def create_user(self, user_id, username, language='en'):
        """Create a new user in the database.
        
        Args:
            user_id (int): Telegram user ID
            username (str): Telegram username
            language (str, optional): User's preferred language. Defaults to 'en'.
            
        Returns:
            bool: True if user was created, False otherwise
        """
        try:
            # Check if user already exists
            existing_user = await self.get_user(user_id)
            if existing_user:
                return False
            
            # Create new user document
            user_doc = {
                'user_id': user_id,
                'username': username,
                'language': language,
                'tokens': 5,  # Start with 5 free tokens
                'preferred_model': 'gpt',  # Default model
                'conversation_history': [],
                'created_at': datetime.now(),
                'last_activity': datetime.now(),
                'is_premium': False,
                'is_banned': False,
                'memory_enabled': True,  # Enable memory by default
                'subscription_tier': None,
                'subscription_date': None,
                'subscription_expires': None,
                'last_bonus_date': None,
                'preferences': {
                    'image_style': 'realistic',
                    'image_size': '1024x1024',
                    'image_quality': 'standard',
                    'token_cost': {
                        'chat': 1,
                        'image': 5
                    }
                }
            }
            
            self.users.insert_one(user_doc)
            logger.info(f"Created new user: {user_id} ({username})")
            return True
            
        except Exception as e:
            logger.error(f"Error creating user {user_id}: {e}")
            return False
    
    async def get_user(self, user_id):
        """Get user data from the database.
        
        Args:
            user_id (int): Telegram user ID
            
        Returns:
            dict: User document or None if not found
        """
        try:
            return self.users.find_one({'user_id': user_id})
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    async def update_user(self, user_id, update_data):
        """Update user data in the database.
        
        Args:
            user_id (int): Telegram user ID
            update_data (dict): Data to update
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            result = self.users.update_one(
                {'user_id': user_id},
                {'$set': update_data}
            )
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return False
    
    async def add_tokens(self, user_id, amount):
        """Add tokens to a user's account.
        
        Args:
            user_id (int): Telegram user ID
            amount (int): Number of tokens to add
            
        Returns:
            bool: True if tokens were added, False otherwise
        """
        try:
            result = self.users.update_one(
                {'user_id': user_id},
                {'$inc': {'tokens': amount}}
            )
            
            if result.modified_count > 0:
                logger.info(f"Added {amount} tokens to user {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error adding tokens to user {user_id}: {e}")
            return False
    
    async def deduct_tokens(self, user_id, amount):
        """Deduct tokens from a user's account.
        
        Args:
            user_id (int): Telegram user ID
            amount (int): Number of tokens to deduct
            
        Returns:
            bool: True if tokens were deducted, False otherwise
        """
        try:
            # First check if user has enough tokens
            user = await self.get_user(user_id)
            if not user or user.get('tokens', 0) < amount:
                return False
            
            result = self.users.update_one(
                {'user_id': user_id},
                {'$inc': {'tokens': -amount}}
            )
            
            if result.modified_count > 0:
                logger.info(f"Deducted {amount} tokens from user {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deducting tokens from user {user_id}: {e}")
            return False
    
    async def log_interaction(self, user_id, interaction_type, model, tokens_used):
        """Log user interaction with the bot.
        
        Args:
            user_id (int): Telegram user ID
            interaction_type (str): Type of interaction (chat, image, etc.)
            model (str): AI model used
            tokens_used (int): Number of tokens used
            
        Returns:
            bool: True if interaction was logged, False otherwise
        """
        try:
            interaction_doc = {
                'user_id': user_id,
                'type': interaction_type,
                'model': model,
                'tokens_used': tokens_used,
                'timestamp': datetime.now()
            }
            
            self.interactions.insert_one(interaction_doc)
            return True
        except Exception as e:
            logger.error(f"Error logging interaction for user {user_id}: {e}")
            return False
    
    async def log_image(self, user_id, prompt, image_path, style, tokens_used):
        """Log image generation.
        
        Args:
            user_id (int): Telegram user ID
            prompt (str): Image prompt
            image_path (str): Path to the generated image
            style (str): Image style
            tokens_used (int): Number of tokens used
            
        Returns:
            bool: True if image was logged, False otherwise
        """
        try:
            image_doc = {
                'user_id': user_id,
                'prompt': prompt,
                'image_path': image_path,
                'style': style,
                'tokens_used': tokens_used,
                'timestamp': datetime.now()
            }
            
            self.images.insert_one(image_doc)
            return True
        except Exception as e:
            logger.error(f"Error logging image for user {user_id}: {e}")
            return False
    
    async def get_user_images(self, user_id, limit=10):
        """Get recent images generated by a user.
        
        Args:
            user_id (int): Telegram user ID
            limit (int, optional): Maximum number of images to return. Defaults to 10.
            
        Returns:
            list: List of image documents
        """
        try:
            return list(self.images.find({'user_id': user_id}).sort('timestamp', DESCENDING).limit(limit))
        except Exception as e:
            logger.error(f"Error getting images for user {user_id}: {e}")
            return []
    
    async def log_feedback(self, user_id, message_id, rating, comment=None):
        """Log user feedback.
        
        Args:
            user_id (int): Telegram user ID
            message_id (int): Message ID that received feedback
            rating (int): Rating (1-5)
            comment (str, optional): User comment. Defaults to None.
            
        Returns:
            bool: True if feedback was logged, False otherwise
        """
        try:
            feedback_doc = {
                'user_id': user_id,
                'message_id': message_id,
                'rating': rating,
                'comment': comment,
                'timestamp': datetime.now()
            }
            
            self.feedback.insert_one(feedback_doc)
            return True
        except Exception as e:
            logger.error(f"Error logging feedback for user {user_id}: {e}")
            return False
    
    async def get_user_stats(self, user_id):
        """Get usage statistics for a user.
        
        Args:
            user_id (int): Telegram user ID
            
        Returns:
            dict: User statistics
        """
        try:
            # Get total interactions
            total_interactions = self.interactions.count_documents({'user_id': user_id})
            
            # Get total tokens used
            pipeline = [
                {'$match': {'user_id': user_id}},
                {'$group': {'_id': None, 'total_tokens': {'$sum': '$tokens_used'}}}
            ]
            result = list(self.interactions.aggregate(pipeline))
            total_tokens = result[0]['total_tokens'] if result else 0
            
            # Get model usage breakdown
            pipeline = [
                {'$match': {'user_id': user_id}},
                {'$group': {'_id': '$model', 'count': {'$sum': 1}}}
            ]
            model_usage = {doc['_id']: doc['count'] for doc in self.interactions.aggregate(pipeline)}
            
            # Get interaction type breakdown
            pipeline = [
                {'$match': {'user_id': user_id}},
                {'$group': {'_id': '$type', 'count': {'$sum': 1}}}
            ]
            type_usage = {doc['_id']: doc['count'] for doc in self.interactions.aggregate(pipeline)}
            
            # Get total images generated
            total_images = self.images.count_documents({'user_id': user_id})
            
            # Get image style breakdown
            pipeline = [
                {'$match': {'user_id': user_id}},
                {'$group': {'_id': '$style', 'count': {'$sum': 1}}}
            ]
            style_usage = {doc['_id']: doc['count'] for doc in self.images.aggregate(pipeline)}
            
            return {
                'total_interactions': total_interactions,
                'total_tokens_used': total_tokens,
                'model_usage': model_usage,
                'type_usage': type_usage,
                'total_images': total_images,
                'style_usage': style_usage
            }
        except Exception as e:
            logger.error(f"Error getting stats for user {user_id}: {e}")
            return None
    
    async def get_global_stats(self):
        """Get global usage statistics.
        
        Returns:
            dict: Global statistics
        """
        try:
            # Get total users
            total_users = self.users.count_documents({})
            
            # Get active users (active in the last 24 hours)
            active_users = self.users.count_documents({
                'last_activity': {'$gte': datetime.now() - timedelta(hours=24)}
            })
            
            # Get premium users
            premium_users = self.users.count_documents({'is_premium': True})
            
            # Get total interactions
            total_interactions = self.interactions.count_documents({})
            
            # Get total tokens used
            pipeline = [
                {'$group': {'_id': None, 'total_tokens': {'$sum': '$tokens_used'}}}
            ]
            result = list(self.interactions.aggregate(pipeline))
            total_tokens = result[0]['total_tokens'] if result else 0
            
            # Get model usage breakdown
            pipeline = [
                {'$group': {'_id': '$model', 'count': {'$sum': 1}}}
            ]
            model_usage = {doc['_id']: doc['count'] for doc in self.interactions.aggregate(pipeline)}
            
            # Get interaction type breakdown
            pipeline = [
                {'$group': {'_id': '$type', 'count': {'$sum': 1}}}
            ]
            type_usage = {doc['_id']: doc['count'] for doc in self.interactions.aggregate(pipeline)}
            
            # Get total images generated
            total_images = self.images.count_documents({})
            
            # Get image style breakdown
            pipeline = [
                {'$group': {'_id': '$style', 'count': {'$sum': 1}}}
            ]
            style_usage = {doc['_id']: doc['count'] for doc in self.images.aggregate(pipeline)}
            
            # Get subscription tier breakdown
            pipeline = [
                {'$match': {'subscription_tier': {'$ne': None}}},
                {'$group': {'_id': '$subscription_tier', 'count': {'$sum': 1}}}
            ]
            subscription_tiers = {doc['_id']: doc['count'] for doc in self.users.aggregate(pipeline)}
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'premium_users': premium_users,
                'total_interactions': total_interactions,
                'total_tokens_used': total_tokens,
                'model_usage': model_usage,
                'type_usage': type_usage,
                'total_images': total_images,
                'style_usage': style_usage,
                'subscription_tiers': subscription_tiers
            }
        except Exception as e:
            logger.error(f"Error getting global stats: {e}")
            return None
    
    async def get_all_users(self, limit=100, skip=0):
        """Get all users from the database.
        
        Args:
            limit (int, optional): Maximum number of users to return. Defaults to 100.
            skip (int, optional): Number of users to skip. Defaults to 0.
            
        Returns:
            list: List of user documents
        """
        try:
            return list(self.users.find().sort('last_activity', DESCENDING).limit(limit).skip(skip))
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    async def get_premium_users(self):
        """Get all premium users from the database.
        
        Returns:
            list: List of premium user documents
        """
        try:
            return list(self.users.find({'is_premium': True}))
        except Exception as e:
            logger.error(f"Error getting premium users: {e}")
            return []
    
    async def ban_user(self, user_id):
        """Ban a user.
        
        Args:
            user_id (int): Telegram user ID
            
        Returns:
            bool: True if user was banned, False otherwise
        """
        try:
            result = self.users.update_one(
                {'user_id': user_id},
                {'$set': {'is_banned': True}}
            )
            
            if result.modified_count > 0:
                logger.info(f"Banned user {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error banning user {user_id}: {e}")
            return False
    
    async def unban_user(self, user_id):
        """Unban a user.
        
        Args:
            user_id (int): Telegram user ID
            
        Returns:
            bool: True if user was unbanned, False otherwise
        """
        try:
            result = self.users.update_one(
                {'user_id': user_id},
                {'$set': {'is_banned': False}}
            )
            
            if result.modified_count > 0:
                logger.info(f"Unbanned user {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error unbanning user {user_id}: {e}")
            return False
    
    async def set_setting(self, key, value):
        """Set a global setting.
        
        Args:
            key (str): Setting key
            value: Setting value
            
        Returns:
            bool: True if setting was set, False otherwise
        """
        try:
            self.settings.update_one(
                {'key': key},
                {'$set': {'value': value}},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error setting setting {key}: {e}")
            return False
    
    async def get_setting(self, key, default=None):
        """Get a global setting.
        
        Args:
            key (str): Setting key
            default: Default value if setting is not found
            
        Returns:
            Setting value or default
        """
        try:
            setting = self.settings.find_one({'key': key})
            return setting['value'] if setting else default
        except Exception as e:
            logger.error(f"Error getting setting {key}: {e}")
            return default
    
    async def reset_user_memory(self, user_id):
        """Reset a user's conversation history.
        
        Args:
            user_id (int): Telegram user ID
            
        Returns:
            bool: True if memory was reset, False otherwise
        """
        try:
            result = self.users.update_one(
                {'user_id': user_id},
                {'$set': {'conversation_history': []}}
            )
            
            if result.modified_count > 0:
                logger.info(f"Reset memory for user {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error resetting memory for user {user_id}: {e}")
            return False
    
    async def toggle_user_memory(self, user_id):
        """Toggle a user's memory setting.
        
        Args:
            user_id (int): Telegram user ID
            
        Returns:
            bool: New memory state (True if enabled, False if disabled)
        """
        try:
            user = await self.get_user(user_id)
            if not user:
                return False
            
            new_state = not user.get('memory_enabled', True)
            
            result = self.users.update_one(
                {'user_id': user_id},
                {'$set': {'memory_enabled': new_state}}
            )
            
            if result.modified_count > 0:
                logger.info(f"{'Enabled' if new_state else 'Disabled'} memory for user {user_id}")
                return new_state
            return user.get('memory_enabled', True)
        except Exception as e:
            logger.error(f"Error toggling memory for user {user_id}: {e}")
            return False
    
    async def get_token_history(self, user_id, limit=50):
        """Get token usage history for a user.
        
        Args:
            user_id (int): Telegram user ID
            limit (int, optional): Maximum number of entries to return. Defaults to 50.
            
        Returns:
            list: List of interaction documents
        """
        try:
            return list(self.interactions.find({'user_id': user_id}).sort('timestamp', DESCENDING).limit(limit))
        except Exception as e:
            logger.error(f"Error getting token history for user {user_id}: {e}")
            return []
    
    async def update_token_costs(self, chat_cost=1, image_cost=5):
        """Update default token costs for different operations.
        
        Args:
            chat_cost (int, optional): Cost per chat message. Defaults to 1.
            image_cost (int, optional): Cost per image generation. Defaults to 5.
            
        Returns:
            bool: True if costs were updated, False otherwise
        """
        try:
            await self.set_setting('token_costs', {
                'chat': chat_cost,
                'image': image_cost
            })
            return True
        except Exception as e:
            logger.error(f"Error updating token costs: {e}")
            return False
    
    async def get_token_costs(self):
        """Get current token costs.
        
        Returns:
            dict: Token costs for different operations
        """
        try:
            costs = await self.get_setting('token_costs')
            if not costs:
                # Default costs
                costs = {
                    'chat': 1,
                    'image': 5
                }
                await self.set_setting('token_costs', costs)
            return costs
        except Exception as e:
            logger.error(f"Error getting token costs: {e}")
            return {'chat': 1, 'image': 5}