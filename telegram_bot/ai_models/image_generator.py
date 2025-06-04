"""
Image generation handler for the Telegram bot.
Handles image generation using OpenAI's DALL-E models.
"""

import logging
import os
import tempfile
import requests
from openai import OpenAI

logger = logging.getLogger('bot.ai.image')

class ImageGenerator:
    """Handler for AI image generation."""
    
    def __init__(self, api_key):
        """Initialize the OpenAI client for image generation.
        
        Args:
            api_key (str): OpenAI API key
        """
        self.client = OpenAI(api_key=api_key)
        self.model = "dall-e-3"  # Default to DALL-E 3
    
    async def generate_image(self, prompt, size="1024x1024"):
        """Generate an image using OpenAI's DALL-E model.
        
        Args:
            prompt (str): Image description
            size (str, optional): Image size. Defaults to "1024x1024".
            
        Returns:
            str: Path to the generated image file or None if generation failed
        """
        try:
            # Call OpenAI API to generate image
            response = self.client.images.generate(
                model=self.model,
                prompt=prompt,
                size=size,
                quality="standard",
                n=1
            )
            
            # Get image URL
            image_url = response.data[0].url
            
            # Download the image
            image_response = requests.get(image_url)
            if image_response.status_code != 200:
                logger.error(f"Failed to download image: {image_response.status_code}")
                return None
            
            # Save the image to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                temp_file.write(image_response.content)
                temp_path = temp_file.name
            
            logger.info(f"Generated image saved to {temp_path}")
            return temp_path
            
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return None
    
    async def change_model(self, model_name):
        """Change the image generation model being used.
        
        Args:
            model_name (str): Name of the model to use
            
        Returns:
            bool: True if model was changed, False otherwise
        """
        valid_models = ["dall-e-3", "dall-e-2"]
        
        if model_name in valid_models:
            self.model = model_name
            logger.info(f"Changed image model to {model_name}")
            return True
        else:
            logger.warning(f"Invalid image model: {model_name}")
            return False