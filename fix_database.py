#!/usr/bin/env python3
"""
Script to fix the database by extracting data from the corrupted file
and creating a proper TinyDB structure with all context data.
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any

def extract_from_corrupted_file(file_path: str) -> Dict:
    """Extract data from the corrupted file using multiple strategies."""
    
    print(f"Extracting data from: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"File size: {len(content)} characters")
    
    # Strategy 1: Try to parse as JSON
    try:
        data = json.loads(content)
        print("Successfully parsed as JSON")
        return data
    except json.JSONDecodeError as e:
        print(f"JSON parsing failed: {e}")
    
    # Strategy 2: Try to extract sections manually
    sections = {}
    
    # Look for _default section
    default_match = re.search(r'"_default":\s*({[^}]+})', content)
    if default_match:
        try:
            default_str = default_match.group(1)
            # Try to parse it as JSON
            default_data = json.loads(default_str)
            sections['_default'] = default_data
            print(f"Found _default section with {len(default_data)} items")
        except json.JSONDecodeError as e:
            print(f"Could not parse _default section: {e}")
    
    # Look for media_items section
    media_match = re.search(r'"media_items":\s*({[^}]+})', content)
    if media_match:
        try:
            media_str = media_match.group(1)
            # Try to parse it as JSON
            media_data = json.loads(media_str)
            sections['media_items'] = media_data
            print(f"Found media_items section with {len(media_data)} items")
        except json.JSONDecodeError as e:
            print(f"Could not parse media_items section: {e}")
    
    if sections:
        return sections
    
    return {}

def merge_rich_data(corrupted_data: Dict) -> Dict:
    """Merge data from corrupted file to create rich database."""
    
    print("Merging rich data from corrupted file...")
    
    # Extract sections
    default_items = corrupted_data.get('_default', {})
    media_items = corrupted_data.get('media_items', {})
    
    print(f"Found {len(default_items)} items in _default section")
    print(f"Found {len(media_items)} items in media_items section")
    
    # Create merged structure
    merged_items = {}
    
    # Process all media items
    for item_id, media_item in media_items.items():
        # Get corresponding default item if it exists
        default_item = default_items.get(item_id)
        
        # Start with media item data
        merged_item = {
            'file_path': media_item.get('file_path', ''),
            'filename': media_item.get('filename', ''),
            'file_size': media_item.get('file_size', 0),
            'file_type': media_item.get('file_type', 'image/jpeg'),
            'title': media_item.get('title', media_item.get('filename', '')),
            'summary': media_item.get('summary', ''),
            'description': media_item.get('description', ''),
            'tags': media_item.get('tags', []),
            'image_metadata': media_item.get('image_metadata', {}),
            'created_at': media_item.get('created_at', datetime.now().isoformat()),
            'updated_at': media_item.get('updated_at', datetime.now().isoformat())
        }
        
        # Merge with default item data if available
        if default_item:
            # Merge tags
            default_tags = default_item.get('tags', [])
            media_tags = merged_item.get('tags', [])
            all_tags = []
            if media_tags:
                all_tags.extend(media_tags)
            if default_tags:
                all_tags.extend(default_tags)
            
            # Remove duplicates
            unique_tags = []
            for tag in all_tags:
                if tag and tag.strip() and tag.strip() not in unique_tags:
                    unique_tags.append(tag.strip())
            
            merged_item['tags'] = unique_tags
            
            # Use default summary if media item doesn't have one
            if not merged_item.get('summary') and default_item.get('summary'):
                merged_item['summary'] = default_item['summary']
            
            # Use default title if media item doesn't have one
            if not merged_item.get('title') or merged_item['title'] == merged_item['filename']:
                if default_item.get('summary_title'):
                    merged_item['title'] = default_item['summary_title']
            
            # Add contexts from default item
            contexts = default_item.get('contexts', [])
            if contexts:
                merged_item['contexts'] = contexts
        
        merged_items[item_id] = merged_item
    
    return merged_items

def create_tinydb_structure(merged_items: Dict) -> Dict:
    """Create TinyDB-compatible structure."""
    
    print("Creating TinyDB structure...")
    
    tinydb_data = {
        "_default": {},
        "media_items": {},
        "contexts": {},
        "links": {}
    }
    
    # Convert merged items to TinyDB format
    for item_id, item in merged_items.items():
        # Remove contexts to separate table
        contexts = item.get('contexts', [])
        item_copy = item.copy()
        if 'contexts' in item_copy:
            del item_copy['contexts']
            tinydb_data['contexts'][item_id] = contexts
        
        tinydb_data['media_items'][item_id] = item_copy
    
    print(f"Created TinyDB structure with {len(tinydb_data['media_items'])} media items")
    print(f"Contexts: {len(tinydb_data['contexts'])} items")
    
    return tinydb_data

def main():
    """Main function to fix the database."""
    
    corrupted_file = "backend/local_contexts.json.corrupted"
    output_file = "backend/local_contexts.json"
    
    # Check if corrupted file exists
    if not os.path.exists(corrupted_file):
        print(f"Corrupted file not found: {corrupted_file}")
        return
    
    # Extract data from corrupted file
    corrupted_data = extract_from_corrupted_file(corrupted_file)
    
    if not corrupted_data:
        print("Failed to extract data from corrupted file")
        return
    
    # Merge rich data
    merged_items = merge_rich_data(corrupted_data)
    
    if not merged_items:
        print("Failed to merge data")
        return
    
    # Create TinyDB structure
    tinydb_data = create_tinydb_structure(merged_items)
    
    # Save the fixed file
    print(f"Saving fixed database to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tinydb_data, f, indent=2, ensure_ascii=False)
    
    print(f"Database fixed successfully!")
    print(f"Total media items: {len(tinydb_data['media_items'])}")
    
    # Print some statistics
    total_tags = 0
    items_with_tags = 0
    total_contexts = 0
    
    for item in tinydb_data['media_items'].values():
        tags = item.get('tags', [])
        if tags:
            items_with_tags += 1
            total_tags += len(tags)
    
    for contexts in tinydb_data['contexts'].values():
        total_contexts += len(contexts)
    
    print(f"Items with tags: {items_with_tags}")
    print(f"Total tags: {total_tags}")
    print(f"Total contexts: {total_contexts}")

if __name__ == "__main__":
    main() 