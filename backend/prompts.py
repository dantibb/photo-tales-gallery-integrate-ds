"""
AI Prompts for the Memory Interview Application

This file contains all the prompts used by the AI interviewer and other AI functions.
Centralizing prompts here makes them easier to find, edit, and maintain.
"""

# =============================================================================
# INTERVIEWER PROMPTS
# =============================================================================

MEMORY_GATHERER_PROMPT = """
You are "Memory Gatherer," an interviewer specializing in finding details and facts about a person. 

Here's how we'll work:
1.  I will provide an image or describe an experience - the image will be one that is relevant to me.
2.  You will ask questions designed to gain information and details about the picture. Aim for one question at a time.
3.  Your first question should be along the lines of 'where was this taken?', 'tell me about this photo.', 'I like this photo of......, is this ......' 
4.  Your questions should focus on finding out facts, locations and dates - as well as details of hobbies, likes and dislikes.
5.  You can ask follow-up questions based on my previous answers to delve deeper.
6.  Remember my previous responses to maintain context and build on our conversation.
7.  Keep your questions conversational and engaging, but focused on gathering specific information.
8.  If I mention something interesting, ask for more details about it.
9.  Your goal is to help me remember and document the story behind this image.

Remember: You are helping me gather memories and details about this image. Be curious, ask specific questions, and help me remember the story behind the photo.
"""

# Keep the old variable for backward compatibility if needed elsewhere
DEFAULT_SYSTEM_PROMPT = MEMORY_GATHERER_PROMPT

# =============================================================================
# SUMMARY PROMPTS
# =============================================================================

SUMMARY_PROMPT_TEMPLATE = """
Write a summary for this image based ONLY on the context information provided below:

Title: <short title with date, location, scene>
Summary: <concise first-person summary matching the context voice and style>

Use exactly these labels: "Title:", "Summary:"
IMPORTANT: Base your summary ONLY on the context information provided. Do not make assumptions about what the image shows.

Context:
{context}
"""

# =============================================================================
# CONTEXT PROMPTS
# =============================================================================

CONTEXT_SUMMARY_TEMPLATE = """Here are some details and context about the image you should use to start the interview:

{context_list}

No additional context provided."""

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_memory_gatherer_prompt():
    """Get the Memory Gatherer system prompt for the interviewer."""
    return MEMORY_GATHERER_PROMPT

# Keep the old function name for backward compatibility
def get_default_system_prompt():
    """Get the default system prompt for the interviewer."""
    return MEMORY_GATHERER_PROMPT

def build_summary_prompt(context_texts, chat_messages=None):
    """
    Build a summary prompt from context texts.
    
    Args:
        context_texts (list): List of context text strings
        chat_messages (list, optional): List of chat message dictionaries (no longer used)
    
    Returns:
        str: Formatted summary prompt
    """
    # Build context section
    if context_texts:
        context_section = "\n".join(f"- {t}" for t in context_texts)
    else:
        context_section = "(No additional context provided.)"
    
    # Return formatted prompt
    return SUMMARY_PROMPT_TEMPLATE.format(
        context=context_section
    )

def build_context_summary(context_texts):
    """
    Build a context summary for starting interviews.
    
    Args:
        context_texts (list): List of context text strings
    
    Returns:
        str: Formatted context summary
    """
    if context_texts:
        context_list = "\n".join(f"- {t}" for t in context_texts)
        return CONTEXT_SUMMARY_TEMPLATE.format(context_list=context_list)
    else:
        return CONTEXT_SUMMARY_TEMPLATE.format(context_list="No additional context provided.") 