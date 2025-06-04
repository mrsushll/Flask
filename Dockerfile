FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY telegram_bot/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY telegram_bot/ .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port for health check
EXPOSE 8080

# Run the bot
CMD ["python", "bot.py"]