import openai
import base64
import os
from datetime import datetime
from PIL import Image
import io
from prompts import get_memory_gatherer_prompt
from dotenv import load_dotenv
load_dotenv(dotenv_path='config.env')

# --- Configuration ---
# Get your OpenAI API key from environment variables or replace with your key directly (less secure)
# It's recommended to set it as an environment variable: export OPENAI_API_KEY='your_key_here'
openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    print("Error: OPENAI_API_KEY environment variable not set.")
    print("Please set it before running, e.g., export OPENAI_API_KEY='sk-...'")
    # Only exit if this is the main module, not when imported
    if __name__ == "__main__":
        exit()

# Store the conversation in a Markdown file
OUTPUT_FOLDER = "interviews"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
current_interview_filename = ""

def encode_image(image_path):
    """Encodes an image to a base64 string."""
    try:
        with Image.open(image_path) as img:
            # Resize image if too large to save tokens/cost
            max_size = (1024, 1024) # Example max dimensions
            img.thumbnail(max_size, Image.LANCZOS)
            
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG") # Use JPEG for smaller size
            return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        return None
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def store_conversation(question, answer, role="user"):
    """Appends the question and answer to the current interview file."""
    if not current_interview_filename:
        print("Error: Interview file not set up.")
        return

    with open(os.path.join(OUTPUT_FOLDER, current_interview_filename), "a", encoding="utf-8") as f:
        if role == "assistant":
            f.write(f"\n**The Chronicler Asks:**\n{question}\n")
        else: # user's response
            f.write(f"\n**My Response:**\n{answer}\n")
            f.write("---\n") # Separator for new Q&A turn

def run_interview_chat(user_text, previous_messages=None, image_path=None, system_prompt=None, existing_context=None, model="gpt-4o-mini"):
    """
    Run a single turn of the interview chat.
    - user_text: The user's latest answer.
    - previous_messages: The conversation so far (list of dicts).
    - image_path: Optional local path to an image to include in the prompt.
    - system_prompt: The system prompt to use (string). If None, use default.
    - existing_context: Optional list of existing context strings to inform the AI.
    Returns: (ai_question, updated_messages)
    """
    if system_prompt is None:
        system_prompt = get_memory_gatherer_prompt()
    
    # Debug logging
    print(f"run_interview_chat called with existing_context: {existing_context}")
    print(f"existing_context length: {len(existing_context) if existing_context else 0}")
    
    # Enhance the system prompt with existing context if available
    if existing_context and len(existing_context) > 0:
        context_summary = "\n\n".join([f"- {ctx}" for ctx in existing_context])
        enhanced_prompt = f"{system_prompt}\n\nEXISTING CONTEXT ABOUT THIS IMAGE:\n{context_summary}\n\nIMPORTANT: You already have significant context about this image. Instead of asking basic questions like 'where was this taken?' or 'tell me about this photo', ask specific follow-up questions that build upon the existing information. For example, if you know it was taken in Paris near the opera house, ask about specific details of that experience, what they saw at Jardin Luxembourg, or other aspects of their Paris trip that aren't yet documented."
        print(f"Enhanced prompt length: {len(enhanced_prompt)}")
    else:
        enhanced_prompt = system_prompt
        print("No existing context provided")
    
    # Initialize messages properly
    if previous_messages is None:
        messages = [{"role": "system", "content": enhanced_prompt}]
    else:
        messages = previous_messages.copy()
        # Ensure the system message is updated with the enhanced prompt
        if messages and messages[0]["role"] == "system":
            messages[0]["content"] = enhanced_prompt
        else:
            messages.insert(0, {"role": "system", "content": enhanced_prompt})
    
    user_input_parts = []
    if image_path:
        encoded_image = encode_image(image_path)
        if encoded_image:
            user_input_parts.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}})
    user_input_parts.append({"type": "text", "text": user_text})
    messages.append({"role": "user", "content": user_input_parts})

    # Debug logging: Print the exact prompt being sent to OpenAI
    print("\n" + "="*80)
    print("OPENAI API CALL - EXACT PROMPT:")
    print("="*80)
    for i, msg in enumerate(messages):
        print(f"\n[{i}] Role: {msg['role']}")
        if isinstance(msg['content'], list):
            for j, part in enumerate(msg['content']):
                if part.get('type') == 'text':
                    print(f"    Text: {part['text']}")
                elif part.get('type') == 'image_url':
                    print(f"    Image: [base64 encoded image data]")
        else:
            print(f"    Content: {msg['content']}")
    print("="*80 + "\n")

    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=1000,
    )
    ai_question = response.choices[0].message.content
    messages.append({"role": "assistant", "content": ai_question})
    return ai_question, messages

