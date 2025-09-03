#!/usr/bin/env python3
"""
Script to clean up the database by removing missing files and adding existing ones
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='config.env')

def cleanup_database():
    """Clean up database by removing missing files and adding existing ones"""
    try:
        print("🔌 Connecting to database...")
        
        # Import here to avoid circular dependencies
        from app.enhanced_data_store import EnhancedDataStore
        
        store = EnhancedDataStore()
        
        # Get all media items
        existing_items = store.list_media_items()
        print(f"📸 Found {len(existing_items)} media items in database")
        
        # Check which files exist and which don't
        valid_items = []
        missing_items = []
        
        for item in existing_items:
            file_path = item.get('file_path')
            if file_path and os.path.exists(file_path):
                valid_items.append(item)
                print(f"✅ Valid: {item.get('title', 'Untitled')} - {file_path}")
            else:
                missing_items.append(item)
                print(f"❌ Missing: {item.get('title', 'Untitled')} - {file_path}")
        
        # Remove missing items
        if missing_items:
            print(f"\n🗑️ Removing {len(missing_items)} missing files...")
            for item in missing_items:
                try:
                    store.delete_media_item(item['id'])
                    print(f"   Removed: {item.get('title', 'Untitled')}")
                except Exception as e:
                    print(f"   Failed to remove {item.get('title', 'Untitled')}: {e}")
        
        # Add existing images from test_images directory
        print(f"\n📁 Checking test_images directory...")
        test_images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_images')
        
        if os.path.exists(test_images_dir):
            for filename in os.listdir(test_images_dir):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                    file_path = os.path.join(test_images_dir, filename)
                    
                    # Check if this file is already in the database
                    existing_item = store.get_media_by_file_path(file_path)
                    if existing_item:
                        print(f"   Already exists: {filename}")
                        continue
                    
                    # Add to database
                    metadata = {
                        'title': f'Test Image - {filename}',
                        'summary': f'A test image from the test_images directory',
                        'tags': ['test', 'sample', 'image'],
                        'file_size': os.path.getsize(file_path),
                        'file_type': 'image/jpeg' if filename.lower().endswith(('.jpg', '.jpeg')) else 'image/png'
                    }
                    
                    media_id = store.add_media_item(file_path, metadata)
                    print(f"   ✅ Added: {filename} (ID: {media_id})")
        
        # Final count
        final_items = store.list_media_items()
        print(f"\n🎉 Database cleanup complete!")
        print(f"   Final media count: {len(final_items)}")
        print(f"   Valid files: {len([item for item in final_items if os.path.exists(item.get('file_path', ''))])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database cleanup failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Photo Tales Database Cleanup ===")
    print("")
    
    success = cleanup_database()
    
    if success:
        print("")
        print("🎉 Database is now clean and ready!")
        print("📸 All remaining media items should have valid files!")
        sys.exit(0)
    else:
        print("")
        print("💥 Database cleanup failed!")
        sys.exit(1)

