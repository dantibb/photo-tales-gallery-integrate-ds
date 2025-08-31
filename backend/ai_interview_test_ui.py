from app import create_app
from app import data_access
from flask import render_template, request, redirect, url_for, session, send_from_directory, jsonify
from interviewer_bot import run_interview_chat, get_memory_gatherer_prompt, generate_image_tags
from prompts import build_summary_prompt, build_context_summary
from image_metadata import extract_image_metadata, format_metadata_for_display, get_metadata_summary
from flask_session import Session
import os
import re
from tinydb import TinyDB, Query
import openai
import base64
from collections import Counter

# Set static_folder to the project root static directory
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = create_app('local', template_folder=template_dir)
app.static_folder = static_dir
Session(app)

print("CWD:", os.getcwd())
print("Exists:", os.path.exists("templates/ai_test_index.html"))
print("Template search path:", app.jinja_loader.searchpath)
print("Static folder:", app.static_folder)

IMAGE_FOLDER = app.config['UPLOAD_FOLDER']

template_folder='templates'

# Ensure image folder exists
os.makedirs(IMAGE_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    images = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))]
    image_data = []
    all_tags = []
    for img in images:
        structured_summary = data_access.get_structured_summary(img)
        tags = data_access.get_tags(img)
        image_data.append({
            "name": img,
            "summary_title": structured_summary.get("summary_title", ""),
            "summary_summary": structured_summary.get("summary_summary", ""),
            "tags": tags
        })
        all_tags.extend(tags)
    tag_counts = Counter(all_tags)
    # Sort tags by count descending, then alphabetically
    sorted_tag_counts = sorted(tag_counts.items(), key=lambda x: (-x[1], x[0].lower()))
    print("DEBUG: image names for index:", [img["name"] for img in image_data])
    return render_template("ai_test_index.html", images=image_data, tag_counts=sorted_tag_counts)

@app.route("/interview/<image_name>", methods=["GET", "POST"])
def interview(image_name):
    image_path = os.path.join(IMAGE_FOLDER, image_name)
    if not os.path.exists(image_path):
        return "Image not found", 404

    # Always use the default system prompt
    system_prompt = get_memory_gatherer_prompt()

    if "messages" not in session or session.get("image_name") != image_name:
        session["messages"] = []
        session["image_name"] = image_name

    ai_reply = None

    # Get the summary for this image (if any)
    structured_summary = data_access.get_structured_summary(image_name)
    ai_summary = structured_summary.get('summary', '')
    title = structured_summary.get('summary_title', '')
    summary_text = structured_summary.get('summary_summary', '')
    description = structured_summary.get('summary_description', '')

    if request.method == "POST":
        user_text = request.form["user_text"]
        previous_messages = session.get("messages", [])
        # Only send the image on the first user response
        send_image = False
        if not previous_messages or (len(previous_messages) == 1 and previous_messages[0]["role"] == "system"):
            send_image = True
        if send_image:
            ai_reply, updated_messages = run_interview_chat(user_text, previous_messages, image_path=image_path, system_prompt=system_prompt)
        else:
            ai_reply, updated_messages = run_interview_chat(user_text, previous_messages, image_path=None, system_prompt=system_prompt)
        session["messages"] = updated_messages
        # Add the user's response as a context description
        data_access.add_context(image_name, user_text)

    # Get only the latest AI question for display
    messages = session.get("messages", [])
    latest_question = None
    if messages:
        # Find the last assistant message
        for msg in reversed(messages):
            if msg["role"] == "assistant":
                latest_question = msg
                break
    
    # Create a list with only the latest question for the template
    display_messages = [latest_question] if latest_question else []

    return render_template(
        "ai_test_interview.html",
        image_name=image_name,
        ai_reply=ai_reply,
        messages=display_messages,
        system_prompt=system_prompt,
        ai_summary=ai_summary,
        title=title,
        summary_text=summary_text,
        description=description
    )

@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("index"))

