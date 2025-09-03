#!/usr/bin/env python3
"""
Demo script to show the enhanced data store search capabilities
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from simple_data_store import SimpleDataStore

def demo_search_capabilities():
    """Demonstrate the search capabilities of the enhanced data store."""
    print("🔍 Enhanced Data Store Search Demo")
    print("=" * 50)
    
    store = SimpleDataStore()
    
    # Demo 1: Search for Paris-related content
    print("\n1️⃣ Searching for 'Paris' content:")
    paris_results = store.search_documents("Paris")
    for i, doc in enumerate(paris_results, 1):
        print(f"   {i}. {doc['title']} ({doc['type']})")
        print(f"      Content preview: {doc['content'][:100]}...")
        print(f"      Tags: {doc['metadata'].get('tags', [])}")
        print()
    
    # Demo 2: Search for family-related content
    print("\n2️⃣ Searching for 'family' content:")
    family_results = store.search_documents("family")
    for i, doc in enumerate(family_results, 1):
        print(f"   {i}. {doc['title']} ({doc['type']})")
        print(f"      People mentioned: {doc['metadata'].get('people', [])}")
        print()
    
    # Demo 3: Search for specific locations
    print("\n3️⃣ Searching for 'Eiffel Tower' content:")
    eiffel_results = store.search_documents("Eiffel Tower")
    for i, doc in enumerate(eiffel_results, 1):
        print(f"   {i}. {doc['title']} ({doc['type']})")
        print(f"      Locations: {doc['metadata'].get('locations', [])}")
        print()
    
    # Demo 4: Get documents by type
    print("\n4️⃣ All interview documents:")
    interviews = store.get_documents_by_type("interview")
    for i, doc in enumerate(interviews, 1):
        print(f"   {i}. {doc['title']}")
        print(f"      Word count: {doc['metadata'].get('word_count', 'N/A')}")
        print(f"      Interview date: {doc['metadata'].get('interview_date', 'N/A')}")
        print()
    
    # Demo 5: Get documents by type
    print("\n5️⃣ All website documents:")
    websites = store.get_documents_by_type("website")
    for i, doc in enumerate(websites, 1):
        print(f"   {i}. {doc['title']}")
        print(f"      Source URL: {doc['metadata'].get('url', 'N/A')}")
        print(f"      Content type: {doc['metadata'].get('content_type', 'N/A')}")
        print()
    
    # Demo 6: Get documents by type
    print("\n6️⃣ All note documents:")
    notes = store.get_documents_by_type("note")
    for i, doc in enumerate(notes, 1):
        print(f"   {i}. {doc['title']}")
        print(f"      Trip date: {doc['metadata'].get('trip_date', 'N/A')}")
        print(f"      Travelers: {doc['metadata'].get('travelers', [])}")
        print()
    
    # Demo 7: Show document relationships
    print("\n7️⃣ Document relationships:")
    if interviews:
        interview_id = interviews[0]['id']
        related_docs = store.get_related_documents(interview_id)
        print(f"   Documents related to '{interviews[0]['title']}':")
        for i, doc in enumerate(related_docs, 1):
            print(f"   {i}. {doc['title']} ({doc['type']})")
        print()
    
    store.close()
    
    print("🎯 Key Features Demonstrated:")
    print("   ✅ Long document storage (interview transcripts, website content)")
    print("   ✅ Easy updates and CRUD operations")
    print("   ✅ Text-based search across all content")
    print("   ✅ Document type filtering")
    print("   ✅ Metadata-based organization")
    print("   ✅ Document relationships")
    print("   ✅ RAG-ready structure (can be enhanced with vector embeddings)")
    
    print("\n💡 This demonstrates how the enhanced data store addresses your requirements:")
    print("   1. ✅ Longer documents - No text length limits")
    print("   2. ✅ Easy updates - Simple CRUD operations")
    print("   3. ✅ RAG LLM ready - Structured for semantic search enhancement")

if __name__ == "__main__":
    demo_search_capabilities()


