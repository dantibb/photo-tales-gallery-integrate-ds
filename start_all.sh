#!/bin/bash

set -e

# 1. Install frontend dependencies
echo "Installing frontend dependencies..."
npm install

# 2. Install backend dependencies
echo "Installing backend dependencies..."
cd backend
pip3 install -r requirements.txt

# 3. Ensure backend config.env exists
if [ ! -f config.env ]; then
  echo "config.env not found. Copying from config.env.example..."
  cp config.env.example config.env
fi

# 4. Warn if config.env contains placeholder values
WARN=0
if grep -q '/path/to/your/service-account-key.json' config.env; then
  echo "WARNING: GOOGLE_APPLICATION_CREDENTIALS is not set in backend/config.env."
  WARN=1
fi
if grep -q 'your-gcs-bucket-name' config.env; then
  echo "WARNING: GCS_BUCKET_NAME is not set in backend/config.env."
  WARN=1
fi
if grep -q 'your-openai-api-key' config.env; then
  echo "WARNING: OPENAI_API_KEY is not set in backend/config.env."
  WARN=1
fi
if grep -q 'your-secret-key-here' config.env; then
  echo "WARNING: FLASK_SECRET_KEY is not set in backend/config.env."
  WARN=1
fi
if [ $WARN -eq 1 ]; then
  echo "One or more environment variables in backend/config.env are placeholders. Please update them for full functionality."
fi

cd ..

# 5. Start backend server in background
echo "Starting backend server..."
npm run dev:backend &
BACKEND_PID=$!

# 6. Start frontend server in background
echo "Starting frontend server..."
npm run dev &
FRONTEND_PID=$!

echo "\nBoth servers are starting."
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "\nAccess the frontend at http://localhost:5173 (or as printed by Vite)."

echo "To stop both servers, run:"
echo "  kill $BACKEND_PID $FRONTEND_PID" 