@app.route("/test_images/<filename>")
def images(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

@app.route("/images/<image_name>/contexts", methods=["GET"])
def get_image_contexts(image_name):
    contexts = data_access.get_contexts(image_name)
    return jsonify(contexts)

@app.route("/images/<image_name>/contexts", methods=["POST"])
def add_image_context(image_name):
    data = request.get_json()
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Text is required."}), 400
    new_context = data_access.add_context(image_name, text)
    return jsonify(new_context), 201

@app.route("/images/<image_name>/contexts/<context_id>", methods=["PUT"])
def update_image_context(image_name, context_id):
    data = request.get_json()
    new_text = data.get("text", "").strip()
    if not new_text:
        return jsonify({"error": "Text is required."}), 400
    updated = data_access.update_context(image_name, context_id, new_text)
    if updated:
        return jsonify({"success": True})
    else:
        return jsonify({"error": "Context not found."}), 404

@app.route("/images/<image_name>/contexts/<context_id>", methods=["DELETE"])
def delete_image_context(image_name, context_id):
    deleted = data_access.delete_context(image_name, context_id)
    if deleted:
        return jsonify({"success": True})
    else:
        return jsonify({"error": "Context not found."}), 404

@app.route("/start_interview/<image_name>", methods=["POST"])
def start_interview(image_name):
    data = request.get_json()
    system_prompt = data.get("system_prompt")
    # Gather all context descriptions for the image
    contexts = data_access.get_contexts(image_name)
    context_texts = [ctx['text'] for ctx in contexts]

    # Extract captured date from image metadata
    image_path = os.path.join(IMAGE_FOLDER, image_name)
    metadata = extract_image_metadata(image_path)
    date_captured = None
    for tag in ['DateTimeOriginal', 'DateTime', 'DateTimeDigitized']:
        if tag in metadata.get('exif_data', {}):
            date_captured = metadata['exif_data'][tag]
            break
    if date_captured:
        context_texts.insert(0, f"This photo was captured on {date_captured}.")

    # Use the new context summary builder
    context_summary = build_context_summary(context_texts)

    # Call run_interview_chat with the image, context, and system prompt
    ai_reply, updated_messages = run_interview_chat(context_summary, previous_messages=None, image_path=image_path, system_prompt=system_prompt)
    # Store messages in session
    session["messages"] = updated_messages
    session["image_name"] = image_name
    return jsonify({"ai_reply": ai_reply, "messages": updated_messages})

def parse_structured_summary(summary_text):
    # Accepts both "Summary:" and "### Summary:" (same for other sections)
    import re
    title = summary = ""
    title_match = re.search(r"Title:\s*([\s\S]*?)(?=\n\s*(?:###\s*)?Summary:|$)", summary_text, re.IGNORECASE)
    summary_match = re.search(r"(?:###\s*)?Summary:\s*([\s\S]*)", summary_text, re.IGNORECASE)
    if title_match:
        title = title_match.group(1).strip()
    if summary_match:
        summary = summary_match.group(1).strip()
    return title, summary

@app.route("/summarise/<image_name>", methods=["POST"])
def summarise(image_name):
    # Gather user context and metadata for the image (no AI chat messages)
    contexts = data_access.get_contexts(image_name)
    context_texts = [ctx['text'] for ctx in contexts]

    # Extract captured date from image metadata
    image_path = os.path.join(IMAGE_FOLDER, image_name)
    metadata = extract_image_metadata(image_path)
    date_captured = None
    for tag in ['DateTimeOriginal', 'DateTime', 'DateTimeDigitized']:
        if tag in metadata.get('exif_data', {}):
            date_captured = metadata['exif_data'][tag]
            break
    if date_captured:
        context_texts.insert(0, f"This photo was captured on {date_captured}.")

    # Use the new prompt builder function with only user context (no AI chat messages)
    summary_prompt = build_summary_prompt(context_texts, [])

    # Call OpenAI to generate the summary
    ai_summary, _ = run_interview_chat(summary_prompt, previous_messages=None, image_path=image_path)
    # Parse the summary into sections
    title, summary = parse_structured_summary(ai_summary)
    # Store the structured summary in the database
    data_access.set_structured_summary(image_name, ai_summary, title, summary, "")
    return jsonify({"summary": ai_summary, "title": title, "summary_text": summary, "description": ""})

@app.route("/clear_all_contexts", methods=["POST"])
def clear_all_contexts():
    """Clear all contexts from the database."""
    try:
        data_access.clear_all_contexts()
        return jsonify({"success": True, "message": "All contexts cleared successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/images/<image_name>/metadata", methods=["GET"])
def get_image_metadata(image_name):
    """Get metadata for a specific image."""
    try:
        image_path = os.path.join(IMAGE_FOLDER, image_name)
        if not os.path.exists(image_path):
            return jsonify({"error": "Image not found"}), 404
        
        # Extract raw metadata
        raw_metadata = extract_image_metadata(image_path)
        
        # Format for display
        formatted_metadata = format_metadata_for_display(raw_metadata)
        
        # Get summary
        summary = get_metadata_summary(raw_metadata)
        
        return jsonify({
            "success": True,
            "raw_metadata": raw_metadata,
            "formatted_metadata": formatted_metadata,
            "summary": summary
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/clear_all_summaries", methods=["POST"])
def clear_all_summaries_route():
    try:
        db = TinyDB('local_contexts.json')
        for item in db:
            db.update({
                'summary': '',
                'summary_title': '',
                'summary_summary': '',
                'summary_description': ''
            }, Query().image_name == item['image_name'])
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/media")
def api_media():
    images = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))]
    items = []
    for image_name in images:
        structured_summary = data_access.get_structured_summary(image_name)
        items.append({
            "id": image_name,
            "gcs_path": image_name,
            "summary_title": structured_summary.get("summary_title", ""),
            "summary_summary": structured_summary.get("summary_summary", ""),
            # Add more fields as needed (e.g., file size, metadata)
        })
    return jsonify(items)

@app.route('/api/ai_tag/<image_name>', methods=['POST'])
def ai_tag_image(image_name):
    contexts = data_access.get_contexts(image_name)
    summary_data = data_access.get_structured_summary(image_name)
    summary = summary_data.get('summary', '')
    context_text = ' '.join([c['text'] for c in contexts])

    # Gather all unique tags from all images
    images = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))]
    all_tags = []
    for img in images:
        tags = data_access.get_tags(img)
        all_tags.extend(tags)
    unique_tags = list(set(all_tags))

    image_path = os.path.join(IMAGE_FOLDER, image_name)
    tags = generate_image_tags(image_path, context_text, summary, model="gpt-4o-mini", existing_tags=unique_tags)
    data_access.set_tags(image_name, tags)
    return jsonify({"tags": tags})

