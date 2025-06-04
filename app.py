import os
import json
import logging
import asyncio
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
            webhook_url = os.environ.get('WEBHOOK_URL', 'https://flask-53nr.onrender.com/')
            if not webhook_url.endswith('/'):
                webhook_url += '/'
            webhook_url += 'webhook'
            
            # Create a task to set the webhook
            asyncio.run_coroutine_threadsafe(
                bot_instance.client.send_request('setWebhook', {
                    'url': webhook_url,
                    'max_connections': 100,
                    'allowed_updates': ['message', 'callback_query', 'inline_query']
                }),
                bot_instance.client.loop
            )
            
            return jsonify({
                'status': 'success',
                'message': f'Webhook set to {webhook_url}'
            }), 200
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
            # Create a task to get the webhook info
            future = asyncio.run_coroutine_threadsafe(
                bot_instance.get_webhook_info(),
                bot_instance.client.loop
            )
            webhook_info = future.result(timeout=10)
            
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
        
        # Process the update asynchronously
        if bot_instance:
            # Create a task to process the update
            asyncio.run_coroutine_threadsafe(
                bot_instance.process_update(update),
                bot_instance.client.loop
            )
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
        if bot_instance:
            # Set the webhook URL
            webhook_url = os.environ.get('WEBHOOK_URL', 'https://flask-53nr.onrender.com/')
            if not webhook_url.endswith('/'):
                webhook_url += '/'
            webhook_url += 'webhook'
            
            logger.info(f"Setting webhook to {webhook_url}")
            
            # Start the bot
            asyncio.run(bot_instance.start())
        else:
            logger.error("Failed to initialize bot")
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

# Start the bot in a separate thread
if __name__ == '__main__':
    # Start the bot in a background thread
    bot_thread = Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Start the Flask app
    port = int(os.environ.get('PORT', 12000))
    app.run(host='0.0.0.0', port=port)
else:
    # For gunicorn, start the bot in a background thread
    bot_thread = Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()