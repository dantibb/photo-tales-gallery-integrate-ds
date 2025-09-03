#!/usr/bin/env python3
"""Test script to fix database schema and test photocard creation."""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
import uuid
from datetime import datetime

def test_and_fix_schema():
    """Test database connection and fix schema if needed."""
    try:
        # Connect to database
        conn = psycopg2.connect(
            host='localhost',
            database='photo_tales',
            user='postgres',
            password='password',
            port='5432'
        )
        
        print("✅ Connected to database successfully")
        
        with conn.cursor() as cursor:
            # Check if media table has metadata column
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'media' AND column_name = 'metadata'
            """)
            
            has_metadata = cursor.fetchone()
            
            if not has_metadata:
                print("📝 Adding metadata column to media table...")
                cursor.execute("ALTER TABLE media ADD COLUMN metadata JSONB DEFAULT '{}'")
                conn.commit()
                print("✅ Metadata column added successfully")
            else:
                print("✅ Metadata column already exists")
            
            # Test adding a media item with metadata
            print("🧪 Testing media item creation...")
            media_id = str(uuid.uuid4())
            test_metadata = {
                "type": "test_placeholder",
                "title": "Test Photocard",
                "description": "Test description"
            }
            
            cursor.execute("""
                INSERT INTO media (id, file_path, file_type, metadata, created_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (media_id, "test_path.jpg", "image", json.dumps(test_metadata), datetime.now()))
            
            result = cursor.fetchone()
            if result:
                print(f"✅ Test media item created with ID: {result[0]}")
                
                # Clean up test data
                cursor.execute("DELETE FROM media WHERE id = %s", (media_id,))
                conn.commit()
                print("🧹 Test data cleaned up")
            else:
                print("❌ Failed to create test media item")
        
        conn.close()
        print("✅ Database test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    test_and_fix_schema()
