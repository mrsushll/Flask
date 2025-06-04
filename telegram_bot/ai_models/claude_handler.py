"""
Anthropic Claude API handler for the Telegram bot.
Handles interactions with Anthropic's Claude models.
"""

import logging
from anthropic import Anthropic

logger = logging.getLogger('bot.ai.claude')

class ClaudeHandler:
    """Handler for Anthropic's Claude models."""
    
    def __init__(self, api_key):
        """Initialize the Anthropic client.
        
        Args:
            api_key (str): Anthropic API key
        """
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-opus-20240229"  # Default to Claude 3 Opus
    
    async def generate_response(self, message, conversation_history=None):
        """Generate a response using Anthropic's Claude model.
        
        Args:
            message (str): User message
            conversation_history (list, optional): Previous conversation history. Defaults to None.
            
        Returns:
            str: Generated response
        """
        if conversation_history is None:
            conversation_history = []
        
        # Format conversation history for Anthropic API
        messages = []
        
        # Add conversation history
        for entry in conversation_history:
            role = "user" if entry["role"] == "user" else "assistant"
            messages.append({
                "role": role,
                "content": entry["content"]
            })
        
        # Add the current message
        messages.append({
            "role": "user",
            "content": message
        })
        
        try:
            # Call Anthropic API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.7,
                system="You are Claude, an AI assistant by Anthropic, helping users in a Telegram bot called 'ChatGpt Claude Mistral'. Be helpful, concise, and friendly.",
                messages=messages
            )
            
            # Extract and return the response text
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Error generating response from Claude: {e}")
            return "Sorry, I encountered an error while processing your request. Please try again later."
    
    async def change_model(self, model_name):
        """Change the Claude model being used.
        
        Args:
            model_name (str): Name of the model to use
            
        Returns:
            bool: True if model was changed, False otherwise
        """
        valid_models = [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
        
        if model_name in valid_models:
            self.model = model_name
            logger.info(f"Changed Claude model to {model_name}")
            return True
        else:
            logger.warning(f"Invalid Claude model: {model_name}")
            return False