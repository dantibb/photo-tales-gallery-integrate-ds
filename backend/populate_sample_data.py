#!/usr/bin/env python3
"""
Script to populate the database with sample media data
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='config.env')

def populate_sample_data():
    """Populate the database with sample media data"""
    try:
        print("🔌 Connecting to database...")
        
        # Import here to avoid circular dependencies
        from app.enhanced_data_store import EnhancedDataStore
        
        store = EnhancedDataStore()
        
        # Check if we already have media items
        existing_items = store.list_media_items()
        if existing_items:
            print(f"📸 Found {len(existing_items)} existing media items")
            for item in existing_items:
                print(f"   - {item.get('title', 'Untitled')} ({item.get('file_path', 'No path')})")
            return True
        
        print("📸 Adding sample image to database...")
        
        # Get the path to the existing image
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, 'uploads', '20250903_130526_PXL_20240120_105258950.jpg')
        
        if not os.path.exists(image_path):
            print(f"❌ Image file not found: {image_path}")
            return False
        
        # Add the image to the database
        metadata = {
            'title': 'Sample Photo',
            'summary': 'A sample photo for testing the gallery',
            'tags': ['sample', 'test', 'photo'],
            'file_size': os.path.getsize(image_path),
            'file_type': 'image/jpeg'
        }
        
        media_id = store.add_media_item(image_path, metadata)
        print(f"✅ Added image with ID: {media_id}")
        print(f"   Path: {image_path}")
        print(f"   Title: {metadata['title']}")
        
        # Verify it was added
        added_item = store.get_media_item(media_id)
        if added_item:
            print(f"✅ Verified item in database: {added_item}")
        else:
            print("❌ Failed to retrieve added item")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to populate sample data: {e}")
        return False

if __name__ == "__main__":
    print("=== Photo Tales Sample Data Population ===")
    print("")
    
    success = populate_sample_data()
    
    if success:
        print("")
        print("🎉 Sample data added successfully!")
        print("📸 You should now see images in your photo gallery!")
        sys.exit(0)
    else:
        print("")
        print("💥 Failed to add sample data!")
        sys.exit(1)
