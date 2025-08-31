#!/bin/bash

# Load environment variables from config.env
export $(cat backend/config.env | grep -v '^#' | xargs)

# Start the backend
cd backend
python3 local_api.py 