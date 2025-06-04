import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return 'OK', 200

@app.route('/', methods=['GET'])
def home():
    return 'Telegram Bot Service is running', 200

@app.route('/webhook', methods=['POST'])
def webhook():
    # This is a placeholder for the webhook handler
    # In a real implementation, you would process the webhook data here
    # and forward it to your Telegram bot
    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 12000))
    app.run(host='0.0.0.0', port=port)