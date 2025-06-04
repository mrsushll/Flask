"""
Mistral AI API handler for the Telegram bot.
Handles interactions with Mistral AI models.
"""

import logging
from mistralai.client import MistralClient
from mistralai.chat.models import UserMessage, SystemMessage, AssistantMessage

logger = logging.getLogger('bot.ai.mistral')

class MistralHandler:
    """Handler for Mistral AI models."""
    
    def __init__(self, api_key):
        """Initialize the Mistral client.
        
        Args:
            api_key (str): Mistral API key
        """
        self.client = MistralClient(api_key=api_key)
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
        messages.append(
            SystemMessage(content="You are Mistral AI, helping users in a Telegram bot called 'ChatGpt Claude Mistral'. Be helpful, concise, and friendly.")
        )
        
        # Add conversation history
        for entry in conversation_history:
            if entry["role"] == "user":
                messages.append(UserMessage(content=entry["content"]))
            else:
                messages.append(AssistantMessage(content=entry["content"]))
        
        # Add the current message
        messages.append(
            UserMessage(content=message)
        )
        
        try:
            # Call Mistral API
            response = self.client.chat(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            # Extract and return the response text
            return response.choices[0].message.content
            
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
            "mistral-small-latest"
        ]
        
        if model_name in valid_models:
            self.model = model_name
            logger.info(f"Changed Mistral model to {model_name}")
            return True
        else:
            logger.warning(f"Invalid Mistral model: {model_name}")
            return False