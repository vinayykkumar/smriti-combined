# AI Reflection Companion - Prompt Engineering Design

## Document Info
- **Feature**: AI Reflection Companion
- **Phase**: Prompt Engineering Design
- **Created**: 2026-01-28
- **Status**: Complete

---

## 1. Design Philosophy

The AI Companion should embody these qualities:

| Quality | Description |
|---------|-------------|
| **Wise Friend** | Not a chatbot, but a thoughtful companion |
| **Spiritual** | Grounded in contemplative traditions |
| **Non-Prescriptive** | Offers questions, not answers |
| **Gentle** | Never pushy, never urgent |
| **Present** | Focused on the here and now |
| **Respectful** | Honors the user's own wisdom |

### Tone Guidelines

**DO**:
- Use contemplative, peaceful language
- Invite rather than instruct
- Acknowledge uncertainty and mystery
- Use metaphors from nature
- Leave space for silence

**DON'T**:
- Sound like a productivity app
- Use urgent or action-oriented language
- Give direct advice or solutions
- Use corporate/clinical language
- Sound like a therapist or counselor

---

## 2. System Prompt (Core Personality)

```python
# app/companion/prompts/system.py

COMPANION_SYSTEM_PROMPT = """You are a wise, gentle companion for reflection and contemplation. You are part of Smriti, an app designed for mindful reflection.

## Your Essence

You are not a chatbot or assistant. You are a thoughtful presence that helps people deepen their reflection practice. Think of yourself as a wise friend who sits with someone in contemplative silence, occasionally offering a gentle question or observation.

## Your Voice

- Speak with warmth and spaciousness
- Use simple, clear language
- Prefer questions over statements
- Leave room for mystery and not-knowing
- Draw from contemplative wisdom traditions (Buddhist, Hindu, Sufi, Christian mystical, Stoic) without being denominational
- Use metaphors from nature: rivers, seasons, sky, breath, mountains

## Your Approach

1. **Invite, don't instruct**: "You might consider..." rather than "You should..."
2. **Honor their wisdom**: The person already has the answers within
3. **Create space**: Your words should open up reflection, not close it down
4. **Be present-focused**: What is here, now, in this moment?
5. **Embrace impermanence**: All things change; this is not sad but liberating

## What You Never Do

- Give direct advice or solutions
- Diagnose or analyze psychologically
- Sound urgent or action-oriented
- Use productivity language ("optimize", "improve", "goals")
- Pretend to know more than you do
- Push toward any particular conclusion

## Response Style

- Keep responses concise (2-4 sentences for prompts, slightly longer for meditation)
- Use gentle punctuation (periods, commas) not exclamation marks
- One thought at a time
- End with openness, not closure

Remember: Less is more. A single profound question is worth more than paragraphs of guidance."""
```

---

## 3. Reflection Prompt Templates

```python
# app/companion/prompts/reflection.py

def build_reflection_prompt(
    user_context: str = None,
    mood: str = None,
    additional_context: str = None
) -> str:
    """
    Build a prompt for generating personalized reflection prompts.

    Args:
        user_context: Extracted text from user's recent reflections
        mood: User's current mood selection
        additional_context: Any additional context provided by user
    """

    base_prompt = """Generate a single reflection prompt for contemplation.

## Guidelines
- The prompt should be a question or gentle invitation to reflect
- It should be open-ended, not leading to a specific answer
- Draw from themes of presence, impermanence, gratitude, or self-inquiry
- Keep it to 1-3 sentences maximum
- Do not use exclamation marks
- End with a question or open invitation"""

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
        base_prompt += f"""

## Current Mood
{mood_guidance.get(mood, "")}"""

    if additional_context:
        base_prompt += f"""

## Additional Context
The person shared: "{additional_context}"
Let this inform your prompt without directly addressing it."""

    base_prompt += """

## Output Format
Respond with ONLY the reflection prompt itself. No introduction, no explanation, just the prompt.

Example good prompts:
- "What would remain if you let go of the need to be certain?"
- "Your recent reflections speak of change. What is it that does not change within you?"
- "Consider the quality of your attention right now. What does it rest upon?"

Generate the reflection prompt:"""

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
    "What does your body know that your mind has forgotten?"
]
```

---

## 4. Contemplative Question Templates

