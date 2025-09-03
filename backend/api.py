import os
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from app.enhanced_data_store import EnhancedDataStore
import mimetypes
from io import BytesIO
from interviewer_bot import run_interview_chat
import tempfile

# Load environment variables from config.env
load_dotenv(dotenv_path='config.env')

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Enhanced Data Store setup (PostgreSQL)
enhanced_db = EnhancedDataStore()

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/media')
def list_media():
    """Lists media from GCS and syncs with Firestore."""
    
    # Get GCS bucket
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    blobs = bucket.list_blobs()
    gcs_files = [blob.name for blob in blobs]

    # Sync with Firestore
    new_items = enhanced_db.sync_gcs_files(gcs_files)
    
    # Get all media items from Firestore
    items = enhanced_db.list_media_items()
    return jsonify(items)

@app.route('/api/media/<doc_id>')
def get_media_item(doc_id):
    """Get a specific media item by document ID."""
    item = enhanced_db.get_media_item(doc_id)
    if item:
        return jsonify(item)
    return jsonify({"error": "Media item not found"}), 404

@app.route('/api/media/<doc_id>/preview')
def preview_media(doc_id):
    """Preview media file from GCS."""
    item = enhanced_db.get_media_item(doc_id)
    if not item:
        return jsonify({"error": "Media item not found"}), 404
    
    try:
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(item['gcs_path'])
        
        # Get the content type
        content_type, _ = mimetypes.guess_type(item['gcs_path'])
        if not content_type:
            content_type = 'application/octet-stream'
        
        # Download the file content
        file_content = blob.download_as_bytes()
        
        return send_file(
            BytesIO(file_content),
            mimetype=content_type,
            as_attachment=False,
            download_name=os.path.basename(item['gcs_path'])
        )
    except Exception as e:
        return jsonify({"error": f"Failed to load media: {str(e)}"}), 500

@app.route('/api/media/<doc_id>/description', methods=['PUT'])
def update_description(doc_id):
    """Update the description of a media item."""
    data = request.get_json()
    description = data.get('description', '')
    
    success = enhanced_db.update_media_item(doc_id, description=description)
    if success:
        return jsonify({"message": "Description updated successfully"})
    return jsonify({"error": "Failed to update description"}), 400

# --- Contexts API ---

@app.route('/api/media/<media_id>/contexts', methods=['GET'])
def get_contexts(media_id):
    """Get all context entries for a media item."""
    contexts = enhanced_db.get_contexts(media_id)
    return jsonify(contexts)

@app.route('/api/media/<media_id>/contexts', methods=['POST'])
def add_context(media_id):
    """Add a new context entry to a media item."""
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Missing 'text' in request body"}), 400
    
    context_id = enhanced_db.add_context(media_id, data['text'])
    return jsonify({"message": "Context added successfully", "id": context_id}), 201

@app.route('/api/media/<media_id>/contexts/<context_id>', methods=['PUT'])
def update_context(media_id, context_id):
    """Update a specific context entry."""
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Missing 'text' in request body"}), 400

    success = enhanced_db.update_context(media_id, context_id, data['text'])
    if success:
        return jsonify({"message": "Context updated successfully"})
    return jsonify({"error": "Failed to update context"}), 400

@app.route('/api/media/<media_id>/contexts/<context_id>', methods=['DELETE'])
def delete_context(media_id, context_id):
    """Delete a specific context entry."""
    success = enhanced_db.delete_context(media_id, context_id)
    if success:
        return jsonify({"message": "Context deleted successfully"})
    return jsonify({"error": "Failed to delete context"}), 400

# --- AI Interview API ---

@app.route('/api/media/<media_id>/interview/start', methods=['POST'])
def start_interview(media_id):
    """Start a new AI interview for a media item."""
    item = enhanced_db.get_media_item(media_id)
    if not item:
        return jsonify({"error": "Media item not found"}), 404
    
    # Check if this is an image
    is_image = item['gcs_path'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'))
    if not is_image:
        return jsonify({"error": "AI Interview is only available for images"}), 400
    
    try:
        # Get the image from GCS for the interview
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(item['gcs_path'])
        
        # Download image to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            blob.download_to_filename(tmp_file.name)
            tmp_path = tmp_file.name
        
        # Start interview
        ai_question, messages = run_interview_chat(
            "I'd like to talk about this image.",
            previous_messages=None,
            image_path=tmp_path
        )
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return jsonify({
            "media_id": media_id,
            "ai_question": ai_question,
            "messages": messages
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to start interview: {str(e)}"}), 500

@app.route('/api/media/<media_id>/interview/chat', methods=['POST'])
def chat_interview(media_id):
    """Continue an AI interview conversation."""
    item = enhanced_db.get_media_item(media_id)
    if not item:
        return jsonify({"error": "Media item not found"}), 404
    
    data = request.get_json()
    if not data or 'user_text' not in data or 'messages' not in data:
        return jsonify({"error": "Missing 'user_text' or 'messages' in request body"}), 400
    
    user_text = data['user_text']
    previous_messages = data['messages']
    
    try:
        # Get the image from GCS for the interview
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(item['gcs_path'])
        
        # Download image to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            blob.download_to_filename(tmp_file.name)
            tmp_path = tmp_file.name
        
        # Continue interview
        ai_question, messages = run_interview_chat(
            user_text, 
            previous_messages=previous_messages,
            image_path=tmp_path
        )
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return jsonify({
            "media_id": media_id,
            "ai_question": ai_question,
            "messages": messages
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to continue interview: {str(e)}"}), 500

@app.route('/api/media/<media_id>/interview/save', methods=['POST'])
def save_interview(media_id):
    """Save an interview conversation as context."""
    item = enhanced_db.get_media_item(media_id)
    if not item:
        return jsonify({"error": "Media item not found"}), 404
    
    data = request.get_json()
    if not data or 'messages' not in data:
        return jsonify({"error": "Missing 'messages' in request body"}), 400
    
    messages = data['messages']
    
    try:
        # Convert conversation to markdown
        conversation_md = '\n'.join([
            f"**{m['role'].capitalize()}:** {m['content']}" 
            for m in messages if m['role'] != 'system'
        ])
        
        # Save as context
        context_id = enhanced_db.add_context(media_id, conversation_md, context_type='ai_interview')
        
        return jsonify({
            "message": "Interview saved as context successfully",
            "context_id": context_id
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to save interview: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 