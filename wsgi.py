from app import app

# This is the WSGI entry point that gunicorn will use
if __name__ == "__main__":
    app.run()