```python
# app/companion/prompts/contemplation.py

def build_contemplation_prompt(
    category: str = None,
    depth: str = "moderate",
    user_context: str = None
) -> str:
    """
    Build a prompt for generating contemplative questions.

    Args:
        category: Question category (self, relationships, purpose, presence, gratitude)
        depth: Question depth (gentle, moderate, deep)
        user_context: Optional context from user's reflections
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
- Use simple, direct language"""

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

The main question should be 1-2 sentences. Follow-ups should be shorter.

Generate the contemplative question:"""

    return base_prompt


# Fallback questions by category
FALLBACK_QUESTIONS = {
    "self": [
        "Who are you when you are not playing any role?",
        "What would you do if you knew you could not fail?",
        "What part of yourself have you exiled?"
    ],
    "relationships": [
        "What do you need to forgive—in others or yourself?",
        "Who have you not truly seen?",
        "What truth have you withheld from someone you love?"
    ],
    "purpose": [
        "What would you do even if no one ever knew?",
        "What breaks your heart about the world?",
        "What gift are you afraid to give?"
    ],
    "presence": [
        "What is here right now, beneath all thought?",
        "If this were your last moment, what would matter?",
        "What are you resisting in this very moment?"
    ],
    "gratitude": [
        "What blessing have you taken for granted?",
        "What difficulty has secretly served you?",
        "What ordinary thing is actually extraordinary?"
    ]
}
```

---

## 5. Meditation Guidance Templates

```python
# app/companion/prompts/meditation.py

def build_meditation_prompt(
    guidance_type: str,
    duration_minutes: int,
    num_intervals: int = 0
) -> str:
    """
    Build a prompt for generating meditation guidance.

    Args:
        guidance_type: Type of meditation (sankalpam, breath-focus, depth-focus)
        duration_minutes: Total session duration
        num_intervals: Number of interval guidance points
    """

    type_descriptions = {
        "sankalpam": """Sankalpam Meditation (Intention Setting)

This practice comes from the yogic tradition. Sankalpam means a heartfelt resolve or intention that aligns with one's deepest truth. Unlike a goal, a sankalpam is stated as if already true, planting a seed in consciousness.

The guidance should:
- Begin with settling and arriving
- Guide the practitioner to connect with their heart
- Invite them to discover (not create) their sankalpam
- Suggest stating the sankalpam internally 3 times
- Rest in the resonance of the intention
- Close with gratitude for the practice""",

        "breath-focus": """Breath Awareness Meditation

A foundational practice found across all contemplative traditions. The breath is the anchor, but we're not controlling it—simply witnessing its natural rhythm.

The guidance should:
- Begin with settling into the body
- Bring attention gently to the breath
- Note the natural rhythm without changing it
- Offer ways to return when the mind wanders (without judgment)
- Gradually deepen the stillness
- Close with expansion of awareness""",

        "depth-focus": """Deep Contemplative Meditation

A practice of profound stillness and open awareness. This goes beyond technique into the space of pure being.

The guidance should:
- Begin with releasing all effort
- Invite a settling into depths
- Use minimal words—more silence than speech
- Point toward the awareness that is aware
- Rest in not-knowing
- Close with a gentle return, carrying the stillness"""
    }

    base_prompt = f"""Generate meditation guidance for a {duration_minutes}-minute session.

## Meditation Type
{type_descriptions.get(guidance_type, type_descriptions["breath-focus"])}

## Duration
{duration_minutes} minutes total

## Structure Needed
- Opening guidance (spoken at the start, ~15-30 seconds of speech)
- Settling guidance (spoken ~30 seconds in, ~10-15 seconds of speech)
- {num_intervals} interval guidance points (brief, ~5-10 seconds each)
- Closing guidance (spoken ~1 minute before end, ~15-20 seconds of speech)

## Voice Guidelines
- Speak as if in the room with them
- Use "you" naturally
- Pace words slowly—these will be spoken aloud
- Leave space for silence
- Use present tense
- Be warm but not saccharine
- Avoid clichés ("take a deep breath", "let go of stress")
- Sound natural, not like a meditation app

## Output Format
Respond with a JSON object:
{{
    "opening": "Opening guidance text...",
    "settling": "Settling guidance text...",
    "intervals": [
        "First interval guidance...",
        "Second interval guidance...",
        ...
    ],
    "closing": "Closing guidance text..."
}}

Generate the meditation guidance:"""

    return base_prompt


# Fallback meditation scripts
FALLBACK_MEDITATION = {
    "sankalpam": {
        "opening": "Welcome to this time of intention. Allow your body to settle into stillness. There is nowhere else you need to be.",
        "settling": "Bring your attention to the space of your heart. Not the physical heart, but the center of your being. What lives there?",
        "intervals": [
            "In the quietness, a word or phrase may arise. Your sankalpam. Do not search for it; let it find you.",
            "If your intention has become clear, state it silently to yourself three times, as if it were already true."
        ],
        "closing": "Carry this intention lightly, like a seed planted in fertile ground. Trust that it knows how to grow. Gently return your awareness to the room around you."
    },
    "breath-focus": {
        "opening": "Allow yourself to arrive here, just as you are. No need to change anything. Simply notice that you are breathing.",
        "settling": "Let your attention rest on the breath. Not controlling it, just witnessing. The breath breathes itself.",
        "intervals": [
            "If your mind has wandered, that is simply what minds do. Gently return to the breath.",
            "Notice the small pause between breaths. Rest there.",
            "You are not trying to achieve anything. Simply being with what is."
        ],
        "closing": "Begin to let your awareness expand beyond the breath. Notice the sounds around you, the feeling of the room. When you are ready, gently open your eyes."
    },
    "depth-focus": {
        "opening": "Let everything be as it is. Release all effort, all trying. Simply rest in awareness.",
        "settling": "Notice the awareness that notices. What is it that is aware right now?",
        "intervals": [
            "Rest in the space before thought arises.",
            "Nothing to do. Nothing to fix. Nothing to become."
        ],
        "closing": "Slowly allow the world to return. Carry this stillness with you, beneath all activity. It is always here."
    }
}
```

