"""
Mistral AI API handler for the Telegram bot.
Handles interactions with Mistral AI models.
"""

import logging
import os
import requests
import json

logger = logging.getLogger('bot.ai.mistral')

class MistralHandler:
    """Handler for Mistral AI models."""
    
    def __init__(self, api_key):
        """Initialize the Mistral client.
        
        Args:
            api_key (str): Mistral API key
        """
        self.api_key = api_key
        self.api_url = "https://api.mistral.ai/v1/chat/completions"
        self.model = "mistral-large-latest"  # Default to Mistral Large
    
    async def generate_response(self, message, conversation_history=None):
        """Generate a response using Mistral AI model.
        
        Args:
            message (str): User message
            conversation_history (list, optional): Previous conversation history. Defaults to None.
            
        Returns:
            str: Generated response
        """
        if conversation_history is None:
            conversation_history = []
        
        # Format conversation history for Mistral API
        messages = []
        
        # Add system message
        messages.append({
            "role": "system",
            "content": "You are Ravyn.ai, an advanced AI assistant powered by Mistral. Be helpful, concise, and friendly. Provide accurate and thoughtful responses to user queries."
        })
        
        # Add conversation history
        for entry in conversation_history:
            messages.append({
                "role": entry["role"],
                "content": entry["content"]
            })
        
        # Add the current message
        messages.append({
            "role": "user",
            "content": message
        })
        
        try:
            # Call Mistral API directly
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(payload)
            )
            
            if response.status_code == 200:
                response_data = response.json()
                return response_data["choices"][0]["message"]["content"]
            else:
                logger.error(f"Error from Mistral API: {response.status_code} - {response.text}")
                return "Sorry, I encountered an error while processing your request. Please try again later."
            
        except Exception as e:
            logger.error(f"Error generating response from Mistral: {e}")
            return "Sorry, I encountered an error while processing your request. Please try again later."
    
    async def change_model(self, model_name):
        """Change the Mistral model being used.
        
        Args:
            model_name (str): Name of the model to use
            
        Returns:
            bool: True if model was changed, False otherwise
        """
        valid_models = [
            "mistral-large-latest",
            "mistral-medium-latest",
            "mistral-small-latest",
            "open-mixtral-8x7b"
        ]
        
        if model_name in valid_models:
            self.model = model_name
            logger.info(f"Changed Mistral model to {model_name}")
            return True
        else:
            logger.warning(f"Invalid Mistral model: {model_name}")
            return False