from flask import current_app as app, render_template, request, jsonify
import os
import openai
import base64
from app.local_db import get_contexts, get_structured_summary, set_tags

@app.route('/')
def index():
    return render_template('gallery.html')

@app.route('/lottie-avatar-test')
def lottie_avatar_test():
    return render_template('lottie_avatar_test.html')

@app.route('/vrm-avatar-test')
def vrm_avatar_test():
    return render_template('vrm_avatar_test.html')

@app.route('/api/ai_tag/<image_name>', methods=['POST'])
def ai_tag_image(image_name):
    contexts = get_contexts(image_name)
    summary_data = get_structured_summary(image_name)
    summary = summary_data.get('summary', '')
    context_text = ' '.join([c['text'] for c in contexts])

    image_path = os.path.join('test_images', image_name)
    with open(image_path, 'rb') as img_file:
        image_b64 = base64.b64encode(img_file.read()).decode()

    prompt = f"You are an expert photo tagger. Given the following image and its context/summary, generate a list of 3-7 relevant, concise tags (single words or short phrases, comma-separated).\n\nContext: {context_text}\nSummary: {summary}\n\nTags:"

    response = openai.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {"role": "system", "content": "You are an expert photo tagger."},
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_b64}"}
            ]}
        ],
        max_tokens=100
    )
    content = response.choices[0].message.content if response.choices[0].message.content else ''
    tags = [tag.strip() for tag in content.strip().split(',') if tag.strip()]
    set_tags(image_name, tags)
    return jsonify({"tags": tags})

print("Registered routes:")
for rule in app.url_map.iter_rules():
    print(rule) 