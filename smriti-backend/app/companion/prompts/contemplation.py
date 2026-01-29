"""
Contemplative question templates.

Builds prompts for generating deep contemplative questions.
"""

from typing import Optional


def build_contemplation_prompt(
    category: Optional[str] = None,
    depth: str = "moderate",
    user_context: Optional[str] = None
) -> str:
    """
    Build a prompt for generating contemplative questions.

    Args:
        category: Question category (self, relationships, purpose, presence, gratitude)
        depth: Question depth (gentle, moderate, deep)
        user_context: Optional context from user's reflections

    Returns:
        Complete prompt for AI
    """
    category_guidance = {
        "self": "Focus on self-inquiry, identity, inner nature, and the question of 'who am I'",
        "relationships": "Focus on connection, love, boundaries, forgiveness, and how we relate to others",
        "purpose": "Focus on meaning, calling, contribution, and what matters most",
        "presence": "Focus on awareness, attention, the present moment, and direct experience",
        "gratitude": "Focus on appreciation, blessing, abundance, and recognizing gifts"
    }

    depth_guidance = {
        "gentle": "Make the question accessible and inviting. It should feel safe to approach.",
        "moderate": "The question can probe a bit deeper, inviting more sustained reflection.",
        "deep": "This question should touch something fundamental. It may be uncomfortable to sit with."
    }

    base_prompt = f"""Generate a contemplative question for deep reflection.

## Category
{category_guidance.get(category, "Any area of life and inner experience")}

## Depth
{depth_guidance.get(depth, depth_guidance["moderate"])}

## Guidelines
- The question should invite genuine inquiry, not have an obvious answer
- It should be something worth sitting with for a while
- Avoid questions that can be answered with simple facts
- The question should open up exploration, not close it down
- Use simple, direct language
- Do not begin with "Have you ever" or similar cliches"""

    if user_context:
        base_prompt += f"""

## User's Journey
Their recent reflections touch on these themes:
{user_context}

Let this inform the question subtly, without directly referencing their writings."""

    base_prompt += """

## Output Format
Respond with a JSON object:
{
    "question": "The main contemplative question",
    "follow_ups": [
        "A follow-up question that goes deeper",
        "Another angle on the same inquiry"
    ]
}

The main question should be 1-2 sentences. Follow-ups should be shorter."""

    return base_prompt


# Fallback questions by category
FALLBACK_QUESTIONS = {
    "self": [
        "Who are you when you are not playing any role?",
        "What would you do if you knew you could not fail?",
        "What part of yourself have you exiled?",
        "What masks do you wear, and what do they protect?",
        "If you met your younger self, what would you say?"
    ],
    "relationships": [
        "What do you need to forgive—in others or yourself?",
        "Who have you not truly seen?",
        "What truth have you withheld from someone you love?",
        "Where do you give to receive?",
        "What relationship is asking you to grow?"
    ],
    "purpose": [
        "What would you do even if no one ever knew?",
        "What breaks your heart about the world?",
        "What gift are you afraid to give?",
        "When do you feel most alive?",
        "What would you regret not having done?"
    ],
    "presence": [
        "What is here right now, beneath all thought?",
        "If this were your last moment, what would matter?",
        "What are you resisting in this very moment?",
        "Where does your attention naturally want to rest?",
        "What would you notice if you truly stopped?"
    ],
    "gratitude": [
        "What blessing have you taken for granted?",
        "What difficulty has secretly served you?",
        "What ordinary thing is actually extraordinary?",
        "Who has shaped you that you've never thanked?",
        "What gift have you received today?"
    ]
}
