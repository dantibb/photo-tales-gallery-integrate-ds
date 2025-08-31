#!/usr/bin/env python3
"""
Migration script to transfer existing rich metadata from old database format
to the new TinyDB structure with title, summary, description, and tags fields.
"""

import json
import os
from local_db import LocalDB
import re

def clean_tag(tag):
    tag = tag.strip()
    # Remove markdown headings
    if tag.startswith('#'):
        return None
    # Remove tags surrounded by parentheses
    if re.match(r'^\(.*\)$', tag):
        return None
    # Remove empty or very short tags
    if len(tag) < 2:
        return None
    # Remove tags with only punctuation/special chars
    if not re.search(r'[a-zA-Z0-9]', tag):
        return None
    return tag

def migrate_existing_data():
    """Migrate existing rich metadata to new database structure."""
    
    # Load the existing database
    old_db_path = "local_contexts.json"
    if not os.path.exists(old_db_path):
        print("No existing database found to migrate.")
        return
    
    with open(old_db_path, 'r') as f:
        old_data = json.load(f)
    
    # Initialize database (will use the same file)
    db = LocalDB("local_contexts.json")
    
    # Check if we have the old format data
    if "_default" not in old_data:
        print("No old format data found to migrate.")
        return
    
    old_items = old_data.get("_default", {})
    migrated_count = 0
    
    print(f"Found {len(old_items)} items to migrate...")
    
    # First, let's sync the media items to ensure they exist
    print("Syncing media items...")
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp', '*.bmp']
    local_files = []
    
    for ext in image_extensions:
        pattern = os.path.join("test_images", ext)
        import glob
        local_files.extend(glob.glob(pattern))
        # Also check for uppercase extensions
        pattern = os.path.join("test_images", ext.upper())
        local_files.extend(glob.glob(pattern))
    
    # Sync with database
    new_items = db.sync_local_files(local_files)
    print(f"Synced {len(new_items)} new items")
    
    # Now migrate the metadata
    for item_id, item_data in old_items.items():
        try:
            # Extract metadata from old format
            image_name = item_data.get("image_name", "")
            summary_title = item_data.get("summary_title", "")
            summary_summary = item_data.get("summary_summary", "")
            tags = item_data.get("tags", [])
            # Clean tags
            tags = [clean_tag(t) for t in tags]
            tags = [t for t in tags if t]
            
            # Find corresponding media item in database
            media_items = db.list_media_items()
            matching_item = None
            
            for media_item in media_items:
                if media_item.get("filename") == image_name:
                    matching_item = media_item
                    break
            
            if matching_item:
                # Update the media item with rich metadata
                update_data = {}
                
                if summary_title:
                    update_data['title'] = summary_title
                if summary_summary:
                    update_data['summary'] = summary_summary
                if tags:
                    update_data['tags'] = tags
                
                if update_data:
                    db.update_media_item(matching_item['id'], **update_data)
                    migrated_count += 1
                    print(f"✓ Migrated: {image_name}")
                else:
                    print(f"- Skipped (no metadata): {image_name}")
            else:
                print(f"✗ Not found in DB: {image_name}")
                
        except Exception as e:
            print(f"✗ Error migrating {item_id}: {e}")
    
    print(f"\nMigration complete! Migrated {migrated_count} items.")
    
    # Also migrate contexts if they exist
    context_count = 0
    for item_id, item_data in old_items.items():
        try:
            contexts = item_data.get("contexts", [])
            if contexts:
                # Find corresponding media item
                image_name = item_data.get("image_name", "")
                media_items = db.list_media_items()
                matching_item = None
                
                for media_item in media_items:
                    if media_item.get("filename") == image_name:
                        matching_item = media_item
                        break
                
                if matching_item:
                    for context in contexts:
                        text = context.get("text", "")
                        if text:
                            db.add_context(matching_item['id'], text, context_type='ai_interview')
                            context_count += 1
                    
                    if contexts:
                        print(f"✓ Migrated {len(contexts)} contexts for: {image_name}")
                        
        except Exception as e:
            print(f"✗ Error migrating contexts for {item_id}: {e}")
    
    print(f"Migrated {context_count} total contexts.")
    db.close()

if __name__ == "__main__":
    migrate_existing_data() 