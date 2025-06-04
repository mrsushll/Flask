from app import app

# This is the WSGI entry point that gunicorn will use
# Export the app as 'application' for gunicorn to find it
application = app

if __name__ == "__main__":
    app.run()