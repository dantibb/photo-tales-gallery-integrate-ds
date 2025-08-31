#!/usr/bin/env python3
"""
Create a clean local_contexts.json file with the expected structure.
"""

import json
import os
from datetime import datetime

def create_clean_contexts():
    """Create a clean local_contexts.json file."""
    
    # Create the expected TinyDB structure
    clean_data = {
        "media_items": {},
        "contexts": {},
        "links": {}
    }
    
    # Add some sample media items based on the test images
    test_images = [
        "DSC_1107.jpg",
        "PXL_20240406_114128068.MP.jpg", 
        "DSC_0933.jpg",
        "PXL_20230825_154052286.jpg",
        "PXL_20220716_113519828.jpg",
        "DSC_1030.jpg",
        "PXL_20230729_110156176.jpg",
        "DSC_0994.jpg",
        "PXL_20221112_105736774.PORTRAIT.jpg",
        "DSC_2196.JPG",
        "DSC_1460.JPG",
        "DSC_0226.JPG",
        "DSC_0179.JPG",
        "DSC_2661~3.JPG",
        "DSC_0235.JPG",
        "DSC_0132.JPG",
        "DSC_0112.JPG",
        "DSC_1191.JPG",
        "DSC_0115.JPG",
        "DSC_6851.JPG",
        "DSC_1440.JPG",
        "DSC_1483.JPG",
        "DSC_0163.JPG",
        "DSC_0160.JPG",
        "DSC_1450.JPG",
        "PXL_20240408_083057072~2.jpg",
        "IMG_20190526_104513.jpg",
        "IMG_20180806_133706.jpg",
        "PXL_20250621_175211269.jpg"
    ]
    
    # Create media items
    for i, filename in enumerate(test_images, 1):
        file_path = f"test_images/{filename}"
        
        # Check if file exists to get actual size
        file_size = 0
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
        
        media_item = {
            "file_path": file_path,
            "filename": filename,
            "file_size": file_size,
            "file_type": "image/jpeg",
            "title": filename,
            "summary": "",
            "description": "",
            "tags": [],
            "image_metadata": {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        clean_data["media_items"][str(i)] = media_item
    
    # Save the clean file
    output_file = "backend/local_contexts.json"
    print(f"Creating clean file: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(clean_data, f, indent=2, ensure_ascii=False)
    
    print(f"Clean file created with {len(clean_data['media_items'])} media items")
    print("File structure:")
    print(f"  - media_items: {len(clean_data['media_items'])} items")
    print(f"  - contexts: {len(clean_data['contexts'])} items") 
    print(f"  - links: {len(clean_data['links'])} items")

if __name__ == "__main__":
    create_clean_contexts() 