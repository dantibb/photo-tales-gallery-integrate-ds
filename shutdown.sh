#!/bin/bash

echo "🛑 Shutting down Photo Tales application..."

# Function to kill process by port
kill_by_port() {
    local port=$1
    local process_id=$(lsof -ti:$port)
    if [ ! -z "$process_id" ]; then
        echo "Stopping process on port $port (PID: $process_id)..."
        kill -TERM $process_id 2>/dev/null
        sleep 2
        # Force kill if still running
        if kill -0 $process_id 2>/dev/null; then
            echo "Force killing process on port $port..."
            kill -9 $process_id 2>/dev/null
        fi
    else
        echo "No process found on port $port"
    fi
}

# Function to kill process by PID file
kill_by_pid_file() {
    local pid_file=$1
    local service_name=$2
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if [ ! -z "$pid" ] && kill -0 $pid 2>/dev/null; then
            echo "Stopping $service_name (PID: $pid)..."
            kill -TERM $pid 2>/dev/null
            sleep 2
            # Force kill if still running
            if kill -0 $pid 2>/dev/null; then
                echo "Force killing $service_name..."
                kill -9 $pid 2>/dev/null
            fi
            rm -f "$pid_file"
        else
            echo "$service_name not running or PID file invalid"
            rm -f "$pid_file"
        fi
    else
        echo "$service_name PID file not found"
    fi
}

# Stop processes by PID files (if started with start_all.sh)
echo "📱 Stopping frontend and backend..."
cd "$(dirname "$0")/.."  # Go to project root
kill_by_pid_file ".frontend.pid" "Frontend"
kill_by_pid_file ".backend.pid" "Backend"

# Fallback: Stop by port if PID files don't exist
echo "🔍 Checking for processes by port..."
kill_by_port 3000   # React default
kill_by_port 5173   # Vite default
kill_by_port 8080   # Flask backend
kill_by_port 5000   # Flask alternative

# Stop PostgreSQL and pgAdmin
echo "🗄️  Stopping database services..."
if command -v docker-compose &> /dev/null; then
    cd "$(dirname "$0")"
    docker-compose down
    echo "✅ Docker services stopped"
else
    echo "⚠️  Docker Compose not found, stopping PostgreSQL manually..."
    kill_by_port 5432  # PostgreSQL
    kill_by_port 5050  # pgAdmin
fi

# Kill any remaining Python processes related to the project
echo "🔍 Cleaning up remaining processes..."
pkill -f "photo-tales-gallery-integrate-ds" 2>/dev/null
pkill -f "main.py" 2>/dev/null
pkill -f "api.py" 2>/dev/null
pkill -f "local_api.py" 2>/dev/null

# Clean up PID files
cd "$(dirname "$0")/.."  # Go to project root
rm -f .frontend.pid .backend.pid

echo "✅ Shutdown complete!"
echo ""
echo "To restart the application:"
echo "1. Run: ./start_all.sh"
echo ""
echo "Or start services individually:"
echo "1. Start database: cd backend && docker-compose up -d"
echo "2. Start backend: cd backend && source venv/bin/activate && python main.py"
echo "3. Start frontend: npm run dev"