@app.route('/api/remove_tag/<tag>', methods=['POST'])
def remove_tag(tag):
    from app.local_db import _db, Context
    all_docs = _db.all()
    for doc in all_docs:
        tags = doc.get('tags', [])
        if tag in tags:
            tags = [t for t in tags if t != tag]
            _db.update({'tags': tags}, Context.image_name == doc['image_name'])
    return jsonify({"success": True, "removed": tag})

@app.route('/api/clear_all_tags', methods=['POST'])
def clear_all_tags():
    from app.local_db import _db, Context
    all_docs = _db.all()
    for doc in all_docs:
        if 'tags' in doc and doc['tags']:
            _db.update({'tags': []}, Context.image_name == doc['image_name'])
    return jsonify({"success": True})

@app.route('/api/ai_tag_question/<tag>', methods=['POST'])
def ai_tag_question(tag):
    # Gather all images with the given tag
    images = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))]
    filtered_contexts = []
    filtered_tags = []
    for img in images:
        tags = data_access.get_tags(img)
        if tag in tags:
            summary_data = data_access.get_structured_summary(img)
            context = summary_data.get('summary', '')
            filtered_contexts.append(context)
            filtered_tags.extend(tags)
    # Remove duplicates
    filtered_tags = list(set(filtered_tags))
    # Compose prompt
    prompt = (
        "You are the owner of these photos. Given the following tag, and the context and tags of several images, "
        "write a short, first-person summary (no more than 2 or 3 short sentences) that describes the known context of these images, "
        "including some personal detail from the context and tags provided. Use language and phrasing that closely matches the style of the context and tags provided. "
        "Be natural and concise, as if you were telling a friend. For example: 'These are some pictures of Paris, I travelled there a lot as I worked there.'\n\n"
        f"Tag: {tag}\n"
        f"Contexts: {filtered_contexts}\n"
        f"Tags: {filtered_tags}\n\n"
        "Summary:"
    )
    
    # Debug logging: Print the exact prompt being sent to OpenAI
    print("\n" + "="*80)
    print("OPENAI API CALL - AI TAG QUESTION:")
    print("="*80)
    print(f"User: {prompt}")
    print("="*80 + "\n")
    
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=100
    )
    question = response.choices[0].message.content.strip() if response.choices[0].message.content else ''
    return jsonify({"question": question})

if __name__ == "__main__":
    app.run(debug=True) 