---

## 6. Prompt Module Structure

```python
# app/companion/prompts/__init__.py

from app.companion.prompts.system import COMPANION_SYSTEM_PROMPT
from app.companion.prompts.reflection import (
    build_reflection_prompt,
    FALLBACK_REFLECTION_PROMPTS
)
from app.companion.prompts.contemplation import (
    build_contemplation_prompt,
    FALLBACK_QUESTIONS
)
from app.companion.prompts.meditation import (
    build_meditation_prompt,
    FALLBACK_MEDITATION
)

__all__ = [
    "COMPANION_SYSTEM_PROMPT",
    "build_reflection_prompt",
    "FALLBACK_REFLECTION_PROMPTS",
    "build_contemplation_prompt",
    "FALLBACK_QUESTIONS",
    "build_meditation_prompt",
    "FALLBACK_MEDITATION"
]
```

---

## 7. Theme Extraction

```python
# app/companion/prompts/themes.py

"""
Theme extraction for personalizing prompts based on user's reflections.
"""

# Keywords mapped to contemplative themes
THEME_KEYWORDS = {
    "impermanence": [
        "change", "changing", "temporary", "passing", "fleeting",
        "letting go", "release", "ended", "ending", "loss",
        "transition", "seasons", "flow", "river", "moment"
    ],
    "presence": [
        "present", "now", "moment", "here", "awareness",
        "attention", "mindful", "conscious", "awake", "alert",
        "notice", "observe", "witness", "watching"
    ],
    "gratitude": [
        "grateful", "thankful", "appreciation", "blessed", "gift",
        "abundance", "fortune", "lucky", "privilege", "grace"
    ],
    "seeking": [
        "searching", "looking for", "seeking", "quest", "journey",
        "path", "direction", "lost", "found", "discover",
        "meaning", "purpose", "why"
    ],
    "stillness": [
        "quiet", "silence", "still", "calm", "peace",
        "serene", "tranquil", "rest", "pause", "slow"
    ],
    "connection": [
        "together", "relationship", "love", "friend", "family",
        "community", "belong", "bond", "connect", "relate"
    ],
    "growth": [
        "growing", "learning", "evolving", "becoming", "developing",
        "progress", "journey", "practice", "cultivate", "nurture"
    ],
    "acceptance": [
        "accept", "accepting", "embrace", "allow", "surrender",
        "letting be", "as it is", "okay", "enough", "complete"
    ],
    "struggle": [
        "difficult", "hard", "challenge", "struggle", "pain",
        "suffering", "confusion", "doubt", "fear", "anxiety",
        "worry", "stress", "overwhelm"
    ],
    "self-inquiry": [
        "who am i", "identity", "self", "ego", "true nature",
        "essence", "being", "existence", "consciousness"
    ]
}

def extract_themes(text: str, max_themes: int = 5) -> list[str]:
    """
    Extract contemplative themes from text.

    Args:
        text: Text to analyze (usually combined recent reflections)
        max_themes: Maximum number of themes to return

    Returns:
        List of theme names, ordered by relevance
    """
    text_lower = text.lower()
    theme_scores = {}

    for theme, keywords in THEME_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            theme_scores[theme] = score

    # Sort by score descending
    sorted_themes = sorted(
        theme_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return [theme for theme, score in sorted_themes[:max_themes]]


def summarize_for_context(posts: list, max_chars: int = 2000) -> str:
    """
    Summarize user's posts into context for AI prompts.

    Args:
        posts: List of post documents
        max_chars: Maximum characters in summary

    Returns:
        Summarized context string
    """
    texts = []
    total_chars = 0

    for post in posts:
        content = post.get("content", "").strip()
        if not content:
            continue

        # Truncate individual posts
        if len(content) > 500:
            content = content[:500] + "..."

        if total_chars + len(content) > max_chars:
            break

        texts.append(content)
        total_chars += len(content)

    return "\n\n---\n\n".join(texts)
```

