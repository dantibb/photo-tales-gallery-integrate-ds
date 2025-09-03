#!/bin/bash

echo "🚀 Starting Photo Tales local development environment..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run setup_local.sh first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if PostgreSQL is running
if ! docker ps | grep -q "photo_tales_postgres"; then
    echo "📦 Starting PostgreSQL..."
    docker-compose up -d postgres
    echo "⏳ Waiting for PostgreSQL to be ready..."
    sleep 10
fi

# Start Flask app
echo "🌐 Starting Flask application..."
export FLASK_ENV=development
export FLASK_DEBUG=1
python main.py


