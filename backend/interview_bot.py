from firestore_db import FirestoreDB

# You can later expand this to use a real AI model for more advanced interviewing

def run_interview(media_id: str, user_input: str, context_type: str = 'interview'):
    """
    Store the user's answer as a context entry for the given media item.
    """
    db = FirestoreDB()
    context_id = db.add_context(media_id, user_input, context_type=context_type)
    return context_id 