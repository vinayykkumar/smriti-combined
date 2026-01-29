"""
Reflection prompt templates.

Builds prompts for generating personalized reflection prompts.
"""

from typing import Optional


def build_reflection_prompt(
    user_context: Optional[str] = None,
    mood: Optional[str] = None,
    additional_context: Optional[str] = None
) -> str:
    """
    Build a prompt for generating personalized reflection prompts.

    Args:
        user_context: Extracted text from user's recent reflections
        mood: User's current mood selection
        additional_context: Any additional context provided by user

    Returns:
        Complete prompt for AI
    """
    base_prompt = """Generate a single reflection prompt for contemplation.

## Guidelines
- The prompt should be a question or gentle invitation to reflect
- It should be open-ended, not leading to a specific answer
- Draw from themes of presence, impermanence, gratitude, or self-inquiry
- Keep it to 1-3 sentences maximum
- Do not use exclamation marks
- End with a question or open invitation
- Do not begin with "Have you considered" or similar phrases"""

    if user_context:
        base_prompt += f"""

## User's Recent Reflections
The person has been exploring these themes in their recent reflections:

{user_context}

Use these themes to personalize the prompt. Notice patterns, recurring questions, or areas of growth. Connect the prompt to their journey without being too explicit about it."""

    if mood:
        mood_guidance = {
            "peaceful": "They are feeling peaceful. Offer something that deepens this stillness.",
            "contemplative": "They are in a contemplative mood. Offer something that invites deeper inquiry.",
            "seeking": "They are seeking something. Offer something that honors this search without rushing toward answers.",
            "grateful": "They are feeling grateful. Offer something that expands this appreciation."
        }
        if mood in mood_guidance:
            base_prompt += f"""

## Current Mood
{mood_guidance[mood]}"""

    if additional_context:
        base_prompt += f"""

## Additional Context
The person shared: "{additional_context}"
Let this inform your prompt without directly addressing it."""

    base_prompt += """

## Output
Respond with ONLY the reflection prompt itself. No introduction, no explanation, just the prompt."""

    return base_prompt


# Fallback prompts when AI is unavailable
FALLBACK_REFLECTION_PROMPTS = [
    "What is asking for your attention in this moment?",
    "If you were to be completely honest with yourself right now, what would you acknowledge?",
    "What would it mean to fully accept where you are, exactly as things are?",
    "Notice your breath. What does it want to tell you?",
    "What are you holding onto that is ready to be released?",
    "Where in your life are you rushing? What would happen if you slowed down?",
    "What small thing are you grateful for that you usually overlook?",
    "What question have you been avoiding?",
    "If this moment were complete in itself, what would you notice?",
    "What does your body know that your mind has forgotten?",
    "What truth is trying to emerge in your life right now?",
    "Where do you find stillness, even in the midst of movement?",
    "What would you do today if you weren't afraid?",
    "What is the quality of your attention right now?",
    "What are you ready to let go of that no longer serves you?"
]
