from app import app

# This file is created to handle the case where gunicorn is looking for 'your_application.wsgi'
# It simply imports and re-exports the app from app.py