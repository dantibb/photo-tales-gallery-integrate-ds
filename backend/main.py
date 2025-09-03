import os
from flask import Flask, jsonify, request, render_template, send_file, redirect, url_for, flash, session
from flask_cors import CORS
from dotenv import load_dotenv
from app.enhanced_data_store import EnhancedDataStore
import mimetypes
from io import BytesIO
from interview_bot import run_interview
from interviewer_bot import run_interview_chat
from app.enhanced_routes import enhanced_bp

# Load environment variables from config.env
load_dotenv(dotenv_path='config.env')

app = Flask(__name__)

# Enable CORS for React frontend
CORS(app, origins=['http://localhost:5173', 'http://localhost:3000', 'http://127.0.0.1:5173'])

# Register the enhanced routes blueprint
app.register_blueprint(enhanced_bp)

# Enhanced Data Store setup (PostgreSQL)
enhanced_db = EnhancedDataStore()

app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev_secret')  # Needed for session

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/media')
def list_media():
    """Lists media from the local database."""
    try:
        # Get all media items from the database
        items = enhanced_db.list_media_items()
        return jsonify(items)
    except Exception as e:
        return jsonify({"error": f"Failed to list media: {str(e)}"}), 500

@app.route('/media/<doc_id>')
def get_media_item(doc_id):
    """Get a specific media item by document ID."""
    item = enhanced_db.get_media_item(doc_id)
    if item:
        return jsonify(item)
    return jsonify({"error": "Media item not found"}), 404

@app.route('/api/media/<doc_id>/preview')
def preview_media(doc_id):
    """Preview media file from local storage."""
    item = enhanced_db.get_media_item(doc_id)
    if not item:
        return jsonify({"error": "Media item not found"}), 404
    
    try:
        file_path = item.get('file_path')
        
        # Check if file_path exists in the item
        if not file_path:
            return jsonify({"error": "No file path found for media item"}), 404
        
        # Check if file exists
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404
        
        # Get the content type
        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = 'application/octet-stream'
        
        return send_file(
            file_path,
            mimetype=content_type,
            as_attachment=False,
            download_name=os.path.basename(file_path)
        )
    except Exception as e:
        return jsonify({"error": f"Failed to load media: {str(e)}"}), 500

@app.route('/media/<doc_id>/description', methods=['PUT'])
def update_description(doc_id):
    """Update the description of a media item."""
    data = request.get_json()
    description = data.get('description', '')
    
    success = enhanced_db.update_media_item(doc_id, description=description)
    if success:
        return jsonify({"message": "Description updated successfully"})
    return jsonify({"error": "Failed to update description"}), 400

# --- Contexts API ---

@app.route('/media/<media_id>/contexts', methods=['GET'])
def get_contexts(media_id):
    """Get all context entries for a media item."""
    contexts = enhanced_db.get_contexts(media_id)
    return jsonify(contexts)

@app.route('/media/<media_id>/contexts', methods=['POST'])
def add_context(media_id):
    """Add a new context entry to a media item."""
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Missing 'text' in request body"}), 400
    
    context_id = enhanced_db.add_context(media_id, data['text'])
    return jsonify({"message": "Context added successfully", "id": context_id}), 201

@app.route('/media/<media_id>/contexts/<context_id>', methods=['PUT'])
def update_context(media_id, context_id):
    """Update a specific context entry."""
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Missing 'text' in request body"}), 400

    success = enhanced_db.update_context(media_id, context_id, data['text'])
    if success:
        return jsonify({"message": "Context updated successfully"})
    return jsonify({"error": "Failed to update context"}), 400

@app.route('/media/<media_id>/contexts/<context_id>', methods=['DELETE'])
def delete_context(media_id, context_id):
    """Delete a specific context entry."""
    success = enhanced_db.delete_context(media_id, context_id)
    if success:
        return jsonify({"message": "Context deleted successfully"})
    return jsonify({"error": "Failed to delete context"}), 400

@app.route('/media/<media_id>/interview', methods=['GET', 'POST'])
def interview_media(media_id):
    item = enhanced_db.get_media_item(media_id)
    if not item:
        return "Media item not found", 404
    if request.method == 'POST':
        user_input = request.form.get('context')
        if user_input:
            run_interview(media_id, user_input)
            flash('Your context has been saved!', 'success')
            return redirect(url_for('gallery'))
        else:
            flash('Please provide some context.', 'danger')
    return render_template('interview.html', media=item)

