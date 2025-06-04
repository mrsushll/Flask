"""
OpenAI API handler for the Telegram bot.
Handles interactions with OpenAI's GPT models.
"""

import logging
from openai import OpenAI

logger = logging.getLogger('bot.ai.openai')

class OpenAIHandler:
    """Handler for OpenAI's GPT models."""
    
    def __init__(self, api_key):
        """Initialize the OpenAI client.
        
        Args:
            api_key (str): OpenAI API key
        """
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o"  # Default to GPT-4o
    
    async def generate_response(self, message, conversation_history=None):
        """Generate a response using OpenAI's GPT model.
        
        Args:
            message (str): User message
            conversation_history (list, optional): Previous conversation history. Defaults to None.
            
        Returns:
            str: Generated response
        """
        if conversation_history is None:
            conversation_history = []
        
        # Format conversation history for OpenAI API
        messages = []
        
        # Add system message
        messages.append({
            "role": "system",
            "content": "You are ChatGPT, a large language model trained by OpenAI. "
                      "You are helping users in a Telegram bot called 'ChatGpt Claude Mistral'. "
                      "Be helpful, concise, and friendly."
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
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            # Extract and return the response text
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating response from OpenAI: {e}")
            return "Sorry, I encountered an error while processing your request. Please try again later."
    
    async def change_model(self, model_name):
        """Change the OpenAI model being used.
        
        Args:
            model_name (str): Name of the model to use
            
        Returns:
            bool: True if model was changed, False otherwise
        """
        valid_models = ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
        
        if model_name in valid_models:
            self.model = model_name
            logger.info(f"Changed OpenAI model to {model_name}")
            return True
        else:
            logger.warning(f"Invalid OpenAI model: {model_name}")
            return False