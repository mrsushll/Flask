# ChatGpt Claude Mistral Telegram Bot

A highly advanced Telegram bot that integrates multiple AI chat models for conversation, including OpenAI's ChatGPT, Anthropic's Claude, and Mistral's models. The bot also supports image generation using AI.

## Features

- **Multiple AI Models**: Chat with OpenAI's ChatGPT, Anthropic's Claude, and Mistral AI
- **Image Generation**: Generate images using AI models
- **Subscription System**: Token-based system using Telegram Stars
- **MongoDB Integration**: Store user data, tokens, usage logs, and settings
- **Admin Controls**: Manage users, tokens, and bot settings
- **Multi-language Support**: English and Arabic
- **User-friendly Interface**: Inline keyboards and commands

## Setup Instructions

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file based on `.env.example` and fill in your API keys:
   ```
   cp .env.example .env
   ```
4. Get your Telegram API credentials from https://my.telegram.org/apps
5. Get API keys for OpenAI, Anthropic, and Mistral
6. Run the bot:
   ```
   python bot.py
   ```

## Environment Variables

- `TELEGRAM_API_ID`: Your Telegram API ID
- `TELEGRAM_API_HASH`: Your Telegram API hash
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `MONGODB_URI`: MongoDB connection string
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key
- `MISTRAL_API_KEY`: Mistral API key

## Bot Commands

- `/start` - Start the bot
- `/help` - Show help message
- `/settings` - Configure bot settings
- `/balance` - Check token balance
- `/models` - Select AI model
- `/language` - Change language
- `/subscribe` - Purchase tokens

### Admin Commands

- `/admin` - Access admin panel
- `/add_tokens <user_id> <amount>` - Add tokens to a user
- `/user_info <user_id>` - Get user information
- `/broadcast <message>` - Send message to all users
- `/stats` - View global statistics

## Project Structure

```
telegram_bot/
├── ai_models/
│   ├── __init__.py
│   ├── claude_handler.py
│   ├── image_generator.py
│   ├── mistral_handler.py
│   └── openai_handler.py
├── database/
│   ├── __init__.py
│   └── mongodb.py
├── handlers/
│   ├── __init__.py
│   ├── admin_handler.py
│   ├── command_handler.py
│   └── subscription_handler.py
├── locales/
│   ├── en/
│   │   └── messages.json
│   └── ar/
│       └── messages.json
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   └── rate_limiter.py
├── __init__.py
├── .env.example
├── bot.py
└── README.md
```

## Developer

Developed by: @MLBOR