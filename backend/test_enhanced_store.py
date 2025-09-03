#!/usr/bin/env python3
"""
Test script for the Enhanced Data Store
Run this to verify everything is working locally
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from enhanced_data_store import EnhancedDataStore

def test_basic_operations():
    """Test basic CRUD operations."""
    print("🧪 Testing Enhanced Data Store...")
    
    try:
        store = EnhancedDataStore()
        print("✅ Database connection successful!")
        
        # Test adding a document
        print("\n📝 Testing document creation...")
        doc_id = store.add_document(
            doc_type="test",
            title="Test Document",
            content="This is a test document to verify the enhanced data store is working correctly.",
            metadata={
                "tags": ["test", "verification"],
                "author": "Test User",
                "category": "testing"
            }
        )
        print(f"✅ Document created with ID: {doc_id}")
        
        # Test retrieving the document
        print("\n🔍 Testing document retrieval...")
        doc = store.get_document(doc_id)
        if doc:
            print(f"✅ Document retrieved: {doc['title']}")
            print(f"   Content: {doc['content'][:50]}...")
            print(f"   Metadata: {doc['metadata']}")
        else:
            print("❌ Failed to retrieve document")
            return False
        
        # Test updating the document
        print("\n✏️  Testing document update...")
        success = store.update_document(
            doc_id,
            title="Updated Test Document",
            metadata={"tags": ["test", "verification", "updated"]}
        )
        if success:
            print("✅ Document updated successfully")
            
            # Verify the update
            updated_doc = store.get_document(doc_id)
            print(f"   New title: {updated_doc['title']}")
            print(f"   New tags: {updated_doc['metadata']['tags']}")
        else:
            print("❌ Failed to update document")
            return False
        
        # Test search functionality
        print("\n🔎 Testing search functionality...")
        search_results = store.search_documents("test document", limit=5)
        if search_results:
            print(f"✅ Search returned {len(search_results)} results")
            for result in search_results:
                print(f"   - {result['title']} (score: {result.get('similarity_score', 'N/A')})")
        else:
            print("❌ Search returned no results")
            return False
        
        # Test document deletion
        print("\n🗑️  Testing document deletion...")
        success = store.delete_document(doc_id)
        if success:
            print("✅ Document deleted successfully")
        else:
            print("❌ Failed to delete document")
            return False
        
        # Verify deletion
        deleted_doc = store.get_document(doc_id)
        if deleted_doc is None:
            print("✅ Document deletion verified")
        else:
            print("❌ Document still exists after deletion")
            return False
        
        store.close()
        print("\n🎉 All tests passed! Enhanced Data Store is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_interview_functionality():
    """Test interview-specific functionality."""
    print("\n🎤 Testing interview functionality...")
    
    try:
        store = EnhancedDataStore()
        
        # Test adding interview transcript
        interview_id = store.add_interview_transcript(
            title="Test Interview with John Doe",
            content="""
            Interviewer: Tell me about this photo.
            John: This was taken during our trip to Paris in 2022. We were at the Eiffel Tower.
            Interviewer: What was the weather like?
            John: It was a beautiful sunny day in May. The sky was clear blue.
            Interviewer: Who else was with you?
            John: My wife Sarah and our daughter Emma were there too.
            """,
            metadata={
                "people": ["John Doe", "Sarah Doe", "Emma Doe"],
                "locations": ["Paris", "Eiffel Tower"],
                "date": "2022-05-15",
                "tags": ["Paris", "Eiffel Tower", "family", "vacation"]
            }
        )
        print(f"✅ Interview transcript created: {interview_id}")
        
        # Test searching for people
        people_results = store.search_documents("John Doe Sarah Emma", doc_type="interview")
        print(f"✅ People search returned {len(people_results)} results")
        
        # Test searching for locations
        location_results = store.search_documents("Paris Eiffel Tower", doc_type="interview")
        print(f"✅ Location search returned {len(location_results)} results")
        
        # Clean up
        store.delete_document(interview_id)
        store.close()
        print("✅ Interview functionality test completed")
        return True
        
    except Exception as e:
        print(f"❌ Interview test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Enhanced Data Store Test Suite")
    print("=" * 50)
    
    # Run basic tests
    basic_success = test_basic_operations()
    
    # Run interview tests
    interview_success = test_interview_functionality()
    
    print("\n" + "=" * 50)
    if basic_success and interview_success:
        print("🎉 ALL TESTS PASSED!")
        print("Your enhanced data store is ready for production use.")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please check the error messages above and fix any issues.")
    
    print("\nTo use the enhanced data store in your application:")
    print("1. Import: from app.enhanced_data_store import EnhancedDataStore")
    print("2. Initialize: store = EnhancedDataStore()")
    print("3. Use methods: store.add_document(), store.search_documents(), etc.")
    print("4. Close: store.close()")


