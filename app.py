import os
import json
import logging
import asyncio
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from threading import Thread

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Import the Telegram bot (lazy import to avoid circular imports)
def get_bot():
    try:
        from telegram_bot.bot import TelegramBot
        return TelegramBot()
    except Exception as e:
        logger.error(f"Error importing TelegramBot: {e}")
        return None

# Global bot instance
bot_instance = None

@app.route('/health', methods=['GET'])
def health_check():
    return 'OK', 200

@app.route('/', methods=['GET'])
def home():
    return 'Telegram Bot Service is running', 200

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    try:
        if bot_instance:
            # Get the webhook URL from environment
            webhook_url = os.environ.get('WEBHOOK_URL', 'https://work-1-agbdcklhstakqvwk.prod-runtime.all-hands.dev')
            if not webhook_url.endswith('/'):
                webhook_url += '/'
            webhook_url += 'webhook'
            
            # Use requests to set webhook directly with Telegram API
            import requests
            import json
            
            # Get the bot token
            bot_token = bot_instance.bot_token
            
            # Set the webhook
            set_webhook_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
            params = {
                'url': webhook_url,
                'max_connections': 100,
                'allowed_updates': json.dumps(['message', 'callback_query', 'inline_query'])
            }
            
            response = requests.post(set_webhook_url, params=params)
            result = response.json()
            
            if result.get('ok'):
                return jsonify({
                    'status': 'success',
                    'message': f'Webhook set to {webhook_url}',
                    'result': result
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': f'Failed to set webhook: {result}',
                }), 500
        else:
            return jsonify({
                'status': 'error',
                'message': 'Bot not initialized'
            }), 500
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/webhook_info', methods=['GET'])
def webhook_info():
    try:
        if bot_instance:
            # Use requests to get webhook info directly from Telegram API
            import requests
            
            # Get the bot token
            bot_token = bot_instance.bot_token
            
            # Get webhook info
            get_webhook_info_url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
            response = requests.get(get_webhook_info_url)
            webhook_info = response.json()
            
            return jsonify({
                'status': 'success',
                'webhook_info': webhook_info
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Bot not initialized'
            }), 500
    except Exception as e:
        logger.error(f"Error getting webhook info: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Get the update from Telegram
        update = request.get_json()
        logger.info(f"Received webhook update: {update}")
        
        # Process the update
        if bot_instance:
            # Process the update directly
            # For message updates
            if 'message' in update:
                message = update['message']
                chat_id = message.get('chat', {}).get('id')
                text = message.get('text', '')
                user_id = message.get('from', {}).get('id')
                
                if not user_id or not chat_id:
                    logger.error(f"Missing user_id or chat_id in update: {update}")
                    return jsonify({'status': 'error', 'message': 'Missing user_id or chat_id'}), 400
                
                # Use Telegram API to send a response
                import requests
                
                # Get the bot token
                bot_token = bot_instance.bot_token
                
                # Send a message back
                if text and text.startswith('/start'):
                    response_text = "Welcome to Ravyn.ai! I'm your advanced AI assistant powered by Mistral. How can I help you today?"
                elif text and text.startswith('/help'):
                    response_text = (
                        "🤖 **Ravyn.ai Help** 🤖\n\n"
                        "Here are the available commands:\n\n"
                        "/start - Start the bot\n"
                        "/help - Show this help message\n"
                        "/settings - Configure your preferences\n"
                        "/balance - Check your token balance\n"
                        "/models - Change AI model\n"
                        "/language - Change language\n"
                        "/memory - Manage conversation memory\n"
                        "/image - Generate an image\n"
                        "/styles - View available image styles\n"
                        "/history - View conversation history\n"
                        "/feedback - Send feedback\n\n"
                        "Just send a message to chat with me!"
                    )
                elif text and text.startswith('/'):
                    # Handle other commands
                    response_text = "I don't recognize that command. Type /help to see available commands."
                else:
                    # Process the message with Mistral AI
                    try:
                        # Use Mistral API to generate a response
                        # Prepare the API request
                        api_url = "https://api.mistral.ai/v1/chat/completions"
                        headers = {
                            "Content-Type": "application/json",
                            "Accept": "application/json",
                            "Authorization": f"Bearer {os.environ.get('MISTRAL_API_KEY')}"
                        }
                        
                        # Create the messages array
                        messages = [
                            {
                                "role": "system",
                                "content": "You are Ravyn.ai, an advanced AI assistant powered by Mistral. Be helpful, concise, and friendly. Provide accurate and thoughtful responses to user queries."
                            },
                            {
                                "role": "user",
                                "content": text
                            }
                        ]
                        
                        # We can't use await in a Flask route, so we'll use the database directly
                        # without async/await
                        
                        payload = {
                            "model": "mistral-large-latest",
                            "messages": messages,
                            "max_tokens": 1000,
                            "temperature": 0.7
                        }
                        
                        # Make the API request
                        response = requests.post(
                            api_url,
                            headers=headers,
                            data=json.dumps(payload)
                        )
                        
                        if response.status_code == 200:
                            response_data = response.json()
                            response_text = response_data["choices"][0]["message"]["content"]
                        else:
                            logger.error(f"Error from Mistral API: {response.status_code} - {response.text}")
                            response_text = "Sorry, I encountered an error while processing your request. Please try again later."
                    except Exception as e:
                        logger.error(f"Error generating response: {e}")
                        response_text = "Sorry, I encountered an error while processing your request. Please try again later."
                
                send_message_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                params = {
                    'chat_id': chat_id,
                    'text': response_text,
                    'parse_mode': 'Markdown'
                }
                
                requests.post(send_message_url, params=params)
            
            # For callback query updates (button presses)
            elif 'callback_query' in update:
                callback_query = update['callback_query']
                callback_id = callback_query.get('id')
                chat_id = callback_query.get('message', {}).get('chat', {}).get('id')
                data = callback_query.get('data', '')
                
                # Answer the callback query
                import requests
                
                # Get the bot token
                bot_token = bot_instance.bot_token
                
                # Answer callback query
                answer_callback_url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"
                params = {
                    'callback_query_id': callback_id,
                    'text': f"You selected: {data}"
                }
                
                requests.post(answer_callback_url, params=params)
                
                # Send a message to the chat
                send_message_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                params = {
                    'chat_id': chat_id,
                    'text': f"You selected: {data}. Processing your request...",
                    'parse_mode': 'Markdown'
                }
                
                requests.post(send_message_url, params=params)
            
            return jsonify({'status': 'success'}), 200
        else:
            logger.error("Bot instance not initialized")
            return jsonify({'status': 'error', 'message': 'Bot not initialized'}), 500
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def start_bot():
    global bot_instance
    try:
        # Initialize the bot
        bot_instance = get_bot()
        if not bot_instance:
            logger.error("Failed to initialize bot")
            return
            
        # Start the bot in a separate process
        import subprocess
        import sys
        
        logger.info("Starting bot in a separate process...")
        subprocess.Popen([sys.executable, 'run_bot.py'])
        logger.info("Bot process started")
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

# Initialize the bot
bot_instance = get_bot()

# Initialize the bot when the app starts
if __name__ == '__main__':
    # Start the Flask app
    port = int(os.environ.get('PORT', 12000))
    app.run(host='0.0.0.0', port=port)
else:
    # For gunicorn, we'll initialize the bot separately
    pass