#!/usr/bin/env python3
"""
Test script for the new enhanced data store API endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8080"

def test_website_import():
    """Test website import functionality."""
    print("🌐 Testing Website Import...")
    
    # Test with a real website
    test_url = "https://httpbin.org/html"
    
    data = {
        "url": test_url,
        "title": "Test HTML Page"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/website/import", json=data)
        print(f"Status: {response.status_code}")
        
        if response.ok:
            result = response.json()
            print(f"✅ Success: {result['message']}")
            print(f"   Document ID: {result['id']}")
            print(f"   Title: {result['title']}")
            print(f"   Content Length: {result['content_length']}")
            print(f"   Metadata: {json.dumps(result['metadata'], indent=2)}")
            return result['id']
        else:
            print(f"❌ Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def test_transcript_add():
    """Test transcript addition functionality."""
    print("\n📝 Testing Transcript Addition...")
    
    data = {
        "title": "Test Interview Transcript",
        "content": """
        Interviewer: Tell me about your recent trip to Paris.
        
        John: It was absolutely amazing! We went in May 2022 and the weather was perfect. 
        We spent three days exploring the city, starting with the Eiffel Tower on our first day.
        
        Interviewer: What was your favorite part?
        
        John: Definitely the Louvre Museum. Sarah is an art teacher, so she was in heaven. 
        We spent almost a full day there, and Emma was surprisingly engaged with the paintings.
        
        Interviewer: Any memorable meals?
        
        Sarah: Oh yes! We had the most incredible croissants at a small café near the Seine. 
        We went back the next day just for more croissants!
        """,
        "metadata": {
            "people": ["John", "Sarah", "Emma"],
            "locations": ["Paris", "Eiffel Tower", "Louvre", "Seine"],
            "date": "2022-05-15",
            "tags": ["Paris", "vacation", "family", "art", "food"]
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/transcript/add", json=data)
        print(f"Status: {response.status_code}")
        
        if response.ok:
            result = response.json()
            print(f"✅ Success: {result['message']}")
            print(f"   Document ID: {result['id']}")
            print(f"   Title: {result['title']}")
            return result['id']
        else:
            print(f"❌ Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def test_document_search():
    """Test document search functionality."""
    print("\n🔍 Testing Document Search...")
    
    # Search for Paris-related content
    search_data = {
        "query": "Paris",
        "limit": 5
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/documents/search", json=search_data)
        print(f"Status: {response.status_code}")
        
        if response.ok:
            result = response.json()
            print(f"✅ Search successful")
            print(f"   Query: {result['query']}")
            print(f"   Results found: {result['count']}")
            
            for i, doc in enumerate(result['results'], 1):
                print(f"   {i}. {doc['title']} ({doc['type']})")
                print(f"      Content preview: {doc['content'][:100]}...")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_get_documents_by_type():
    """Test getting documents by type."""
    print("\n📚 Testing Get Documents by Type...")
    
    # Get all interview documents
    try:
        response = requests.get(f"{BASE_URL}/api/documents/interview")
        print(f"Status: {response.status_code}")
        
        if response.ok:
            result = response.json()
            print(f"✅ Retrieved {result['count']} interview documents")
            
            for i, doc in enumerate(result['documents'], 1):
                print(f"   {i}. {doc['title']}")
                print(f"      Created: {doc['created_at']}")
                print(f"      Content length: {len(doc['content'])}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_health_check():
    """Test if the server is running."""
    print("🏥 Testing Server Health...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        
        if response.ok:
            print("✅ Server is running and healthy")
            return True
        else:
            print(f"❌ Server error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Enhanced Data Store API Test Suite")
    print("=" * 50)
    
    # Check if server is running
    if not test_health_check():
        print("\n❌ Server is not running. Please start the Flask app first:")
        print("   cd backend && python main.py")
        return
    
    print("\n" + "=" * 50)
    
    # Test website import
    website_id = test_website_import()
    
    # Test transcript addition
    transcript_id = test_transcript_add()
    
    # Test search functionality
    test_document_search()
    
    # Test getting documents by type
    test_get_documents_by_type()
    
    print("\n" + "=" * 50)
    print("🎉 API Test Suite Completed!")
    
    if website_id and transcript_id:
        print(f"✅ Created website document: {website_id}")
        print(f"✅ Created transcript document: {transcript_id}")
        print("\nYou can now test the frontend ContentImporter component!")
    else:
        print("❌ Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()


