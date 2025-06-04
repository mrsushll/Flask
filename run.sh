#!/bin/bash

# Run script for ChatGPT Claude Mistral Telegram Bot
# This script checks for dependencies and starts the bot

echo "Starting ChatGPT Claude Mistral Telegram Bot..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if we're in the right directory
if [ ! -d "telegram_bot" ]; then
    echo "Error: telegram_bot directory not found. Make sure you're running this script from the project root."
    exit 1
fi

# Check if .env file exists
if [ ! -f "telegram_bot/.env" ]; then
    echo "Warning: .env file not found in telegram_bot directory."
    echo "Creating a template .env file. Please edit it with your API keys."
    
    cat > telegram_bot/.env << EOL
# Telegram API credentials
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_BOT_TOKEN=your_bot_token

# MongoDB connection string
MONGODB_URI=your_mongodb_connection_string

# AI API keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
MISTRAL_API_KEY=your_mistral_api_key
EOL
    
    echo "Template .env file created. Please edit it before continuing."
    exit 1
fi

# Check if requirements are installed
echo "Checking dependencies..."
pip3 install -r telegram_bot/requirements.txt

# Create logs directory if it doesn't exist
mkdir -p telegram_bot/logs

# Start the bot
echo "Starting the bot..."
cd telegram_bot
python3 bot.py

# If the bot crashes, this will execute
echo "Bot has stopped. Check the logs for errors."