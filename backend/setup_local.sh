#!/bin/bash

echo "🚀 Setting up Photo Tales local development environment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "📦 Starting PostgreSQL and pgAdmin with Docker Compose..."
docker-compose up -d

echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

echo "🐍 Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

echo "🔧 Activating virtual environment and installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

echo "📝 Creating config.env from example..."
if [ ! -f "config.env" ]; then
    cp config.env.example config.env
    echo "⚠️  Please edit config.env and add your OpenAI API key!"
else
    echo "✅ config.env already exists"
fi

echo "🎯 Testing database connection..."
python -c "
from app.enhanced_data_store import EnhancedDataStore
try:
    store = EnhancedDataStore()
    print('✅ Database connection successful!')
    store.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    print('Make sure PostgreSQL is running and config.env is set correctly.')
"

echo ""
echo "🎉 Setup complete! Here's what you can do next:"
echo ""
echo "1. Edit config.env and add your OpenAI API key"
echo "2. Start the Flask app: python main.py"
echo "3. Access pgAdmin at http://localhost:5050 (admin@phototales.com / admin)"
echo "4. PostgreSQL is running on localhost:5432"
echo ""
echo "To stop the databases: docker-compose down"
echo "To start them again: docker-compose up -d"