@app.route('/media/<media_id>/ai-interview', methods=['GET', 'POST'])
def ai_interview_media(media_id):
    item = enhanced_db.get_media_item(media_id)
    if not item:
        return "Media item not found", 404
    if 'ai_chat' not in session or session.get('ai_chat_media_id') != media_id:
        # Start new conversation
        session['ai_chat'] = []
        session['ai_chat_media_id'] = media_id
        ai_question, messages = run_interview_chat(
            user_text="I'd like to talk about this image.",
            previous_messages=None,
            image_path=None  # You could download the image from GCS if you want to send it
        )
        session['ai_chat'] = messages
        return render_template('ai_interview.html', media=item, ai_question=ai_question, chat=messages)

    messages = session['ai_chat']
    ai_question = None
    if request.method == 'POST':
        user_text = request.form.get('user_text')
        if user_text:
            ai_question, messages = run_interview_chat(user_text, previous_messages=messages)
            session['ai_chat'] = messages
            if 'finish' in request.form:
                # Save the conversation as a context entry
                conversation_md = '\n'.join([
                    f"**{m['role'].capitalize()}:** {m['content']}" for m in messages if m['role'] != 'system']
                )
                enhanced_db.add_context(media_id, conversation_md, context_type='ai_interview')
                flash('Interview saved as context!', 'success')
                session.pop('ai_chat', None)
                session.pop('ai_chat_media_id', None)
                return redirect(url_for('gallery'))
        else:
            flash('Please enter a response.', 'danger')
    else:
        ai_question = messages[-1]['content'] if messages and messages[-1]['role'] == 'assistant' else None
    return render_template('ai_interview.html', media=item, ai_question=ai_question, chat=messages)

@app.route('/media/<media_id>/gallery-interview', methods=['GET', 'POST'])
def gallery_interview(media_id):
    """Gallery interview with image context from GCS."""
    item = enhanced_db.get_media_item(media_id)
    if not item:
        return "Media item not found", 404
    
    # Check if this is an image
    is_image = item['gcs_path'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'))
    if not is_image:
        flash('AI Interview is only available for images.', 'warning')
        return redirect(url_for('gallery'))
    
    # Initialize or get existing chat session
    if 'gallery_chat' not in session or session.get('gallery_chat_media_id') != media_id:
        session['gallery_chat'] = []
        session['gallery_chat_media_id'] = media_id
    
    messages = session['gallery_chat']
    
    if request.method == 'POST':
        user_text = request.form.get('user_text')
        if user_text:
            # For now, run interview without image (placeholder functionality)
            try:
                # TODO: Implement local image handling when you have actual image files
                ai_question, messages = run_interview_chat(
                    user_text, 
                    previous_messages=messages,
                    image_path=None  # No image for now
                )
                
                session['gallery_chat'] = messages
                
                if 'finish' in request.form:
                    # Save the conversation as a context entry
                    conversation_md = '\n'.join([
                        f"**{m['role'].capitalize()}:** {m['content']}" 
                        for m in messages if m['role'] != 'system'
                    ])
                    enhanced_db.add_context(media_id, conversation_md, context_type='ai_interview')
                    flash('Interview saved as context!', 'success')
                    session.pop('gallery_chat', None)
                    session.pop('gallery_chat_media_id', None)
                    return redirect(url_for('gallery'))
                    
            except Exception as e:
                flash(f'Error processing image: {str(e)}', 'danger')
                return redirect(url_for('gallery'))
        else:
            flash('Please enter a response.', 'danger')
    
    # Get the last AI question for display
    ai_question = None
    if messages:
        # Find the last assistant message
        for msg in reversed(messages):
            if msg['role'] == 'assistant':
                ai_question = msg['content']
                break
    
    # If no previous conversation, start with an initial question
    if not ai_question and not messages:
        try:
            # TODO: Implement local image handling when you have actual image files
            ai_question, messages = run_interview_chat(
                "I'd like to talk about this image.",
                previous_messages=None,
                image_path=None  # No image for now
            )
            
            session['gallery_chat'] = messages
            
        except Exception as e:
            flash(f'Error starting interview: {str(e)}', 'danger')
            return redirect(url_for('gallery'))
    
    return render_template('gallery_interview.html', media=item, ai_question=ai_question, chat=messages)

if __name__ == '__main__':
    app.run(debug=True, port=8080) 