"""
Meditation guidance templates.

Builds prompts for generating meditation guidance scripts.
"""


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

    Returns:
        Complete prompt for AI
    """
    type_descriptions = {
        "sankalpam": """Sankalpam Meditation (Intention Setting)

This practice comes from the yogic tradition. Sankalpam means a heartfelt resolve or intention that aligns with one's deepest truth. Unlike a goal, a sankalpam is stated as if already true, planting a seed in consciousness.

The guidance should:
- Begin with settling and arriving
- Guide the practitioner to connect with their heart center
- Invite them to discover (not create) their sankalpam
- Suggest stating the sankalpam internally three times
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
- Leave space for silence between phrases
- Use present tense
- Be warm but not saccharine
- Avoid cliches ("take a deep breath", "let go of stress", "clear your mind")
- Sound natural, not like a meditation app
- No exclamation marks

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

Generate exactly {num_intervals} interval texts."""

    return base_prompt


# Fallback meditation scripts
FALLBACK_MEDITATION = {
    "sankalpam": {
        "opening": "Welcome to this time of intention. Allow your body to settle into stillness. There is nowhere else you need to be.",
        "settling": "Bring your attention to the space of your heart. Not the physical heart, but the center of your being. What lives there?",
        "intervals": [
            "In the quietness, a word or phrase may arise. Your sankalpam. Do not search for it; let it find you.",
            "If your intention has become clear, state it silently to yourself three times, as if it were already true.",
            "Rest now in the resonance of your sankalpam. Let it settle into the depths of your being."
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
