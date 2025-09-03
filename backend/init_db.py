#!/usr/bin/env python3
"""
Simple database initialization script
Creates the database schema without importing the full Flask app
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='config.env')

def init_database():
    """Initialize the database schema"""
    try:
        print("🔌 Connecting to database...")
        
        # Import here to avoid circular dependencies
        from app.enhanced_data_store import EnhancedDataStore
        
        print("📊 Creating database schema...")
        store = EnhancedDataStore()
        
        print("✅ Database schema created successfully!")
        print("🎯 You can now start the Flask backend with: python3 main.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Photo Tales Database Initialization ===")
    print("")
    
    success = init_database()
    
    if success:
        print("")
        print("🎉 Database is ready!")
        sys.exit(0)
    else:
        print("")
        print("💥 Database initialization failed!")
        sys.exit(1)