def generate_image_tags(image_path, context, summary, model="gpt-4o-mini", existing_tags=None):
    if existing_tags is None:
        existing_tags = []
    tag_list_str = ', '.join(sorted(existing_tags))
    prompt = (
        "You are an expert photo tagger. Given the following context/summary, "
        "generate a list of 3-6 relevant, concise tags (single words or short phrases, comma-separated). Where possible add a place and a year/month. If any people are named include the name too. "
        "If any of the following existing tags are appropriate, use them but always add a date and new location. "
        "If the capture date is available in the metadata, extract the year from it and include it as a tag (e.g., '2022'). "
        f"Existing tags: {tag_list_str}\n\n"
        f"Context: {context}\nSummary: {summary}\n\nTags:"
    )

    # Debug logging: Print the exact prompt being sent to OpenAI
    print("\n" + "="*80)
    print("OPENAI API CALL - IMAGE TAGGING:")
    print("="*80)
    print(f"System: You are an expert photo tagger.")
    print(f"User: {prompt}")
    print("="*80 + "\n")

    response = openai.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert photo tagger."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100
    )
    content = response.choices[0].message.content if response.choices[0].message.content else ''
    tags = [tag.strip() for tag in content.strip().split(',') if tag.strip()]
    return tags

def main():
    global current_interview_filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    current_interview_filename = f"interview_{timestamp}.md"
    print(f"\nStarting new interview session. Output will be saved to: {os.path.join(OUTPUT_FOLDER, current_interview_filename)}\n")

    messages = [{"role": "system", "content": get_memory_gatherer_prompt()}]

    # Write initial header to file
    with open(os.path.join(OUTPUT_FOLDER, current_interview_filename), "w", encoding="utf-8") as f:
        f.write(f"# Interview Session: {timestamp}\n\n")
        f.write("## Memory Gatherer's Introduction:\n")
        f.write(get_memory_gatherer_prompt().strip() + "\n\n")
        f.write("---\n")

    print("\n" + get_memory_gatherer_prompt().strip())
    print("\n---")

    while True:
        user_input_parts = []
        image_path = input("\nEnter image path (leave empty for text only): ").strip()
        
        if image_path:
            encoded_image = encode_image(image_path)
            if encoded_image:
                user_input_parts.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}})
            else:
                print("Could not process image. Continuing with text only.")

        text_input = input("Share your initial thought or description: ").strip()
        user_input_parts.append({"type": "text", "text": text_input})

        messages.append({"role": "user", "content": user_input_parts})
        store_conversation(text_input, f"Image: {image_path}" if image_path else text_input, role="user") # Store user's initial prompt

        try:
            print("\nChronicler is thinking...\n")
            
            # Debug logging: Print the exact prompt being sent to OpenAI
            print("\n" + "="*80)
            print("OPENAI API CALL - MAIN INTERVIEW:")
            print("="*80)
            for i, msg in enumerate(messages):
                print(f"\n[{i}] Role: {msg['role']}")
                if isinstance(msg['content'], list):
                    for j, part in enumerate(msg['content']):
                        if part.get('type') == 'text':
                            print(f"    Text: {part['text']}")
                        elif part.get('type') == 'image_url':
                            print(f"    Image: [base64 encoded image data]")
                else:
                    print(f"    Content: {msg['content']}")
            print("="*80 + "\n")
            
            response = openai.chat.completions.create(
                model="gpt-4o-mini", # Or "gpt-4o", "gpt-4-turbo" for more advanced models (higher cost)
                messages=messages,
                max_tokens=500,
            )
            chronicler_question = response.choices[0].message.content
            print(f"\n{chronicler_question}\n")
            
            messages.append({"role": "assistant", "content": chronicler_question})
            store_conversation(chronicler_question, "", role="assistant")

            user_answer = input("Your answer (type 'QUIT' to end session): ").strip()
            if user_answer.lower() == 'quit':
                break
            
            messages.append({"role": "user", "content": user_answer})
            store_conversation("", user_answer, role="user")

        except openai.OpenAIError as e:
            print(f"An OpenAI API error occurred: {e}")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

    print(f"\nInterview session ended. Conversation saved to {os.path.join(OUTPUT_FOLDER, current_interview_filename)}")

if __name__ == "__main__":
    main()