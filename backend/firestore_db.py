from google.cloud import firestore
from typing import List, Dict, Optional
import os

class FirestoreDB:
    def __init__(self, database_name: str = "(default)"):
        self.db = firestore.Client(database=database_name)
        self.media_collection = self.db.collection('media_items')
        self.links_collection = self.db.collection('media_links')
    
    def add_media_item(self, gcs_path: str, metadata: Dict = None) -> str:
        """Add a new media item to Firestore."""
        doc_ref = self.media_collection.document()
        doc_data = {
            'gcs_path': gcs_path,
            'metadata': metadata or {},
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP
        }
        doc_ref.set(doc_data)
        return doc_ref.id
    
    def get_media_item(self, doc_id: str) -> Optional[Dict]:
        """Get a media item by document ID."""
        doc = self.media_collection.document(doc_id).get()
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            data['contexts'] = self.get_contexts(doc.id)
            return data
        return None
    
    def get_media_by_gcs_path(self, gcs_path: str) -> Optional[Dict]:
        """Get a media item by GCS path."""
        docs = self.media_collection.where('gcs_path', '==', gcs_path).limit(1).stream()
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            data['contexts'] = self.get_contexts(doc.id)
            return data
        return None
    
    def list_media_items(self) -> List[Dict]:
        """List all media items."""
        docs = self.media_collection.stream()
        items = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            # To keep list view fast, we don't fetch all contexts here.
            # They will be fetched on demand when a single item is viewed.
            items.append(data)
        return items
    
    def update_media_item(self, doc_id: str, description: str = None, metadata: Dict = None) -> bool:
        """Update a media item."""
        doc_ref = self.media_collection.document(doc_id)
        update_data = {'updated_at': firestore.SERVER_TIMESTAMP}
        
        if description is not None:
            update_data['description'] = description
        if metadata is not None:
            update_data['metadata'] = metadata
        
        doc_ref.update(update_data)
        return True
    
    def add_media_link(self, source_id: str, target_id: str, link_type: str = "related") -> str:
        """Add a link between two media items."""
        doc_ref = self.links_collection.document()
        doc_data = {
            'source_id': source_id,
            'target_id': target_id,
            'link_type': link_type,
            'created_at': firestore.SERVER_TIMESTAMP
        }
        doc_ref.set(doc_data)
        return doc_ref.id
    
    def get_media_links(self, media_id: str) -> List[Dict]:
        """Get all links for a media item."""
        links = []
        
        # Get links where this item is the source
        source_docs = self.links_collection.where('source_id', '==', media_id).stream()
        for doc in source_docs:
            data = doc.to_dict()
            data['id'] = doc.id
            data['direction'] = 'outgoing'
            links.append(data)
        
        # Get links where this item is the target
        target_docs = self.links_collection.where('target_id', '==', media_id).stream()
        for doc in target_docs:
            data = doc.to_dict()
            data['id'] = doc.id
            data['direction'] = 'incoming'
            links.append(data)
        
        return links
    
    def add_context(self, media_id: str, text: str, context_type: str = 'description') -> str:
        """Add a context document to a media item's subcollection."""
        context_collection = self.media_collection.document(media_id).collection('contexts')
        doc_ref = context_collection.document()
        doc_data = {
            'text': text,
            'type': context_type,
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP
        }
        doc_ref.set(doc_data)
        return doc_ref.id

    def get_contexts(self, media_id: str) -> List[Dict]:
        """Get all context documents for a media item."""
        context_collection = self.media_collection.document(media_id).collection('contexts')
        docs = context_collection.order_by('created_at').stream()
        contexts = []
        for doc in docs:
            context_data = doc.to_dict()
            context_data['id'] = doc.id
            contexts.append(context_data)
        return contexts

    def update_context(self, media_id: str, context_id: str, text: str) -> bool:
        """Update a specific context document."""
        context_ref = self.media_collection.document(media_id).collection('contexts').document(context_id)
        context_ref.update({
            'text': text,
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        return True

    def delete_context(self, media_id: str, context_id: str) -> bool:
        """Delete a specific context document."""
        context_ref = self.media_collection.document(media_id).collection('contexts').document(context_id)
        context_ref.delete()
        return True
    
    def sync_gcs_files(self, gcs_files: List[str]) -> List[Dict]:
        """Sync GCS files with Firestore, adding new ones that don't exist."""
        existing_items = self.list_media_items()
        existing_paths = {item['gcs_path'] for item in existing_items}
        
        new_items = []
        for gcs_path in gcs_files:
            if gcs_path not in existing_paths:
                doc_id = self.add_media_item(gcs_path)
                new_items.append({'id': doc_id, 'gcs_path': gcs_path})
        
        return new_items 