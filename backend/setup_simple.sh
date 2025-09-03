#!/bin/bash

echo "🚀 Setting up Photo Tales with SQLite (no Docker required)..."

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

echo "🎯 Testing enhanced data store..."
python test_enhanced_store.py

echo ""
echo "🎉 Setup complete! Here's what you can do next:"
echo ""
echo "1. Edit config.env and add your OpenAI API key"
echo "2. Start the Flask app: python main.py"
echo "3. Test the system: python test_enhanced_store.py"
echo ""
echo "The system is now running with SQLite instead of PostgreSQL for simplicity."


