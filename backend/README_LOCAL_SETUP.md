# Photo Tales - Local Development Setup

This guide will help you set up and run the Photo Tales application locally with the new enhanced data storage system.

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** - For running PostgreSQL locally
- **Python 3.8+** - For the Flask backend
- **OpenAI API Key** - For AI features

### 1. One-Command Setup

```bash
cd backend
chmod +x setup_local.sh
./setup_local.sh
```

This script will:
- Start PostgreSQL and pgAdmin with Docker
- Create a Python virtual environment
- Install all dependencies
- Create configuration files
- Test the database connection

### 2. Start the Application

```bash
chmod +x start_local.sh
./start_local.sh
```

## 🗄️ What's Running Locally

### PostgreSQL Database
- **Host**: `localhost:5432`
- **Database**: `photo_tales`
- **User**: `postgres`
- **Password**: `password`

### pgAdmin (Database Management)
- **URL**: http://localhost:5050
- **Email**: `admin@phototales.com`
- **Password**: `admin`

### ChromaDB (Vector Database)
- **Location**: `./chroma_db/` (local directory)
- **Purpose**: Semantic search and RAG functionality

## 🔧 Manual Setup (Alternative)

If you prefer to set up manually:

### 1. Start Databases

```bash
docker-compose up -d
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp config.env.example config.env
# Edit config.env and add your OpenAI API key
```

### 5. Test the Setup

```bash
python test_enhanced_store.py
```

## 📊 Database Schema

The enhanced data store creates these tables:

### `documents`
- `id` - UUID primary key
- `type` - Document type (interview, website, media, note)
- `title` - Document title
- `content` - Full document content (supports long text)
- `metadata` - JSONB field for flexible metadata
- `source` - Source of the document
- `created_at` / `updated_at` - Timestamps

### `document_relations`
- Links between related documents
- Supports different relationship types

### `embeddings`
- Vector embeddings for semantic search

## 🎯 Key Features

### 1. **Long Document Support**
- No text length limits
- Efficient storage with PostgreSQL TEXT fields
- Metadata stored as JSONB for flexibility

### 2. **Easy Updates**
- Simple CRUD operations
- Automatic timestamp updates
- Batch operations support

### 3. **RAG LLM Ready**
- Vector embeddings with ChromaDB
- Semantic similarity search
- Metadata filtering
- Relationship tracking between documents

## 📝 Usage Examples

### Adding an Interview Transcript

```python
from app.enhanced_data_store import EnhancedDataStore

store = EnhancedDataStore()

interview_id = store.add_interview_transcript(
    title="Interview with John about Paris Trip",
    content="Full interview transcript here...",
    metadata={
        "people": ["John Doe", "Sarah Doe"],
        "locations": ["Paris", "Eiffel Tower"],
        "date": "2022-05-15",
        "tags": ["vacation", "family", "Paris"]
    }
)
```

### Searching Documents

```python
# Semantic search
results = store.search_documents("Paris vacation with family")

# Filter by type
interviews = store.get_documents_by_type("interview")

# Get related documents
related = store.get_related_documents(interview_id)
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_enhanced_store.py
```

This tests:
- Basic CRUD operations
- Interview functionality
- Search capabilities
- Document relationships

## 🔍 Troubleshooting

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Restart the database
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

### Python Dependencies
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version
python --version  # Should be 3.8+
```

### ChromaDB Issues
```bash
# Clear ChromaDB data
rm -rf ./chroma_db/

# Restart the application
```

## 🚀 Production Considerations

When moving to production:

1. **Use managed PostgreSQL** (AWS RDS, Google Cloud SQL, etc.)
2. **Use managed ChromaDB** or self-hosted with proper backups
3. **Set up proper authentication** and connection pooling
4. **Configure environment variables** for production
5. **Set up monitoring** and logging

## 📚 API Integration

The enhanced data store can be easily integrated with your existing Flask routes:

```python
from app.enhanced_data_store import EnhancedDataStore

@app.route('/api/documents', methods=['POST'])
def add_document():
    data = request.get_json()
    store = EnhancedDataStore()
    
    doc_id = store.add_document(
        doc_type=data['type'],
        title=data['title'],
        content=data['content'],
        metadata=data.get('metadata', {})
    )
    
    store.close()
    return jsonify({"id": doc_id})
```

## 🤝 Support

If you encounter issues:

1. Check the test output: `python test_enhanced_store.py`
2. Verify database connectivity
3. Check environment variables in `config.env`
4. Review Docker logs: `docker-compose logs`

The enhanced data store is designed to be robust and easy to debug locally!


