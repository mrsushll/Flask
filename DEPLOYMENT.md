# Deployment Guide

This document provides detailed instructions for deploying the ChatGPT Claude Mistral Telegram Bot to various platforms.

## Deploying to Render

### Prerequisites

1. A [Render](https://render.com/) account
2. A GitHub account
3. API keys for:
   - Telegram Bot API
   - OpenAI API
   - Anthropic API
   - Mistral AI API
4. MongoDB database (you can use MongoDB Atlas for a free cloud database)

### Deployment Steps

1. **Fork the Repository**
   - Fork this repository to your GitHub account

2. **Create a New Web Service on Render**
   - Go to your Render dashboard
   - Click "New" and select "Blueprint"
   - Connect your GitHub account if you haven't already
   - Select the forked repository
   - Render will automatically detect the `render.yaml` configuration

3. **Configure Environment Variables**
   - In the Render dashboard, navigate to your new service
   - Go to the "Environment" tab
   - Add the following environment variables:
     - `TELEGRAM_API_ID`: Your Telegram API ID
     - `TELEGRAM_API_HASH`: Your Telegram API hash
     - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
     - `MONGODB_URI`: Your MongoDB connection string
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `ANTHROPIC_API_KEY`: Your Anthropic API key
     - `MISTRAL_API_KEY`: Your Mistral AI API key

4. **Deploy the Service**
   - Click "Deploy" to start the deployment process
   - Render will build and deploy your bot automatically

5. **Verify Deployment**
   - Once deployed, check the logs to ensure the bot started successfully
   - Test the bot by sending a message to it on Telegram

## Manual Deployment on a VPS

### Prerequisites

1. A VPS with Ubuntu 20.04 or later
2. Python 3.8 or later installed
3. API keys (same as above)
4. MongoDB database

### Deployment Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/telegram-ai-bot.git
   cd telegram-ai-bot
   ```

2. **Install Dependencies**
   ```bash
   pip install -r telegram_bot/requirements.txt
   ```

3. **Create Environment Variables**
   Create a `.env` file in the `telegram_bot` directory:
   ```bash
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
   ```

4. **Run the Bot**
   ```bash
   cd telegram_bot
   python bot.py
   ```

5. **Set Up a Systemd Service (Optional)**
   To keep the bot running in the background:
   ```bash
   sudo nano /etc/systemd/system/telegram-bot.service
   ```
   
   Add the following content:
   ```
   [Unit]
   Description=Telegram AI Bot
   After=network.target

   [Service]
   User=your_username
   WorkingDirectory=/path/to/telegram-ai-bot/telegram_bot
   ExecStart=/usr/bin/python3 bot.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```
   
   Enable and start the service:
   ```bash
   sudo systemctl enable telegram-bot.service
   sudo systemctl start telegram-bot.service
   ```

## Troubleshooting

### Common Issues

1. **Bot Not Responding**
   - Check if the bot is running (check logs on Render or systemd status)
   - Verify that your Telegram Bot Token is correct
   - Make sure you've started a conversation with the bot on Telegram

2. **MongoDB Connection Issues**
   - Check if your MongoDB URI is correct
   - Ensure your IP address is whitelisted in MongoDB Atlas
   - Verify that your MongoDB user has the correct permissions

3. **API Key Issues**
   - Verify that all API keys are valid and have not expired
   - Check if you have sufficient credits/quota for the APIs

### Checking Logs

- **On Render**: Go to your service dashboard and click on "Logs"
- **On VPS**: Use `journalctl -u telegram-bot.service` if using systemd

## Updating the Bot

### On Render

Render will automatically deploy new versions when you push to your GitHub repository.

### On VPS

1. Pull the latest changes:
   ```bash
   cd /path/to/telegram-ai-bot
   git pull
   ```

2. Restart the service:
   ```bash
   sudo systemctl restart telegram-bot.service
   ```