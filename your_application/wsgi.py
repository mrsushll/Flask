from app import app

# This file is created to handle the case where gunicorn is looking for 'your_application.wsgi'
# Export the app as 'application' for gunicorn to find it
application = app