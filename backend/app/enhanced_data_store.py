import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
import psycopg2
from psycopg2.extras import RealDictCursor
import chromadb
from chromadb.config import Settings
import json
from dotenv import load_dotenv

load_dotenv()

class EnhancedDataStore:
    def __init__(self):
        # PostgreSQL connection parameters
        self.db_params = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'database': os.getenv('POSTGRES_DB', 'photo_tales'),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'password'),
            'port': os.getenv('POSTGRES_PORT', '5432')
        }
        
        # Create initial connection for schema initialization
        self.pg_conn = psycopg2.connect(**self.db_params)
        
        # ChromaDB client with telemetry completely disabled
        os.environ['CHROMA_TELEMETRY_ENABLED'] = 'false'
        
        self.chroma_client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize collections
        self.documents_collection = self.chroma_client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize database schema
        self._init_schema()
    
    def _init_schema(self):
        """Initialize PostgreSQL database schema."""
        with self.pg_conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id UUID PRIMARY KEY,
                    type VARCHAR(50) NOT NULL,
                    title VARCHAR(500) NOT NULL,
                    content TEXT NOT NULL,
                    metadata JSONB NOT NULL,
                    source VARCHAR(500),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_relations (
                    id UUID PRIMARY KEY,
                    source_doc_id UUID REFERENCES documents(id),
                    target_doc_id UUID REFERENCES documents(id),
                    relation_type VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS embeddings (
                    id UUID PRIMARY KEY,
                    document_id UUID REFERENCES documents(id),
                    embedding_vector JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_metadata ON documents USING GIN(metadata)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at)")
            
        self.pg_conn.commit()
        
        # Initialize media schema as well
        self._init_media_schema()
    
    def _get_connection(self):
        """Get a fresh database connection."""
        try:
            return psycopg2.connect(**self.db_params)
        except Exception as e:
            print(f"Failed to create database connection: {e}")
            raise
    
    def _init_media_schema(self):
        """Initialize PostgreSQL media schema."""
        with self.pg_conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS media (
                    id UUID PRIMARY KEY,
                    document_id UUID REFERENCES documents(id),
                    file_path VARCHAR(500) NOT NULL,
                    file_type VARCHAR(50) NOT NULL,
                    title VARCHAR(500),
                    summary TEXT,
                    tags JSONB DEFAULT '[]',
                    metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Make document_id nullable if it's not already
            try:
                cursor.execute("ALTER TABLE media ALTER COLUMN document_id DROP NOT NULL")
                self.pg_conn.commit()
            except Exception as e:
                # Column might already be nullable or not exist
                self.pg_conn.rollback()
                pass
            
            # Add missing columns if they don't exist (for existing tables)
            columns_to_add = [
                ("ALTER TABLE media ADD COLUMN title VARCHAR(500)", "title"),
                ("ALTER TABLE media ADD COLUMN summary TEXT", "summary"),
                ("ALTER TABLE media ADD COLUMN tags JSONB DEFAULT '[]'", "tags")
            ]
            
            for alter_sql, column_name in columns_to_add:
                try:
                    cursor.execute(alter_sql)
                    self.pg_conn.commit()
                    print(f"Added column {column_name} to media table")
                except Exception as e:
                    self.pg_conn.rollback()
                    # Column already exists or other error, continue
                    pass
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contexts (
                    id UUID PRIMARY KEY,
                    media_id UUID REFERENCES media(id),
                    text TEXT NOT NULL,
                    context_type VARCHAR(100) DEFAULT 'description',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS media_embeddings (
                    id UUID PRIMARY KEY,
                    media_id UUID REFERENCES media(id),
                    embedding_vector JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_document_id ON media(document_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_file_path ON media(file_path)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_file_type ON media(file_type)")
            
            # Create metadata index only if the column exists
            try:
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_metadata ON media USING GIN(metadata)")
            except:
                pass  # Column might not exist yet
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_contexts_media_id ON contexts(media_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_embeddings_vector ON media_embeddings USING GIN(embedding_vector)")
            
        self.pg_conn.commit()
    
    def add_document(self, doc_type: str, title: str, content: str, 
                    metadata: Dict[str, Any], source: str = None) -> str:
        """Add a new document to both PostgreSQL and ChromaDB."""
        doc_id = str(uuid.uuid4())
        
        # Add to PostgreSQL
        with self.pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                INSERT INTO documents (id, type, title, content, metadata, source)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (doc_id, doc_type, title, content, json.dumps(metadata), source))
            
            # Add to ChromaDB for vector search
            # Filter out None values from metadata for ChromaDB compatibility
            clean_metadata = {k: v for k, v in metadata.items() if v is not None}
            
            # Prepare ChromaDB metadata, ensuring no None values
            chroma_metadata = {
                "id": doc_id,
                "type": doc_type,
                "title": title,
                **clean_metadata
            }
            
            # Only add source if it's not None
            if source is not None:
                chroma_metadata["source"] = source
            
            self.documents_collection.add(
                documents=[content],
                metadatas=[chroma_metadata],
                ids=[doc_id]
            )
        
        self.pg_conn.commit()
        return doc_id
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a document by ID."""
        with self.pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM documents WHERE id = %s
            """, (doc_id,))
            
            result = cursor.fetchone()
            if result:
                doc = dict(result)
                doc['metadata'] = json.loads(doc['metadata'])
                return doc
        return None
    
    def search_documents(self, query: str, doc_type: str = None, 
                        limit: int = 10) -> List[Dict[str, Any]]:
        """Search documents using semantic similarity."""
        # Search in ChromaDB
        results = self.documents_collection.query(
            query_texts=[query],
            n_results=limit,
            where={"type": doc_type} if doc_type else None
        )
        
        # Get full documents from PostgreSQL
        if results['ids'] and results['ids'][0]:
            doc_ids = results['ids'][0]
            documents = []
            
            with self.pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
                for doc_id in doc_ids:
                    cursor.execute("""
                        SELECT * FROM documents WHERE id = %s
                    """, (doc_id,))
                    
                    result = cursor.fetchone()
                    if result:
                        doc = dict(result)
                        doc['metadata'] = json.loads(doc['metadata'])
                        doc['similarity_score'] = results['distances'][0][doc_ids.index(doc_id)]
                        documents.append(doc)
            
            return documents
        return []
    
    def update_document(self, doc_id: str, title: str = None, content: str = None,
                       metadata: Dict[str, Any] = None) -> bool:
        """Update an existing document."""
        updates = []
        values = []
        
        if title is not None:
            updates.append("title = %s")
            values.append(title)
        
        if content is not None:
            updates.append("content = %s")
            values.append(content)
        
        if metadata is not None:
            updates.append("metadata = %s")
            values.append(json.dumps(metadata))
        
        if not updates:
            return False
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(doc_id)
        
        with self.pg_conn.cursor() as cursor:
            cursor.execute(f"""
                UPDATE documents 
                SET {', '.join(updates)}
                WHERE id = %s
            """, values)
            
            # Update in ChromaDB if content changed
            if content is not None:
                self.documents_collection.update(
                    ids=[doc_id],
                    documents=[content],
                    metadatas=[{
                        "id": doc_id,
                        "updated_at": datetime.now().isoformat()
                    }]
                )
        
        self.pg_conn.commit()
        return True
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document and its embeddings."""
        try:
            # Delete from ChromaDB
            self.documents_collection.delete(ids=[doc_id])
            
            # Delete from PostgreSQL
            with self.pg_conn.cursor() as cursor:
                cursor.execute("DELETE FROM documents WHERE id = %s", (doc_id,))
            
            self.pg_conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    def add_interview_transcript(self, title: str, content: str, 
                               metadata: Dict[str, Any]) -> str:
        """Add an interview transcript with enhanced metadata."""
        # Filter out None values from metadata for ChromaDB compatibility
        clean_metadata = {k: v for k, v in metadata.items() if v is not None}
        
        enhanced_metadata = {
            **clean_metadata,
            "word_count": len(content.split()),
            "has_people": bool(clean_metadata.get('people')),
            "has_locations": bool(clean_metadata.get('locations')),
            "interview_date": clean_metadata.get('date', datetime.now().isoformat())
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
        # Filter out None values from metadata for ChromaDB compatibility
        clean_metadata = {k: v for k, v in metadata.items() if v is not None}
        
        enhanced_metadata = {
            **clean_metadata,
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
        with self.pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM documents 
                WHERE type = %s 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (doc_type, limit))
            
            results = cursor.fetchall()
            documents = []
            for result in results:
                doc = dict(result)
                doc['metadata'] = json.loads(doc['metadata'])
                documents.append(doc)
            
            return documents
    
    def get_related_documents(self, doc_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get semantically related documents."""
        # Get the current document
        current_doc = self.get_document(doc_id)
        if not current_doc:
            return []
        
        # Search for similar documents
        similar_docs = self.search_documents(
            current_doc['content'][:500],  # Use first 500 chars for similarity
            limit=limit + 1  # +1 to exclude self
        )
        
        # Filter out the current document
        related = [doc for doc in similar_docs if doc['id'] != doc_id]
        return related[:limit]
    
    def add_document_relation(self, source_doc_id: str, target_doc_id: str, 
                             relation_type: str = "related") -> str:
        """Create a relationship between two documents."""
        relation_id = str(uuid.uuid4())
        
        with self.pg_conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO document_relations (id, source_doc_id, target_doc_id, relation_type)
                VALUES (%s, %s, %s, %s)
            """, (relation_id, source_doc_id, target_doc_id, relation_type))
        
        self.pg_conn.commit()
        return relation_id
    
    def get_document_relations(self, doc_id: str) -> List[Dict[str, Any]]:
        """Get all relations for a document."""
        with self.pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM document_relations 
                WHERE source_doc_id = %s OR target_doc_id = %s
            """, (doc_id, doc_id))
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
    
    # Media-related methods
    def add_media_item(self, file_path: str, metadata: Optional[Dict] = None) -> str:
        """Add a new media item."""
        media_id = str(uuid.uuid4())
        
        # Ensure metadata is always a dict, never None
        if metadata is None:
            metadata = {}
        
        # Extract title, summary, and tags from metadata
        title = metadata.get('title', None)
        summary = metadata.get('summary', None)
        tags = metadata.get('tags', [])
        
        with self.pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                INSERT INTO media (id, file_path, file_type, title, summary, tags, metadata, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (media_id, file_path, 'image', title, summary, json.dumps(tags), json.dumps(metadata), datetime.now()))
        
        self.pg_conn.commit()
        return media_id
    
    def get_media_item(self, doc_id: str) -> Optional[Dict]:
        """Get a media item by ID."""
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM media WHERE id = %s
                """, (doc_id,))
                
                result = cursor.fetchone()
                return dict(result) if result else None
        finally:
            conn.close()
    
    def get_media_by_file_path(self, file_path: str) -> Optional[Dict]:
        """Get a media item by file path."""
        with self.pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM media WHERE file_path = %s
            """, (file_path,))
            
            result = cursor.fetchone()
            return dict(result) if result else None
    
    def list_media_items(self) -> List[Dict]:
        """List all media items."""
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM media ORDER BY created_at DESC
                """)
                
                results = cursor.fetchall()
                return [dict(row) for row in results]
        finally:
            conn.close()
    
    def update_media_item(self, doc_id: str, title: Optional[str] = None, 
                         summary: Optional[str] = None, tags: Optional[List[str]] = None, 
                         metadata: Optional[Dict] = None) -> bool:
        """Update a media item."""
        try:
            with self.pg_conn.cursor() as cursor:
                # Build dynamic update query based on provided fields
                update_fields = []
                update_values = []
                
                if title is not None:
                    update_fields.append("title = %s")
                    update_values.append(title)
                
                if summary is not None:
                    update_fields.append("summary = %s")
                    update_values.append(summary)
                
                if tags is not None:
                    update_fields.append("tags = %s")
                    update_values.append(json.dumps(tags))
                
                if metadata is not None:
                    update_fields.append("metadata = %s")
                    update_values.append(json.dumps(metadata))
                
                if not update_fields:
                    return True  # Nothing to update
                
                # Add the doc_id for the WHERE clause
                update_values.append(doc_id)
                
                query = f"""
                    UPDATE media SET {', '.join(update_fields)} 
                    WHERE id = %s
                """
                
                cursor.execute(query, update_values)
            
            self.pg_conn.commit()
            return True
        except Exception as e:
            print(f"Error updating media item: {e}")
            self.pg_conn.rollback()
            return False
    
    def delete_media_item(self, doc_id: str) -> bool:
        """Delete a media item."""
        try:
            with self.pg_conn.cursor() as cursor:
                cursor.execute("DELETE FROM media WHERE id = %s", (doc_id,))
            
            self.pg_conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting media item: {e}")
            return False
    
    def add_context(self, media_id: str, text: str, context_type: str = 'description') -> str:
        """Add context to a media item."""
        context_id = str(uuid.uuid4())
        
        with self.pg_conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO contexts (id, media_id, text, context_type, created_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (context_id, media_id, text, context_type, datetime.now()))
        
        self.pg_conn.commit()
        return context_id
    
    def get_contexts(self, media_id: str) -> List[Dict]:
        """Get all contexts for a media item."""
        with self.pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM contexts WHERE media_id = %s ORDER BY created_at DESC
            """, (media_id,))
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
    
    def update_context(self, context_id: str, text: str) -> bool:
        """Update a context."""
        try:
            with self.pg_conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE contexts SET text = %s WHERE id = %s
                """, (text, context_id))
            
            self.pg_conn.commit()
            return True
        except Exception as e:
            print(f"Error updating context: {e}")
            return False
    
    def delete_context(self, context_id: str) -> bool:
        """Delete a context."""
        try:
            with self.pg_conn.cursor() as cursor:
                cursor.execute("DELETE FROM contexts WHERE id = %s", (context_id,))
            
            self.pg_conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting context: {e}")
            return False
    
    def sync_gcs_files(self, gcs_files: List[str]) -> List[Dict]:
        """Sync GCS files with local database (placeholder for now)."""
        # This is a placeholder - you can implement actual GCS sync logic here
        return []
    
    def close(self):
        """Close database connections."""
        if self.pg_conn:
            self.pg_conn.close()

