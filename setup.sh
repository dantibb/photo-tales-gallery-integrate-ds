#!/bin/bash

echo "🚀 Setting up Photo Tales Gallery..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first:"
    echo "   Visit: https://nodejs.org/"
    echo "   Or use nvm: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first:"
    echo "   Visit: https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Node.js and Python are installed"

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
npm install

# Install backend dependencies
echo "🐍 Installing backend dependencies..."
cd backend
pip3 install -r requirements.txt
cd ..

# Check if test_images folder exists
if [ ! -d "test_images" ]; then
    echo "⚠️  test_images folder not found!"
    echo "📁 Creating test_images folder..."
    mkdir -p test_images
    echo "✅ Created test_images folder"
    echo "📝 Please add some images to the test_images folder"
else
    echo "✅ test_images folder found"
fi

# Check if config.env exists
if [ ! -f "backend/config.env" ]; then
    echo "⚠️  Configuration file not found!"
    echo "📝 Creating backend/config.env with local configuration..."
    cat > backend/config.env << EOF
# Local Configuration
IMAGES_FOLDER=test_images

# OpenAI Configuration (optional - for AI interviews)
OPENAI_API_KEY=your-openai-api-key

# Flask Configuration
FLASK_SECRET_KEY=local-dev-secret-key
EOF
    echo "✅ Created backend/config.env"
    echo "📝 Update OPENAI_API_KEY in backend/config.env if you want to use AI interviews"
else
    echo "✅ Configuration file found"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start the application:"
echo "  npm run dev:full    # Start both frontend and backend"
echo "  npm run dev:frontend # Start frontend only"
echo "  npm run dev:backend  # Start backend only"
echo ""
echo "📖 For more information, see README.md" 