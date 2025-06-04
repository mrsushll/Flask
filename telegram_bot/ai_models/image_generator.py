"""
Image generation handler for the Telegram bot.
Handles image generation using OpenAI's DALL-E models with various styles and options.
"""

import logging
import os
import tempfile
import requests
from PIL import Image
from openai import OpenAI

logger = logging.getLogger('bot.ai.image')

class ImageGenerator:
    """Handler for AI image generation with multiple styles and options."""
    
    def __init__(self, api_key):
        """Initialize the OpenAI client for image generation.
        
        Args:
            api_key (str): OpenAI API key
        """
        self.client = OpenAI(api_key=api_key)
        self.model = "dall-e-3"  # Default to DALL-E 3
        self.styles = {
            "realistic": "Create a photorealistic image with natural lighting and details: ",
            "anime": "Create an anime-style illustration with vibrant colors and distinctive anime aesthetics: ",
            "pixel-art": "Create a pixel art image with visible pixels and limited color palette: ",
            "sketch": "Create a hand-drawn sketch with pencil/pen lines and minimal shading: "
        }
        self.default_style = "realistic"
        
    async def generate_image(self, prompt, size="1024x1024", style=None, quality="standard"):
        """Generate an image using OpenAI's DALL-E model.
        
        Args:
            prompt (str): Image description
            size (str, optional): Image size. Defaults to "1024x1024".
            style (str, optional): Image style (realistic, anime, pixel-art, sketch). Defaults to None.
            quality (str, optional): Image quality (standard, hd). Defaults to "standard".
            
        Returns:
            str: Path to the generated image file or None if generation failed
        """
        try:
            # Apply style to prompt if specified
            if style and style in self.styles:
                styled_prompt = self.styles[style] + prompt
            else:
                styled_prompt = prompt
            
            # Call OpenAI API to generate image
            response = self.client.images.generate(
                model=self.model,
                prompt=styled_prompt,
                size=size,
                quality=quality,
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
    
    async def upscale_image(self, image_path, scale=2):
        """Upscale an image to a higher resolution.
        
        Args:
            image_path (str): Path to the image file
            scale (int, optional): Scale factor. Defaults to 2.
            
        Returns:
            str: Path to the upscaled image file or None if upscaling failed
        """
        try:
            # Open the image
            img = Image.open(image_path)
            
            # Calculate new dimensions
            width, height = img.size
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            # Resize the image with high quality
            upscaled_img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Save the upscaled image to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix="_upscaled.png") as temp_file:
                upscaled_img.save(temp_file.name, format="PNG")
                temp_path = temp_file.name
            
            logger.info(f"Upscaled image saved to {temp_path}")
            return temp_path
            
        except Exception as e:
            logger.error(f"Error upscaling image: {e}")
            return None
    
    async def generate_variation(self, prompt, original_image_path, style=None):
        """Generate a variation of an image based on the original and a new prompt.
        
        Args:
            prompt (str): New image description
            original_image_path (str): Path to the original image file
            style (str, optional): Image style. Defaults to None.
            
        Returns:
            str: Path to the generated variation or None if generation failed
        """
        try:
            # For DALL-E 3, we can't directly create variations, so we'll use the original as inspiration
            # and generate a new image with a modified prompt
            variation_prompt = f"Create a variation of this concept, but with these changes: {prompt}"
            
            # Apply style if specified
            if style and style in self.styles:
                variation_prompt = self.styles[style] + variation_prompt
            
            # Generate the variation
            return await self.generate_image(variation_prompt)
            
        except Exception as e:
            logger.error(f"Error generating image variation: {e}")
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
            
    def get_available_styles(self):
        """Get a list of available image styles.
        
        Returns:
            list: List of available styles
        """
        return list(self.styles.keys())