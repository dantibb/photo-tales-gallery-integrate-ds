#!/usr/bin/env python3
"""
Simple test script to check database connections
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='config.env')

def test_postgres_connection():
    """Test PostgreSQL connection only."""
    try:
        import psycopg2
        print("✅ psycopg2 imported successfully")
        
        # Test connection
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            database=os.getenv('POSTGRES_DB', 'photo_tales'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', 'password'),
            port=os.getenv('POSTGRES_PORT', '5432')
        )
        print("✅ PostgreSQL connection successful!")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def test_chromadb_connection():
    """Test ChromaDB connection only."""
    try:
        import chromadb
        print("✅ chromadb imported successfully")
        
        # Test client creation
        client = chromadb.PersistentClient(path="./chroma_db")
        print("✅ ChromaDB client created successfully!")
        
        # Test collection creation
        collection = client.get_or_create_collection(name="test_collection")
        print("✅ ChromaDB collection created successfully!")
        return True
    except Exception as e:
        print(f"❌ ChromaDB connection failed: {e}")
        return False

def test_enhanced_data_store():
    """Test the full EnhancedDataStore."""
    try:
        from app.enhanced_data_store import EnhancedDataStore
        print("✅ EnhancedDataStore imported successfully")
        
        # Test store creation
        store = EnhancedDataStore()
        print("✅ EnhancedDataStore created successfully!")
        store.close()
        return True
    except Exception as e:
        print(f"❌ EnhancedDataStore creation failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing database connections...\n")
    
    print("1. Testing PostgreSQL connection...")
    postgres_ok = test_postgres_connection()
    print()
    
    print("2. Testing ChromaDB connection...")
    chromadb_ok = test_chromadb_connection()
    print()
    
    print("3. Testing EnhancedDataStore...")
    store_ok = test_enhanced_data_store()
    print()
    
    if postgres_ok and chromadb_ok and store_ok:
        print("🎉 All tests passed! Database connections are working.")
    else:
        print("❌ Some tests failed. Check the errors above.")
