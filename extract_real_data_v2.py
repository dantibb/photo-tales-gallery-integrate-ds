#!/usr/bin/env python3
"""
Extract real data from the corrupted local_contexts.json.corrupted file
using more targeted parsing based on the actual structure.
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any

def extract_default_items(content: str) -> Dict:
    """Extract default items from the corrupted file content."""
    
    print("Extracting default items...")
    
    # Look for _default section - it's at the beginning
    default_pattern = r'"_default":\s*{([^}]+)}'
    default_match = re.search(default_pattern, content, re.DOTALL)
    
    if not default_match:
        print("No _default section found")
        return {}
    
    default_section = default_match.group(1)
    
    # Extract individual default items
    items = {}
    
    # Pattern to match individual default items
    item_pattern = r'"(\d+)":\s*{([^}]+)}'
    item_matches = re.findall(item_pattern, default_section, re.DOTALL)
    
    for item_id, item_content in item_matches:
        try:
            # Clean up the item content
            item_content = item_content.strip()
            
            # Extract key-value pairs
            item_data = {}
            
            # Extract image_name
            image_name_match = re.search(r'"image_name":\s*"([^"]+)"', item_content)
            if image_name_match:
                item_data['image_name'] = image_name_match.group(1)
            
            # Extract summary_title
            summary_title_match = re.search(r'"summary_title":\s*"([^"]+)"', item_content)
            if summary_title_match:
                item_data['summary_title'] = summary_title_match.group(1)
            
            # Extract summary
            summary_match = re.search(r'"summary":\s*"([^"]*)"', item_content)
            if summary_match:
                item_data['summary'] = summary_match.group(1)
            
            # Extract tags
            tags_match = re.search(r'"tags":\s*\[([^\]]*)\]', item_content)
            if tags_match:
                tags_str = tags_match.group(1)
                # Parse tags array
                tags = []
                if tags_str.strip():
                    # Extract individual tag strings
                    tag_matches = re.findall(r'"([^"]+)"', tags_str)
                    tags = [tag.strip() for tag in tag_matches if tag.strip()]
                item_data['tags'] = tags
            
            # Extract contexts (simplified)
            contexts_match = re.search(r'"contexts":\s*\[([^\]]*)\]', item_content)
            if contexts_match:
                contexts_str = contexts_match.group(1)
                # For now, just store the raw contexts string
                item_data['contexts'] = contexts_str
            
            items[item_id] = item_data
            
        except Exception as e:
            print(f"Error parsing default item {item_id}: {e}")
            continue
    
    print(f"Extracted {len(items)} default items")
    return items

def find_media_items_section(content: str) -> str:
    """Find the media_items section in the corrupted file."""
    
    # Look for media_items section - it might be after the _default section
    media_pattern = r'"media_items":\s*{'
    media_match = re.search(media_pattern, content)
    
    if not media_match:
        print("No media_items section found")
        return ""
    
    # Find the start position
    start_pos = media_match.start()
    
    # Find the matching closing brace
    brace_count = 0
    pos = start_pos
    
    while pos < len(content):
        if content[pos] == '{':
            brace_count += 1
        elif content[pos] == '}':
            brace_count -= 1
            if brace_count == 0:
                # Found the closing brace
                return content[start_pos:pos+1]
        pos += 1
    
    print("Could not find closing brace for media_items")
    return ""

def extract_media_items_from_section(media_section: str) -> Dict:
    """Extract media items from the media_items section."""
    
    print("Extracting media items from section...")
    
    # Remove the "media_items": { wrapper
    media_section = media_section.replace('"media_items": {', '').rstrip('}')
    
    # Extract individual media items
    items = {}
    
    # Pattern to match individual media items
    item_pattern = r'"(\d+)":\s*{([^}]+)}'
    item_matches = re.findall(item_pattern, media_section, re.DOTALL)
    
    for item_id, item_content in item_matches:
        try:
            # Clean up the item content
            item_content = item_content.strip()
            
            # Extract key-value pairs
            item_data = {}
            
            # Extract file_path
            file_path_match = re.search(r'"file_path":\s*"([^"]+)"', item_content)
            if file_path_match:
                item_data['file_path'] = file_path_match.group(1)
            
            # Extract filename
            filename_match = re.search(r'"filename":\s*"([^"]+)"', item_content)
            if filename_match:
                item_data['filename'] = filename_match.group(1)
            
            # Extract file_size
            file_size_match = re.search(r'"file_size":\s*(\d+)', item_content)
            if file_size_match:
                item_data['file_size'] = int(file_size_match.group(1))
            
            # Extract file_type
            file_type_match = re.search(r'"file_type":\s*"([^"]+)"', item_content)
            if file_type_match:
                item_data['file_type'] = file_type_match.group(1)
            
            # Extract title
            title_match = re.search(r'"title":\s*"([^"]+)"', item_content)
            if title_match:
                item_data['title'] = title_match.group(1)
            
            # Extract summary
            summary_match = re.search(r'"summary":\s*"([^"]*)"', item_content)
            if summary_match:
                item_data['summary'] = summary_match.group(1)
            
            # Extract description
            description_match = re.search(r'"description":\s*"([^"]*)"', item_content)
            if description_match:
                item_data['description'] = description_match.group(1)
            
            # Extract tags
            tags_match = re.search(r'"tags":\s*\[([^\]]*)\]', item_content)
            if tags_match:
                tags_str = tags_match.group(1)
                # Parse tags array
                tags = []
                if tags_str.strip():
                    # Extract individual tag strings
                    tag_matches = re.findall(r'"([^"]+)"', tags_str)
                    tags = [tag.strip() for tag in tag_matches if tag.strip()]
                item_data['tags'] = tags
            
            # Extract image_metadata (simplified)
            image_metadata_match = re.search(r'"image_metadata":\s*{([^}]*)}', item_content)
            if image_metadata_match:
                item_data['image_metadata'] = {}
            
            # Extract timestamps
            created_at_match = re.search(r'"created_at":\s*"([^"]+)"', item_content)
            if created_at_match:
                item_data['created_at'] = created_at_match.group(1)
            
            updated_at_match = re.search(r'"updated_at":\s*"([^"]+)"', item_content)
            if updated_at_match:
                item_data['updated_at'] = updated_at_match.group(1)
            
            # Set defaults for missing fields
            if 'file_type' not in item_data:
                item_data['file_type'] = 'image/jpeg'
            if 'title' not in item_data:
                item_data['title'] = item_data.get('filename', '')
            if 'summary' not in item_data:
                item_data['summary'] = ''
            if 'description' not in item_data:
                item_data['description'] = ''
            if 'tags' not in item_data:
                item_data['tags'] = []
            if 'image_metadata' not in item_data:
                item_data['image_metadata'] = {}
            if 'created_at' not in item_data:
                item_data['created_at'] = datetime.now().isoformat()
            if 'updated_at' not in item_data:
                item_data['updated_at'] = datetime.now().isoformat()
            
            items[item_id] = item_data
            
        except Exception as e:
            print(f"Error parsing item {item_id}: {e}")
            continue
    
    print(f"Extracted {len(items)} media items")
    return items

def merge_data(media_items: Dict, default_items: Dict) -> Dict:
    """Merge media items with default items."""
    
    print("Merging data...")
    
    merged_items = {}
    
    for item_id, media_item in media_items.items():
        default_item = default_items.get(item_id)
        
        # Start with media item data
        merged_item = media_item.copy()
        
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
        
        merged_items[item_id] = merged_item
    
    return merged_items

def create_tinydb_structure(merged_items: Dict) -> Dict:
    """Create TinyDB-compatible structure."""
    
    print("Creating TinyDB structure...")
    
    tinydb_data = {
        "_default": {},
        "media_items": merged_items,
        "contexts": {},
        "links": {}
    }
    
    print(f"Created TinyDB structure with {len(tinydb_data['media_items'])} media items")
    
    return tinydb_data

def main():
    """Main function to extract real data from corrupted file."""
    
    corrupted_file = "backend/local_contexts.json.corrupted"
    output_file = "backend/local_contexts.json"
    
    # Check if corrupted file exists
    if not os.path.exists(corrupted_file):
        print(f"Corrupted file not found: {corrupted_file}")
        return
    
    # Read the corrupted file
    print(f"Reading corrupted file: {corrupted_file}")
    with open(corrupted_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"File size: {len(content)} characters")
    
    # Extract default items
    default_items = extract_default_items(content)
    
    # Find and extract media items section
    media_section = find_media_items_section(content)
    if media_section:
        media_items = extract_media_items_from_section(media_section)
    else:
        media_items = {}
    
    if not media_items and not default_items:
        print("No data extracted")
        return
    
    # If we have default items but no media items, create media items from defaults
    if not media_items and default_items:
        print("Creating media items from default items...")
        media_items = {}
        for item_id, default_item in default_items.items():
            media_items[item_id] = {
                'file_path': f"test_images/{default_item.get('image_name', 'unknown.jpg')}",
                'filename': default_item.get('image_name', 'unknown.jpg'),
                'file_size': 0,
                'file_type': 'image/jpeg',
                'title': default_item.get('summary_title', default_item.get('image_name', '')),
                'summary': default_item.get('summary', ''),
                'description': '',
                'tags': default_item.get('tags', []),
                'image_metadata': {},
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
    
    # Merge the data
    merged_items = merge_data(media_items, default_items)
    
    # Create TinyDB structure
    tinydb_data = create_tinydb_structure(merged_items)
    
    # Save the fixed file
    print(f"Saving extracted data to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tinydb_data, f, indent=2, ensure_ascii=False)
    
    print(f"Data extracted successfully!")
    print(f"Total media items: {len(tinydb_data['media_items'])}")
    
    # Print some statistics
    total_tags = 0
    items_with_tags = 0
    
    for item in tinydb_data['media_items'].values():
        tags = item.get('tags', [])
        if tags:
            items_with_tags += 1
            total_tags += len(tags)
    
    print(f"Items with tags: {items_with_tags}")
    print(f"Total tags: {total_tags}")

if __name__ == "__main__":
    main() 