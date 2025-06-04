"""
Rate limiter for the Telegram bot.
Prevents users from sending too many requests in a short period of time.
"""

import logging
import time
from collections import defaultdict

logger = logging.getLogger('bot.utils.rate_limiter')

class RateLimiter:
    """Rate limiter to prevent abuse of the bot."""
    
    def __init__(self, max_requests=5, time_window=60):
        """Initialize the rate limiter.
        
        Args:
            max_requests (int, optional): Maximum number of requests allowed in the time window. Defaults to 5.
            time_window (int, optional): Time window in seconds. Defaults to 60.
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.request_history = defaultdict(list)
    
    def check_rate_limit(self, user_id):
        """Check if a user has exceeded the rate limit.
        
        Args:
            user_id: User ID
            
        Returns:
            bool: True if user is within rate limit, False otherwise
        """
        current_time = time.time()
        
        # Remove old requests from history
        self.request_history[user_id] = [
            timestamp for timestamp in self.request_history[user_id]
            if current_time - timestamp < self.time_window
        ]
        
        # Check if user has exceeded rate limit
        if len(self.request_history[user_id]) >= self.max_requests:
            logger.warning(f"User {user_id} has exceeded rate limit")
            return False
        
        # Add current request to history
        self.request_history[user_id].append(current_time)
        return True
    
    def reset_user(self, user_id):
        """Reset rate limit for a user.
        
        Args:
            user_id: User ID
        """
        if user_id in self.request_history:
            del self.request_history[user_id]
            logger.info(f"Reset rate limit for user {user_id}")
    
    def update_limits(self, max_requests, time_window):
        """Update rate limit parameters.
        
        Args:
            max_requests (int): Maximum number of requests allowed in the time window
            time_window (int): Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        logger.info(f"Updated rate limits: {max_requests} requests per {time_window} seconds")