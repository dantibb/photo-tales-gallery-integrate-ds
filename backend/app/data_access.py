import os

if os.environ.get('USE_FIRESTORE', 'False') == 'True':
    from .firestore_db import (
        get_contexts, add_context, update_context, delete_context,
        get_summary, set_summary, clear_all_contexts
    )
    def set_tags(image_name, tags):
        # TODO: Implement Firestore tag storage if needed
        pass
    def get_tags(image_name):
        # TODO: Implement Firestore tag retrieval if needed
        return []
else:
    from .local_db import (
        get_contexts, add_context, update_context, delete_context,
        get_summary, set_summary, clear_all_contexts,
        get_structured_summary, set_structured_summary, set_tags, get_tags
    ) 