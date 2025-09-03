from flask import Blueprint, request, jsonify, current_app
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
from app.enhanced_data_store import EnhancedDataStore
import os
from datetime import datetime

# Create Blueprint for enhanced data store routes
enhanced_bp = Blueprint('enhanced', __name__)

@enhanced_bp.route('/api/documents', methods=['POST'])
def add_document():
    """Add a new document to the enhanced data store."""
    try:
        data = request.get_json()
        
        if not data or 'type' not in data or 'title' not in data or 'content' not in data:
            return jsonify({"error": "Missing required fields: type, title, content"}), 400
        
        store = EnhancedDataStore()
        
        # Add the document
        doc_id = store.add_document(
            doc_type=data['type'],
            title=data['title'],
            content=data['content'],
            metadata=data.get('metadata', {}),
            source=data.get('source')
        )
        
        return jsonify({
            "success": True,
            "id": doc_id,
            "message": f"Document '{data['title']}' added successfully"
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Failed to add document: {str(e)}"}), 500

@enhanced_bp.route('/api/documents/<doc_type>', methods=['GET'])
def get_documents_by_type(doc_type):
    """Get all documents of a specific type."""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        store = EnhancedDataStore()
        documents = store.get_documents_by_type(doc_type, limit=limit)
        
        return jsonify({
            "success": True,
            "documents": documents,
            "count": len(documents)
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve documents: {str(e)}"}), 500

@enhanced_bp.route('/api/documents/search', methods=['POST'])
def search_documents():
    """Search documents using text matching."""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({"error": "Missing query parameter"}), 400
        
        store = EnhancedDataStore()
        
        # Search with optional type filter
        doc_type = data.get('type')
        limit = data.get('limit', 10)
        
        results = store.search_documents(
            query=data['query'],
            doc_type=doc_type,
            limit=limit
        )
        
        return jsonify({
            "success": True,
            "results": results,
            "count": len(results),
            "query": data['query']
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Search failed: {str(e)}"}), 500

@enhanced_bp.route('/api/website/import', methods=['POST'])
def import_website():
    """Import content from a website URL."""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({"error": "Missing URL parameter"}), 400
        
        url = data['url']
        custom_title = data.get('title')
        
        # Validate URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return jsonify({"error": "Invalid URL format"}), 400
        
        # Fetch website content
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        if not custom_title:
            title_tag = soup.find('title')
            custom_title = title_tag.get_text().strip() if title_tag else f"Content from {parsed_url.netloc}"
        
        # Extract main content
        content = extract_main_content(soup)
        
        if not content or len(content.strip()) < 100:
            return jsonify({"error": "Could not extract sufficient content from website"}), 400
        
        # Extract metadata
        metadata = extract_website_metadata(soup, url)
        
        # Store in enhanced data store
        store = EnhancedDataStore()
        
        doc_id = store.add_website_content(
            title=custom_title,
            content=content,
            url=url,
            metadata=metadata
        )
        
        return jsonify({
            "success": True,
            "id": doc_id,
            "title": custom_title,
            "url": url,
            "content_length": len(content),
            "metadata": metadata,
            "message": f"Website content imported successfully from {url}"
        }), 201
        
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch website: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Import failed: {str(e)}"}), 500

@enhanced_bp.route('/api/content/test', methods=['GET'])
def test_content():
    """Simple test endpoint to verify content API is working."""
    return jsonify({
        "success": True,
        "message": "Content API is working!",
        "endpoints": {
            "add_content": "POST /api/content/add",
            "add_transcript": "POST /api/transcript/add",
            "add_document": "POST /api/documents"
        }
    }), 200

@enhanced_bp.route('/api/content/add', methods=['POST'])
def add_content():
    """Simple endpoint to add any type of content with automatic photocard creation for transcripts."""
    try:
        data = request.get_json()
        
        if not data or 'title' not in data or 'content' not in data:
            return jsonify({"error": "Missing required fields: title, content"}), 400
        
        store = EnhancedDataStore()
        
        # Determine content type from the request or default to 'document'
        content_type = data.get('type', 'document')
        
        # Ensure metadata is always a dict, never None
        metadata = data.get('metadata', {})
        if metadata is None:
            metadata = {}
            
        # Add the content using the general document method
        doc_id = store.add_document(
            doc_type=content_type,
            title=data['title'],
            content=data['content'],
            metadata=metadata,
            source=data.get('source')
        )
        
        # If this is a transcript, create a placeholder photocard
        if content_type == 'transcript':
            try:
                # Create a placeholder photocard
                photocard_id = store.add_media_item(
                    file_path=f"placeholder_transcript_{doc_id}.jpg",
                    metadata={
                        "type": "transcript_placeholder",
                        "document_id": doc_id,
                        "title": data['title'],
                        "description": f"Transcript: {data['title']}",
                        "is_placeholder": True,
                        "content_preview": data['content'][:100] + "..." if len(data['content']) > 100 else data['content']
                    }
                )
                
                # Link the photocard to the transcript
                store.add_document_relation(
                    source_doc_id=doc_id,
                    target_doc_id=photocard_id,
                    relation_type="has_photocard"
                )
                
                # Generate AI summary and tags for the transcript
                try:
                    from prompts import build_summary_prompt
                    from interviewer_bot import run_interview_chat, generate_image_tags
                    
                    # Generate AI summary
                    summary_prompt = build_summary_prompt([data['content']])
                    ai_summary_response, _ = run_interview_chat(summary_prompt, image_path=None)
                    
                    # Parse the summary response
                    lines = ai_summary_response.strip().split('\n')
                    summary_title = ""
                    summary_text = ""
                    
                    for line in lines:
                        if line.startswith('Title:'):
                            summary_title = line.replace('Title:', '').strip()
                        elif line.startswith('Summary:'):
                            summary_text = line.replace('Summary:', '').strip()
                    
                    # If parsing failed, use the whole response
                    if not summary_title or not summary_text:
                        summary_title = f"Transcript: {data['title']}"
                        summary_text = ai_summary_response.strip()
                    
                    # Generate AI tags
                    ai_tags = generate_image_tags(
                        image_path=None,  # No image for transcripts
                        context=data['content'],
                        summary=summary_text,
                        existing_tags=[]
                    )
                    
                    # Update the photocard with AI-generated summary and tags
                    store.update_media_item(
                        photocard_id,
                        title=summary_title,
                        summary=summary_text,
                        tags=ai_tags
                    )
                    
                    # Update the transcript document with the summary
                    store.update_document(
                        doc_id,
                        title=summary_title,
                        metadata={
                            **metadata,
                            "ai_summary": summary_text,
                            "ai_tags": ai_tags,
                            "summary_generated_at": datetime.now().isoformat()
                        }
                    )
                    
                    return jsonify({
                        "success": True,
                        "id": doc_id,
                        "type": content_type,
                        "photocard_id": photocard_id,
                        "ai_summary": {
                            "title": summary_title,
                            "summary": summary_text,
                            "tags": ai_tags
                        },
                        "message": f"Transcript '{data['title']}' added successfully with AI-generated summary and tags"
                    }), 201
                    
                except Exception as ai_error:
                    print(f"Warning: AI processing failed for transcript: {ai_error}")
                    # Return success even if AI processing fails
                    return jsonify({
                        "success": True,
                        "id": doc_id,
                        "type": content_type,
                        "photocard_id": photocard_id,
                        "warning": "Transcript added but AI processing failed",
                        "message": f"Transcript '{data['title']}' added successfully with placeholder photocard"
                    }), 201
                
            except Exception as e:
                # If photocard creation fails, still return success for the transcript
                print(f"Warning: Failed to create photocard for transcript: {e}")
                return jsonify({
                    "success": True,
                    "id": doc_id,
                    "type": content_type,
                    "warning": "Transcript added but photocard creation failed",
                    "message": f"Transcript '{data['title']}' added successfully"
                }), 201
        
        return jsonify({
            "success": True,
            "id": doc_id,
            "type": content_type,
            "message": f"{content_type.title()} '{data['title']}' added successfully"
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Failed to add content: {str(e)}"}), 500

@enhanced_bp.route('/api/transcript/add', methods=['POST'])
def add_transcript():
    """Add a transcript document with enhanced metadata."""
    try:
        data = request.get_json()
        
        if not data or 'title' not in data or 'content' not in data:
            return jsonify({"error": "Missing required fields: title, content"}), 400
        
        store = EnhancedDataStore()
        
        # Add the transcript
        doc_id = store.add_interview_transcript(
            title=data['title'],
            content=data['content'],
            metadata=data.get('metadata', {})
        )
        
        return jsonify({
            "success": True,
            "id": doc_id,
            "message": f"Transcript '{data['title']}' added successfully"
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Failed to add transcript: {str(e)}"}), 500

@enhanced_bp.route('/api/documents/<doc_id>', methods=['GET'])
def get_document(doc_id):
    """Get a specific document by ID."""
    try:
        store = EnhancedDataStore()
        document = store.get_document(doc_id)
        
        if not document:
            return jsonify({"error": "Document not found"}), 404
        
        return jsonify({
            "success": True,
            "document": document
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve document: {str(e)}"}), 500

@enhanced_bp.route('/api/documents/<doc_id>', methods=['PUT'])
def update_document(doc_id):
    """Update an existing document."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No update data provided"}), 400
        
        store = EnhancedDataStore()
        
        # Update the document
        success = store.update_document(
            doc_id=doc_id,
            title=data.get('title'),
            content=data.get('content'),
            metadata=data.get('metadata')
        )
        
        if not success:
            return jsonify({"error": "Document not found or no changes made"}), 404
        
        return jsonify({
            "success": True,
            "message": f"Document updated successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to update document: {str(e)}"}), 500

@enhanced_bp.route('/api/documents/<doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """Delete a document."""
    try:
        store = EnhancedDataStore()
        success = store.delete_document(doc_id)
        
        if not success:
            return jsonify({"error": "Document not found"}), 404
        
        return jsonify({
            "success": True,
            "message": "Document deleted successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to delete document: {str(e)}"}), 500

@enhanced_bp.route('/api/media/<doc_id>', methods=['GET'])
def get_media_item(doc_id):
    """Get a specific media item by document ID."""
    try:
        store = EnhancedDataStore()
        item = store.get_media_item(doc_id)
        
        if item:
            return jsonify(item), 200
        else:
            return jsonify({"error": "Media item not found"}), 404
            
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve media item: {str(e)}"}), 500

@enhanced_bp.route('/api/media/upload', methods=['POST'])
def upload_media():
    """Upload multiple media files with optional media file details."""
    try:
        if 'files' not in request.files:
            return jsonify({"error": "No files provided"}), 400
        
        files = request.files.getlist('files')
        if not files or all(file.filename == '' for file in files):
            return jsonify({"error": "No files selected"}), 400
        
        # Get media file details from form data
        media_file_name = request.form.get('media_file_name', '').strip()
        media_file_description = request.form.get('media_file_description', '').strip()
        
        store = EnhancedDataStore()
        uploaded_items = []
        
        for file in files:
            if file.filename == '':
                continue
                
            # Check if file is an image
            if not file.content_type or not file.content_type.startswith('image/'):
                continue
                
            # Create a safe filename
            filename = file.filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{timestamp}_{filename}"
            file_path = f"uploads/{safe_filename}"
            
            # Ensure uploads directory exists
            os.makedirs('uploads', exist_ok=True)
            
            # Save the actual file to disk
            file.save(file_path)
            
            # Add to database with media file details
            metadata = {
                'title': media_file_name if media_file_name else safe_filename,
                'summary': media_file_description if media_file_description else '',
                'file_size': len(file.read()),
                'file_type': file.content_type,
                'original_filename': filename
            }
            
            # Reset file pointer for storage
            file.seek(0)
            
            media_item = store.add_media_item(
                file_path=file_path,
                metadata=metadata
            )
            
            uploaded_items.append(media_item)
        
        return jsonify({
            "message": f"Successfully uploaded {len(uploaded_items)} files",
            "uploaded_items": uploaded_items,
            "media_file_name": media_file_name,
            "media_file_description": media_file_description
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@enhanced_bp.route('/api/media/<doc_id>/title', methods=['PUT'])
def update_media_title(doc_id):
    """Update the title of a media item."""
    try:
        data = request.get_json()
        title = data.get('title', '')
        
        store = EnhancedDataStore()
        success = store.update_media_item(doc_id, title=title)
        
        if success:
            return jsonify({"message": "Title updated successfully"}), 200
        else:
            return jsonify({"error": "Failed to update title"}), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to update title: {str(e)}"}), 500

@enhanced_bp.route('/api/media/<doc_id>/summary', methods=['PUT'])
def update_media_summary(doc_id):
    """Update the summary of a media item."""
    try:
        data = request.get_json()
        summary = data.get('summary', '')
        
        store = EnhancedDataStore()
        success = store.update_media_item(doc_id, summary=summary)
        
        if success:
            return jsonify({"message": "Summary updated successfully"}), 200
        else:
            return jsonify({"error": "Failed to update summary"}), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to update summary: {str(e)}"}), 500

@enhanced_bp.route('/api/media/<doc_id>/tags', methods=['PUT'])
def update_media_tags(doc_id):
    """Update the tags of a media item."""
    try:
        data = request.get_json()
        tags = data if isinstance(data, list) else []
        
        store = EnhancedDataStore()
        success = store.update_media_item(doc_id, tags=tags)
        
        if success:
            return jsonify({"message": "Tags updated successfully"}), 200
        else:
            return jsonify({"error": "Failed to update tags"}), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to update tags: {str(e)}"}), 500

@enhanced_bp.route('/api/media/<doc_id>', methods=['DELETE'])
def delete_media_item(doc_id):
    """Delete a media item."""
    try:
        store = EnhancedDataStore()
        success = store.delete_media_item(doc_id)
        
        if success:
            return jsonify({"message": "Media item deleted successfully"}), 200
        else:
            return jsonify({"error": "Failed to delete media item"}), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to delete media item: {str(e)}"}), 500

@enhanced_bp.route('/api/media/<doc_id>/contexts', methods=['GET'])
def get_media_contexts(doc_id):
    """Get all context entries for a media item."""
    try:
        store = EnhancedDataStore()
        contexts = store.get_contexts(doc_id)
        return jsonify(contexts), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve contexts: {str(e)}"}), 500

@enhanced_bp.route('/api/media/<doc_id>/contexts', methods=['POST'])
def add_media_context(doc_id):
    """Add a new context entry for a media item."""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({"error": "Text is required"}), 400
        
        store = EnhancedDataStore()
        context_id = store.add_context(doc_id, text)
        
        return jsonify({"id": context_id}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to add context: {str(e)}"}), 500

@enhanced_bp.route('/api/media/<doc_id>/contexts/<context_id>', methods=['PUT'])
def update_media_context(doc_id, context_id):
    """Update a context entry for a media item."""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({"error": "Text is required"}), 400
        
        store = EnhancedDataStore()
        success = store.update_context(doc_id, context_id, text)
        
        if success:
            return jsonify({"message": "Context updated successfully"}), 200
        else:
            return jsonify({"error": "Failed to update context"}), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to update context: {str(e)}"}), 500

@enhanced_bp.route('/api/media/<doc_id>/contexts/<context_id>', methods=['DELETE'])
def delete_media_context(doc_id, context_id):
    """Delete a context entry for a media item."""
    try:
        store = EnhancedDataStore()
        success = store.delete_context(doc_id, context_id)
        
        if success:
            return jsonify({"message": "Context deleted successfully"}), 200
        else:
            return jsonify({"error": "Failed to delete context"}), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to delete context: {str(e)}"}), 500

@enhanced_bp.route('/api/media/<doc_id>/interview/start', methods=['POST'])
def start_interview(doc_id):
    """Start an AI interview for a media item."""
    try:
        store = EnhancedDataStore()
        # This would integrate with your interview bot
        # For now, return a placeholder response
        return jsonify({
            "media_id": doc_id,
            "ai_question": "Tell me about this photo. What do you see?",
            "messages": [
                {
                    "role": "system",
                    "content": "I'm here to help you explore this photo through conversation."
                }
            ]
        }), 200
    except Exception as e:
        return jsonify({"error": f"Failed to start interview: {str(e)}"}), 500

def extract_main_content(soup):
    """Extract main content from HTML, removing navigation and ads."""
    # Remove unwanted elements
    for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
        element.decompose()
    
    # Remove common ad and navigation classes
    for element in soup.find_all(class_=re.compile(r'(ad|nav|menu|sidebar|banner|popup)', re.I)):
        element.decompose()
    
    # Look for main content areas
    main_content = None
    
    # Try to find main content by common selectors
    selectors = [
        'main',
        '[role="main"]',
        '.content',
        '.main-content',
        '.post-content',
        '.article-content',
        '.entry-content'
    ]
    
    for selector in selectors:
        main_content = soup.select_one(selector)
        if main_content:
            break
    
    # If no main content found, try to find the largest text block
    if not main_content:
        text_blocks = soup.find_all(['p', 'div', 'article', 'section'])
        if text_blocks:
            # Find the block with the most text
            main_content = max(text_blocks, key=lambda x: len(x.get_text()))
    
    if main_content:
        # Clean up the content
        text = main_content.get_text()
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    # Fallback: get all text from body
    return soup.get_text()

def extract_website_metadata(soup, url):
    """Extract metadata from website HTML."""
    metadata = {
        "url": url,
        "imported_at": datetime.now().isoformat(),
        "content_type": "website"
    }
    
    # Extract meta tags
    meta_tags = soup.find_all('meta')
    for meta in meta_tags:
        name = meta.get('name', meta.get('property', ''))
        content = meta.get('content', '')
        
        if name and content:
            if name in ['description', 'og:description']:
                metadata['description'] = content
            elif name in ['keywords', 'og:keywords']:
                metadata['keywords'] = content
            elif name == 'author':
                metadata['author'] = content
    
    # Extract Open Graph tags
    og_title = soup.find('meta', property='og:title')
    if og_title:
        metadata['og_title'] = og_title.get('content', '')
    
    # Extract structured data (JSON-LD)
    json_ld = soup.find('script', type='application/ld+json')
    if json_ld:
        try:
            import json
            structured_data = json.loads(json_ld.string)
            if isinstance(structured_data, dict):
                if structured_data.get('@type') == 'Article':
                    metadata['article_type'] = 'Article'
                    if 'datePublished' in structured_data:
                        metadata['published_date'] = structured_data['datePublished']
        except:
            pass
    
    return metadata


