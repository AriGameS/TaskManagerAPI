#!/bin/bash

# TaskManagerAPI Production Startup Script

set -e

echo "🚀 Starting TaskManagerAPI..."

# Check if running in production mode
if [ "$FLASK_ENV" = "production" ]; then
    echo "📦 Production mode detected"
    
    # Run database migrations if needed
    # python manage.py migrate
    
    # Collect static files if needed
    # python manage.py collectstatic --noinput
    
    # Start with gunicorn
    echo "🔧 Starting with Gunicorn..."
    exec gunicorn \
        --bind 0.0.0.0:5125 \
        --workers 4 \
        --worker-class sync \
        --worker-connections 1000 \
        --timeout 120 \
        --keep-alive 2 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --preload \
        --access-logfile - \
        --error-logfile - \
        --log-level info \
        app:app
else
    echo "🔧 Development mode detected"
    
    # Start with Flask development server
    exec python app.py
fi
