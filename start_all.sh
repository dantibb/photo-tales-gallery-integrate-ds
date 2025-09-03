#!/bin/bash

set -e

echo "🚀 Starting Photo Tales Gallery Application..."

# 1. Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# 2. Install frontend dependencies
echo "📦 Installing frontend dependencies..."
npm install

# 3. Install backend dependencies
echo "🐍 Installing backend dependencies..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment and installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# 4. Ensure backend config.env exists
if [ ! -f config.env ]; then
    echo "📝 config.env not found. Copying from config.env.example..."
    cp config.env.example config.env
    echo "⚠️  Please edit config.env and add your OpenAI API key!"
fi

# 5. Start PostgreSQL and pgAdmin
echo "🗄️  Starting PostgreSQL and pgAdmin..."
docker-compose up -d

echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

# 6. Test database connection
echo "🔍 Testing database connection..."
python -c "
from app.enhanced_data_store import EnhancedDataStore
try:
    store = EnhancedDataStore()
    print('✅ Database connection successful!')
    store.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    print('Make sure PostgreSQL is running and config.env is set correctly.')
    exit(1)
"

cd ..

# 7. Start backend server in background
echo "🐍 Starting backend server..."
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!
cd ..

# 8. Start frontend server in background
echo "📱 Starting frontend server..."
npm run dev &
FRONTEND_PID=$!

# 9. Save PIDs to a file for shutdown script
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

echo ""
echo "🎉 Both servers are starting!"
echo "Backend PID: $BACKEND_PID (Flask on port 8080)"
echo "Frontend PID: $FRONTEND_PID (Vite on port 5173)"
echo ""
echo "🌐 Access the application:"
echo "   Frontend: http://localhost:5173"
echo "   Backend API: http://localhost:8080"
echo "   pgAdmin: http://localhost:5050 (admin@phototales.com / admin)"
echo "   PostgreSQL: localhost:5432"
echo ""
echo "🛑 To stop all services, run:"
echo "   ./shutdown.sh"
echo ""
echo "📊 To view logs:"
echo "   Backend: tail -f backend/logs/app.log (if logging is enabled)"
echo "   Docker: docker-compose logs -f (in backend directory)" 