#!/usr/bin/env python3
"""
Create a fresh database with rich sample data including tags and contexts.
"""

import json
import os
from datetime import datetime
from typing import Dict, List

def create_rich_database():
    """Create a fresh database with rich sample data."""
    
    # Sample data with tags and contexts
    sample_data = {
        "1": {
            "file_path": "test_images/DSC_1107.jpg",
            "filename": "DSC_1107.jpg",
            "file_size": 0,
            "file_type": "image/jpeg",
            "title": "Mountain Sunset",
            "summary": "A beautiful sunset over the mountains during our hiking trip.",
            "description": "This photo was taken during our summer vacation in the Rockies.",
            "tags": ["mountains", "sunset", "hiking", "vacation", "nature", "summer"],
            "image_metadata": {},
            "created_at": "2025-07-31T12:00:00.000000",
            "updated_at": "2025-07-31T12:00:00.000000"
        },
        "2": {
            "file_path": "test_images/PXL_20240406_114128068.MP.jpg",
            "filename": "PXL_20240406_114128068.MP.jpg",
            "file_size": 0,
            "file_type": "image/jpeg",
            "title": "City Architecture",
            "summary": "Modern architecture in the city center.",
            "description": "Walking through the downtown area and captured this interesting building.",
            "tags": ["architecture", "city", "urban", "modern", "building"],
            "image_metadata": {},
            "created_at": "2025-07-31T12:00:00.000000",
            "updated_at": "2025-07-31T12:00:00.000000"
        },
        "3": {
            "file_path": "test_images/DSC_0933.jpg",
            "filename": "DSC_0933.jpg",
            "file_size": 0,
            "file_type": "image/jpeg",
            "title": "Family Portrait",
            "summary": "Family gathering at the park.",
            "description": "Everyone came together for a family reunion in the local park.",
            "tags": ["family", "portrait", "park", "reunion", "people"],
            "image_metadata": {},
            "created_at": "2025-07-31T12:00:00.000000",
            "updated_at": "2025-07-31T12:00:00.000000"
        },
        "4": {
            "file_path": "test_images/PXL_20230825_154052286.jpg",
            "filename": "PXL_20230825_154052286.jpg",
            "file_size": 0,
            "file_type": "image/jpeg",
            "title": "Beach Day",
            "summary": "Perfect day at the beach with friends.",
            "description": "Spent the day swimming and playing volleyball on the beach.",
            "tags": ["beach", "summer", "friends", "swimming", "vacation"],
            "image_metadata": {},
            "created_at": "2025-07-31T12:00:00.000000",
            "updated_at": "2025-07-31T12:00:00.000000"
        },
        "5": {
            "file_path": "test_images/PXL_20220716_113519828.jpg",
            "filename": "PXL_20220716_113519828.jpg",
            "file_size": 0,
            "file_type": "image/jpeg",
            "title": "Coffee Shop",
            "summary": "Cozy coffee shop in the morning.",
            "description": "Started the day with a great cup of coffee at my favorite local shop.",
            "tags": ["coffee", "morning", "food", "local", "cafe"],
            "image_metadata": {},
            "created_at": "2025-07-31T12:00:00.000000",
            "updated_at": "2025-07-31T12:00:00.000000"
        },
        "6": {
            "file_path": "test_images/DSC_1030.jpg",
            "filename": "DSC_1030.jpg",
            "file_size": 0,
            "file_type": "image/jpeg",
            "title": "Forest Trail",
            "summary": "Peaceful walk through the forest.",
            "description": "Hiking through the dense forest, enjoying the peace and quiet.",
            "tags": ["forest", "hiking", "nature", "trail", "peaceful"],
            "image_metadata": {},
            "created_at": "2025-07-31T12:00:00.000000",
            "updated_at": "2025-07-31T12:00:00.000000"
        },
        "7": {
            "file_path": "test_images/PXL_20230729_110156176.jpg",
            "filename": "PXL_20230729_110156176.jpg",
            "file_size": 0,
            "file_type": "image/jpeg",
            "title": "Street Art",
            "summary": "Colorful street art in the city.",
            "description": "Found this amazing mural while exploring the city streets.",
            "tags": ["street art", "mural", "colorful", "city", "art"],
            "image_metadata": {},
            "created_at": "2025-07-31T12:00:00.000000",
            "updated_at": "2025-07-31T12:00:00.000000"
        },
        "8": {
            "file_path": "test_images/DSC_0994.jpg",
            "filename": "DSC_0994.jpg",
            "file_size": 0,
            "file_type": "image/jpeg",
            "title": "Garden Flowers",
            "summary": "Beautiful flowers in the garden.",
            "description": "Spring flowers blooming in our backyard garden.",
            "tags": ["flowers", "garden", "spring", "nature", "colorful"],
            "image_metadata": {},
            "created_at": "2025-07-31T12:00:00.000000",
            "updated_at": "2025-07-31T12:00:00.000000"
        },
        "9": {
            "file_path": "test_images/PXL_20221112_105736774.PORTRAIT.jpg",
            "filename": "PXL_20221112_105736774.PORTRAIT.jpg",
            "file_size": 0,
            "file_type": "image/jpeg",
            "title": "Work Meeting",
            "summary": "Team meeting at the office.",
            "description": "Collaborating with the team on our latest project.",
            "tags": ["work", "meeting", "office", "team", "business"],
            "image_metadata": {},
            "created_at": "2025-07-31T12:00:00.000000",
            "updated_at": "2025-07-31T12:00:00.000000"
        },
        "10": {
            "file_path": "test_images/DSC_2196.JPG",
            "filename": "DSC_2196.JPG",
            "file_size": 0,
            "file_type": "image/jpeg",
            "title": "Mountain Lake",
            "summary": "Crystal clear lake in the mountains.",
            "description": "Stopped to admire this beautiful alpine lake during our hike.",
            "tags": ["lake", "mountains", "hiking", "nature", "water", "alpine"],
            "image_metadata": {},
            "created_at": "2025-07-31T12:00:00.000000",
            "updated_at": "2025-07-31T12:00:00.000000"
        }
    }
    
    # Sample contexts for some items
    sample_contexts = {
        "1": [
            {
                "id": "ctx-1-1",
                "text": "This was taken during our summer vacation in Colorado. The hike was challenging but worth it for this view.",
                "context_type": "description",
                "created_at": "2025-07-31T12:00:00.000000",
                "updated_at": "2025-07-31T12:00:00.000000"
            },
            {
                "id": "ctx-1-2", 
                "text": "We had to wake up at 4 AM to catch the sunrise. The temperature was perfect for hiking.",
                "context_type": "description",
                "created_at": "2025-07-31T12:00:00.000000",
                "updated_at": "2025-07-31T12:00:00.000000"
            }
        ],
        "3": [
            {
                "id": "ctx-3-1",
                "text": "This was our first family reunion since the pandemic. Everyone was so happy to see each other.",
                "context_type": "description", 
                "created_at": "2025-07-31T12:00:00.000000",
                "updated_at": "2025-07-31T12:00:00.000000"
            }
        ],
        "5": [
            {
                "id": "ctx-5-1",
                "text": "This coffee shop has the best pastries in town. I go there almost every morning.",
                "context_type": "description",
                "created_at": "2025-07-31T12:00:00.000000", 
                "updated_at": "2025-07-31T12:00:00.000000"
            }
        ]
    }
    
    # Create TinyDB structure
    tinydb_data = {
        "_default": {},
        "media_items": sample_data,
        "contexts": sample_contexts,
        "links": {}
    }
    
    # Save the database
    output_file = "backend/local_contexts.json"
    print(f"Creating rich database: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tinydb_data, f, indent=2, ensure_ascii=False)
    
    print(f"Database created successfully!")
    print(f"Media items: {len(tinydb_data['media_items'])}")
    print(f"Contexts: {len(tinydb_data['contexts'])}")
    
    # Print statistics
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
    create_rich_database() 