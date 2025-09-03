#!/usr/bin/env python3
"""
Test script for the Simple Data Store (SQLite version)
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

from simple_data_store import SimpleDataStore

def test_basic_operations():
    """Test basic CRUD operations."""
    print("🧪 Testing Simple Data Store...")
    
    try:
        store = SimpleDataStore()
        print("✅ Database connection successful!")
        
        # Test adding a document
        print("\n📝 Testing document creation...")
        doc_id = store.add_document(
            doc_type="test",
            title="Test Document",
            content="This is a test document to verify the simple data store is working correctly.",
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
                print(f"   - {result['title']}")
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
        print("\n🎉 All tests passed! Simple Data Store is working correctly.")
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
        store = SimpleDataStore()
        
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
        people_results = store.search_documents("John Doe", doc_type="interview")
        print(f"✅ People search returned {len(people_results)} results")
        
        # Test searching for locations
        location_results = store.search_documents("Paris", doc_type="interview")
        print(f"✅ Location search returned {len(location_results)} results")
        
        # Test getting documents by type
        interviews = store.get_documents_by_type("interview")
        print(f"✅ Found {len(interviews)} interview documents")
        
        # Clean up
        store.delete_document(interview_id)
        store.close()
        print("✅ Interview functionality test completed")
        return True
        
    except Exception as e:
        print(f"❌ Interview test failed: {e}")
        return False

def insert_sample_data():
    """Insert sample data for demonstration."""
    print("\n📚 Inserting sample data...")
    
    try:
        store = SimpleDataStore()
        
        # Sample interview transcript
        interview_id = store.add_interview_transcript(
            title="Paris Vacation Interview - John and Sarah",
            content="""
            Interviewer: Tell me about this photo from your Paris trip.
            
            John: This was taken in May 2022 during our family vacation to Paris. We were standing in front of the Eiffel Tower, and it was our first time visiting the city. The weather was absolutely perfect - sunny and warm, about 22 degrees Celsius.
            
            Interviewer: What was the most memorable part of that day?
            
            Sarah: For me, it was watching Emma's face light up when she first saw the Eiffel Tower. She was only 8 years old at the time, and she had been talking about seeing it for months. When we finally got there, she was speechless for a moment, then started jumping up and down with excitement.
            
            John: I remember the crowds were quite large, but we managed to find a good spot for photos. We took about 50 pictures that day! The architecture was incredible - much more impressive in person than in photos.
            
            Interviewer: Did you go up the tower?
            
            Sarah: Yes! We took the elevator to the second floor. Emma was a bit nervous about the height at first, but once we were up there, she loved looking out over the city. We could see the Seine River, Notre Dame, and all the beautiful Haussmann buildings.
            
            John: The view was breathtaking. We spent about an hour up there, just taking in the panorama. It was worth every euro of the ticket price.
            
            Interviewer: What did you do after visiting the tower?
            
            Sarah: We walked along the Seine to the Trocadéro area and had lunch at a small café. We tried our first authentic French croissants and café au lait. Emma loved the chocolate croissant so much that we went back the next day for another one!
            
            John: That afternoon, we visited the Musée d'Orsay. Sarah is an art teacher, so she was particularly excited about seeing the Impressionist collection. We saw works by Monet, Van Gogh, and Degas. Emma was surprisingly engaged with the art, asking lots of questions about the paintings.
            """,
            metadata={
                "people": ["John", "Sarah", "Emma"],
                "locations": ["Paris", "Eiffel Tower", "Seine River", "Trocadéro", "Musée d'Orsay"],
                "date": "2022-05-15",
                "tags": ["Paris", "Eiffel Tower", "family", "vacation", "art", "museum", "croissants"]
            }
        )
        
        # Sample website content
        website_id = store.add_website_content(
            title="Paris Travel Guide - Best Family Activities",
            content="""
            Paris is one of the world's most family-friendly cities, offering countless activities that both children and adults will enjoy. Here are some of the best family activities in the City of Light:
            
            **Eiffel Tower Experience**
            The Eiffel Tower is a must-visit for families. Children under 4 enter free, and there are special family packages available. The second floor offers the best balance of views and accessibility for families with young children.
            
            **Seine River Cruise**
            A boat cruise along the Seine is perfect for families. Many companies offer family-friendly tours with audio guides in multiple languages. The cruise provides a unique perspective of Paris's most famous landmarks.
            
            **Jardin du Luxembourg**
            This beautiful park is perfect for families. Children can sail boats in the central pond, play in the playground, or enjoy puppet shows. The park also has pony rides and a carousel.
            
            **Musée d'Orsay**
            This museum is more family-friendly than the Louvre, with shorter lines and a more manageable size. The Impressionist collection is particularly engaging for children, with its bright colors and recognizable subjects.
            
            **Disneyland Paris**
            Located just outside the city, Disneyland Paris offers a full day of family fun. The park combines classic Disney attractions with French flair, making it a unique experience.
            
            **Tips for Families:**
            - Purchase a Paris Pass for discounted entry to many attractions
            - Book restaurant reservations in advance, especially for dinner
            - Use the metro system - it's efficient and children under 4 ride free
            - Pack comfortable walking shoes - Paris is best explored on foot
            """,
            url="https://example.com/paris-family-guide",
            metadata={
                "tags": ["Paris", "family travel", "Eiffel Tower", "museums", "travel guide"],
                "content_type": "travel guide",
                "target_audience": "families with children"
            }
        )
        
        # Sample note/document
        note_id = store.add_document(
            doc_type="note",
            title="Paris Trip Planning Notes",
            content="""
            **Paris Trip Planning - May 2022**
            
            **Accommodation:**
            - Hotel: Hotel des Grands Boulevards (3 nights)
            - Location: 2nd arrondissement, near metro stations
            - Family room with separate sleeping area for Emma
            
            **Itinerary:**
            Day 1: Arrival, check-in, dinner near hotel
            Day 2: Eiffel Tower, Seine cruise, Trocadéro
            Day 3: Musée d'Orsay, Jardin du Luxembourg, shopping
            Day 4: Notre Dame area, Latin Quarter, departure
            
            **Restaurant Reservations:**
            - Le Comptoir du Relais (traditional French)
            - L'As du Fallafel (casual, kid-friendly)
            - Café de Flore (historic café experience)
            
            **Budget:**
            - Hotel: €450 (3 nights)
            - Meals: €300
            - Attractions: €200
            - Transportation: €100
            - Total: €1,050
            
            **Packing List:**
            - Comfortable walking shoes
            - Light jacket (May weather can be variable)
            - Camera and extra batteries
            - Travel adapter for electronics
            - Small backpack for day trips
            
            **Emergency Contacts:**
            - Hotel: +33 1 42 36 00 00
            - US Embassy: +33 1 43 12 22 22
            - Emergency: 112
            """,
            metadata={
                "tags": ["Paris", "travel planning", "itinerary", "budget", "family"],
                "trip_date": "2022-05-15",
                "travelers": ["John", "Sarah", "Emma"]
            }
        )
        
        print(f"✅ Sample data inserted:")
        print(f"   - Interview: {interview_id}")
        print(f"   - Website: {website_id}")
        print(f"   - Note: {note_id}")
        
        # Test search functionality with sample data
        print("\n🔍 Testing search with sample data...")
        
        # Search for Paris-related content
        paris_results = store.search_documents("Paris")
        print(f"✅ Found {len(paris_results)} documents about Paris")
        
        # Search for family-related content
        family_results = store.search_documents("family")
        print(f"✅ Found {len(family_results)} documents about family")
        
        # Get all interviews
        interviews = store.get_documents_by_type("interview")
        print(f"✅ Found {len(interviews)} interview documents")
        
        # Get all website content
        websites = store.get_documents_by_type("website")
        print(f"✅ Found {len(websites)} website documents")
        
        store.close()
        print("✅ Sample data insertion completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Sample data insertion failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Simple Data Store Test Suite")
    print("=" * 50)
    
    # Run basic tests
    basic_success = test_basic_operations()
    
    # Run interview tests
    interview_success = test_interview_functionality()
    
    # Insert sample data
    sample_success = insert_sample_data()
    
    print("\n" + "=" * 50)
    if basic_success and interview_success and sample_success:
        print("🎉 ALL TESTS PASSED!")
        print("Your simple data store is ready with sample data!")
        print("\nSample data includes:")
        print("- Paris vacation interview transcript")
        print("- Paris travel guide website content")
        print("- Paris trip planning notes")
        print("\nYou can now test search functionality with queries like:")
        print("- 'Paris'")
        print("- 'family'")
        print("- 'Eiffel Tower'")
        print("- 'museum'")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please check the error messages above and fix any issues.")
    
    print("\nTo use the simple data store in your application:")
    print("1. Import: from app.simple_data_store import SimpleDataStore")
    print("2. Initialize: store = SimpleDataStore()")
    print("3. Use methods: store.add_document(), store.search_documents(), etc.")
    print("4. Close: store.close()")


