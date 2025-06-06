#!/bin/bash

# Start the Flask app
python app.py &
APP_PID=$!

# Wait for the Flask app to start
sleep 5

# Set the webhook
python set_webhook.py

# Wait for the Flask app to finish
wait $APP_PID