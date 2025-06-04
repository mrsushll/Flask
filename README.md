# ChatGPT Claude Mistral Telegram Bot

A powerful Telegram bot that integrates multiple AI models for chat and image generation.

## Features

### 🔮 Multi-Model AI Chat System
- Seamlessly chat with OpenAI's ChatGPT, Anthropic's Claude, and Mistral AI
- Choose your preferred AI model
- Token-based system with configurable costs

### 🖼️ Advanced Image Generation
- Generate images from text prompts
- Multiple styles: realistic, anime, pixel-art, sketch
- Upscale images or create variations
- Save images to your personal gallery

### 💰 Tokens & Telegram Stars Subscription System
- Purchase tokens using Telegram Stars
- Tier-based subscriptions with monthly bonuses
- View balance, usage history, and refill via inline buttons
- Admin panel to adjust token prices and grant bonuses

### 🧠 Memory & Personalization
- Conversation memory system that remembers your chat context
- Toggle memory on/off or reset it completely
- Personalized settings for each user

### 🌐 Multilingual Support
- Full support for English and Arabic
- Easily switch between languages
- All messages and buttons are translated

### 🛠️ Admin Tools
- Comprehensive admin panel
- Broadcast messages to all users
- View statistics and analytics
- Manage users and tokens

## Setup Instructions

### Prerequisites
- Python 3.8+
- MongoDB database
- Telegram Bot API credentials
- API keys for OpenAI, Anthropic, and Mistral AI

### Installation

1. Clone the repository:
```bash
git clone https://github.com/mrsushll/telegram-ai-bot.git
cd telegram-ai-bot
```

2. Install dependencies:
```bash
pip install -r telegram_bot/requirements.txt
```

3. Create a `.env` file in the `telegram_bot` directory with the following content:
```
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
```

4. Run the bot:
```bash
cd telegram_bot
python bot.py
```

## User Commands

- `/start` - Start the bot
- `/help` - Show help message
- `/settings` - Configure bot settings
- `/balance` - Check token balance
- `/models` - Select AI model
- `/language` - Change language
- `/subscribe` - Purchase tokens
- `/memory` - Manage conversation memory
- `/image` - Generate an image
- `/styles` - View available image styles
- `/history` - View token usage history
- `/feedback` - Provide feedback

## Admin Commands

- `/admin` - Access admin panel
- `/add_tokens <user_id> <amount>` - Add tokens to a user
- `/user_info <user_id>` - View user information
- `/broadcast <message>` - Send message to all users
- `/stats` - View global statistics

## Image Generation

To generate an image, use the `/image` command followed by your description:

```
/image a beautiful sunset over mountains
```

You can specify a style by adding `--style` followed by the style name:

```
/image a beautiful sunset over mountains --style anime
```

Available styles:
- realistic
- anime
- pixel-art
- sketch

## Subscription Tiers

- **Basic Plan ($5)**
  - 50 tokens
  - 10 monthly bonus tokens
  - Access to all AI models
  - Basic image generation

- **Standard Plan ($10)**
  - 150 tokens
  - 30 monthly bonus tokens
  - Access to all AI models
  - HD image generation
  - Priority support

- **Premium Plan ($25)**
  - 500 tokens
  - 100 monthly bonus tokens
  - Access to all AI models
  - HD image generation
  - Priority support
  - Exclusive features

## Development

The bot is structured in a modular way:

- `bot.py` - Main bot class and entry point
- `ai_models/` - AI model handlers
- `database/` - MongoDB database handler
- `handlers/` - Command and callback handlers
- `utils/` - Utility functions
- `locales/` - Internationalization files

## Deployment

### Deploying to Render

This project is configured for easy deployment on [Render](https://render.com/).

1. Fork this repository to your GitHub account.

2. Create a new Web Service on Render:
   - Connect your GitHub account and select the forked repository
   - Select "Blueprint" as the deployment method
   - Render will automatically detect the `render.yaml` configuration

3. Configure the environment variables in the Render dashboard:
   - `TELEGRAM_API_ID`: Your Telegram API ID
   - `TELEGRAM_API_HASH`: Your Telegram API hash
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
   - `MONGODB_URI`: Your MongoDB connection string
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `ANTHROPIC_API_KEY`: Your Anthropic API key
   - `MISTRAL_API_KEY`: Your Mistral AI API key

4. Deploy the service.

### Docker Deployment

You can also deploy the bot using Docker:

1. Clone the repository
2. Create a `.env` file in the `telegram_bot` directory with your API keys
3. Run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

### Manual Deployment

You can also deploy the bot manually on any server:

1. Clone the repository
2. Install the dependencies: `pip install -r telegram_bot/requirements.txt`
3. Set up the environment variables
4. Run the bot: `cd telegram_bot && python bot.py`

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Developed by: @MLBOR
