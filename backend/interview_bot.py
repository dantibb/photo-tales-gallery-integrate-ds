from app.enhanced_data_store import EnhancedDataStore
import openai
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='config.env')

# Lazy-load the database connection to avoid circular dependency issues
_db = None

def get_db():
    global _db
    if _db is None:
        _db = EnhancedDataStore()
    return _db

# You can later expand this to use a real AI model for more advanced interviewing

def run_interview(media_id: str, user_input: str, context_type: str = 'interview'):
    """
    Store the user's answer as a context entry for the given media item.
    """
    db = get_db()
    context_id = db.add_context(media_id, user_input, context_type=context_type)
    return context_id 