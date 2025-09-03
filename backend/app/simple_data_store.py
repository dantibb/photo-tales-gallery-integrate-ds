import os
import uuid
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv

load_dotenv()

class SimpleDataStore:
    def __init__(self, db_path="photo_tales.db"):
        """Initialize with SQLite database."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Enable dict-like access
        self._init_schema()
    
    def _init_schema(self):
        """Initialize SQLite database schema."""
        cursor = self.conn.cursor()
        
        # Create documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT NOT NULL,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create document relations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_relations (
                id TEXT PRIMARY KEY,
                source_doc_id TEXT REFERENCES documents(id),
                target_doc_id TEXT REFERENCES documents(id),
                relation_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_source ON documents(source)")
        
        self.conn.commit()
    
    def add_document(self, doc_type: str, title: str, content: str, 
                    metadata: Dict[str, Any], source: str = None) -> str:
        """Add a new document."""
        doc_id = str(uuid.uuid4())
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO documents (id, type, title, content, metadata, source)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (doc_id, doc_type, title, content, json.dumps(metadata), source))
        
        self.conn.commit()
        return doc_id
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a document by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
        
        result = cursor.fetchone()
        if result:
            doc = dict(result)
            doc['metadata'] = json.loads(doc['metadata'])
            return doc
        return None
    
    def search_documents(self, query: str, doc_type: str = None, 
                        limit: int = 10) -> List[Dict[str, Any]]:
        """Search documents using text matching (simple version)."""
        cursor = self.conn.cursor()
        
        if doc_type:
            cursor.execute("""
                SELECT * FROM documents 
                WHERE type = ? AND (title LIKE ? OR content LIKE ?)
                ORDER BY created_at DESC 
                LIMIT ?
            """, (doc_type, f"%{query}%", f"%{query}%", limit))
        else:
            cursor.execute("""
                SELECT * FROM documents 
                WHERE title LIKE ? OR content LIKE ?
                ORDER BY created_at DESC 
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))
        
        results = cursor.fetchall()
        documents = []
        for result in results:
            doc = dict(result)
            doc['metadata'] = json.loads(doc['metadata'])
            documents.append(doc)
        
        return documents
    
    def update_document(self, doc_id: str, title: str = None, content: str = None,
                       metadata: Dict[str, Any] = None) -> bool:
        """Update an existing document."""
        updates = []
        values = []
        
        if title is not None:
            updates.append("title = ?")
            values.append(title)
        
        if content is not None:
            updates.append("content = ?")
            values.append(content)
        
        if metadata is not None:
            updates.append("metadata = ?")
            values.append(json.dumps(metadata))
        
        if not updates:
            return False
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(doc_id)
        
        cursor = self.conn.cursor()
        cursor.execute(f"""
            UPDATE documents 
            SET {', '.join(updates)}
            WHERE id = ?
        """, values)
        
        self.conn.commit()
        return True
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    def add_interview_transcript(self, title: str, content: str, 
                               metadata: Dict[str, Any]) -> str:
        """Add an interview transcript with enhanced metadata."""
        enhanced_metadata = {
            **metadata,
            "word_count": len(content.split()),
            "has_people": bool(metadata.get('people')),
            "has_locations": bool(metadata.get('locations')),
            "interview_date": metadata.get('date', datetime.now().isoformat())
        }
        
        return self.add_document(
            doc_type="interview",
            title=title,
            content=content,
            metadata=enhanced_metadata,
            source="interview_transcript"
        )
    
    def add_website_content(self, title: str, content: str, url: str,
                           metadata: Dict[str, Any]) -> str:
        """Add website content with URL tracking."""
        enhanced_metadata = {
            **metadata,
            "url": url,
            "content_type": "website",
            "scraped_at": datetime.now().isoformat()
        }
        
        return self.add_document(
            doc_type="website",
            title=title,
            content=content,
            metadata=enhanced_metadata,
            source=url
        )
    
    def get_documents_by_type(self, doc_type: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get documents of a specific type."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM documents 
            WHERE type = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (doc_type, limit))
        
        results = cursor.fetchall()
        documents = []
        for result in results:
            doc = dict(result)
            doc['metadata'] = json.loads(doc['metadata'])
            documents.append(doc)
        
        return documents
    
    def get_related_documents(self, doc_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get related documents based on shared metadata."""
        current_doc = self.get_document(doc_id)
        if not current_doc:
            return []
        
        # Find documents with similar tags or metadata
        current_metadata = current_doc['metadata']
        current_tags = current_metadata.get('tags', [])
        
        if not current_tags:
            return []
        
        # Search for documents with overlapping tags
        cursor = self.conn.cursor()
        related_docs = []
        
        for tag in current_tags[:3]:  # Use first 3 tags
            cursor.execute("""
                SELECT * FROM documents 
                WHERE id != ? AND metadata LIKE ?
                ORDER BY created_at DESC 
                LIMIT ?
            """, (doc_id, f"%{tag}%", limit))
            
            results = cursor.fetchall()
            for result in results:
                doc = dict(result)
                doc['metadata'] = json.loads(doc['metadata'])
                if doc not in related_docs:
                    related_docs.append(doc)
        
        return related_docs[:limit]
    
    def add_document_relation(self, source_doc_id: str, target_doc_id: str, 
                             relation_type: str = "related") -> str:
        """Create a relationship between two documents."""
        relation_id = str(uuid.uuid4())
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO document_relations (id, source_doc_id, target_doc_id, relation_type)
            VALUES (?, ?, ?, ?)
        """, (relation_id, source_doc_id, target_doc_id, relation_type))
        
        self.conn.commit()
        return relation_id
    
    def get_document_relations(self, doc_id: str) -> List[Dict[str, Any]]:
        """Get all relations for a document."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT r.*, 
                   d1.title as source_title, d1.type as source_type,
                   d2.title as target_title, d2.type as target_type
            FROM document_relations r
            JOIN documents d1 ON r.source_doc_id = d1.id
            JOIN documents d2 ON r.target_doc_id = d2.id
            WHERE r.source_doc_id = ? OR r.target_doc_id = ?
        """, (doc_id, doc_id))
        
        results = cursor.fetchall()
        relations = []
        for result in results:
            rel = dict(result)
            if rel['source_doc_id'] == doc_id:
                rel['related_doc'] = {
                    'id': rel['target_doc_id'],
                    'title': rel['target_title'],
                    'type': rel['target_type']
                }
                rel['direction'] = 'outgoing'
            else:
                rel['related_doc'] = {
                    'id': rel['source_doc_id'],
                    'title': rel['source_title'],
                    'type': rel['source_type']
                }
                rel['direction'] = 'incoming'
            
            relations.append(rel)
        
        return relations
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