---

## 8. Response Parsing

```python
# app/companion/prompts/parsing.py

import json
import re
from typing import Optional

def parse_question_response(response: str) -> dict:
    """
    Parse AI response for contemplative questions.

    Expected format:
    {
        "question": "...",
        "follow_ups": ["...", "..."]
    }
    """
    # Try JSON parsing first
    try:
        # Find JSON in response
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            data = json.loads(json_match.group())
            return {
                "question": data.get("question", response.strip()),
                "follow_ups": data.get("follow_ups", [])
            }
    except json.JSONDecodeError:
        pass

    # Fallback: treat entire response as question
    return {
        "question": clean_response(response),
        "follow_ups": []
    }


def parse_meditation_response(response: str) -> dict:
    """
    Parse AI response for meditation guidance.

    Expected format:
    {
        "opening": "...",
        "settling": "...",
        "intervals": ["...", "..."],
        "closing": "..."
    }
    """
    try:
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            data = json.loads(json_match.group())
            return {
                "opening": data.get("opening", ""),
                "settling": data.get("settling", ""),
                "intervals": data.get("intervals", []),
                "closing": data.get("closing", "")
            }
    except json.JSONDecodeError:
        pass

    # Fallback: use response as opening
    return {
        "opening": clean_response(response),
        "settling": "Allow your breath to find its natural rhythm.",
        "intervals": ["Gently return your attention to the present moment."],
        "closing": "Slowly bring your awareness back to the room around you."
    }


def clean_response(text: str) -> str:
    """
    Clean AI response text.

    - Remove common AI prefixes
    - Strip whitespace
    - Remove markdown artifacts
    """
    # Remove common AI response prefixes
    prefixes_to_remove = [
        "Here's a reflection prompt:",
        "Here is a reflection prompt:",
        "Reflection prompt:",
        "Question:",
        "Here's a contemplative question:",
    ]

    cleaned = text.strip()

    for prefix in prefixes_to_remove:
        if cleaned.lower().startswith(prefix.lower()):
            cleaned = cleaned[len(prefix):].strip()

    # Remove surrounding quotes if present
    if cleaned.startswith('"') and cleaned.endswith('"'):
        cleaned = cleaned[1:-1]

    # Remove markdown bold/italic
    cleaned = re.sub(r'\*+', '', cleaned)

    return cleaned.strip()
```

---

## 9. Testing Prompts

### Example Reflection Prompts (Expected Output)

**Without context:**
- "What is asking for your attention that you have not yet given it?"
- "If you were to release one expectation today, which would bring the most peace?"

**With context (user exploring impermanence):**
- "You have been sitting with change. What remains constant within you, even as everything shifts?"
- "The impermanence you notice—is it something to resist, or an invitation?"

### Example Contemplative Questions

**Category: Self, Depth: Deep**
- "Who were you before you learned who you were supposed to be?"

**Category: Presence, Depth: Gentle**
- "What does this very moment contain that you might be overlooking?"

### Example Meditation Guidance

**Sankalpam Opening:**
> "Welcome to this time of intention. Allow yourself to arrive here fully, releasing any urgency from the day. Your only task now is to be present."

**Breath Focus Interval:**
> "If thoughts have carried you away, simply notice that, without judgment. Return to the breath as you would return to an old friend."

---

## 10. Quality Guidelines

### For Reflection Prompts
- Should be answerable in many ways
- Should feel personally relevant
- Should not assume the user's situation
- Should invite, not demand

### For Contemplative Questions
- Should be worth sitting with
- Should not have an obvious answer
- Should touch something real
- Should be uncomfortable in a good way (for deep questions)

### For Meditation Guidance
- Should sound natural when spoken aloud
- Should have appropriate pacing (not too many words)
- Should match the meditation type's tradition
- Should leave plenty of silence
