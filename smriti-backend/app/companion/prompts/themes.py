"""
Theme extraction and pattern identification utilities.

Extracts contemplative themes from user's reflections
and identifies emotional/reflective patterns for AI context.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass


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

# Keywords for emotional tone detection
EMOTIONAL_KEYWORDS = {
    "positive": [
        "happy", "joy", "peace", "calm", "grateful", "blessed",
        "content", "fulfilled", "hopeful", "inspired", "light",
        "free", "open", "clear", "serene", "warm", "love"
    ],
    "contemplative": [
        "wondering", "curious", "pondering", "reflecting", "thinking",
        "considering", "exploring", "inquiring", "questioning"
    ],
    "struggling": [
        "anxious", "worried", "stressed", "overwhelmed", "confused",
        "lost", "sad", "heavy", "difficult", "hard", "painful",
        "fear", "doubt", "uncertain", "stuck"
    ],
    "seeking": [
        "searching", "seeking", "looking", "wanting", "needing",
        "longing", "hoping", "wishing", "yearning"
    ]
}


@dataclass
class ReflectionPatterns:
    """
    Identified patterns from user's reflections.

    Used to provide richer context for AI personalization.
    """
    themes: List[str]
    emotional_tone: str
    recurring_concerns: List[str]
    growth_indicators: List[str]
    summary: str


def extract_themes(text: str, max_themes: int = 5) -> List[str]:
    """
    Extract contemplative themes from text.

    Uses keyword matching to identify themes present in the text.
    Simple but effective for personalization.

    Args:
        text: Text to analyze (usually combined recent reflections)
        max_themes: Maximum number of themes to return

    Returns:
        List of theme names, ordered by relevance (most matches first)
    """
    if not text:
        return []

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


def detect_emotional_tone(text: str) -> str:
    """
    Detect the overall emotional tone of reflections.

    Args:
        text: Combined text from user's reflections

    Returns:
        Emotional tone: 'positive', 'contemplative', 'struggling', 'seeking', or 'neutral'
    """
    if not text:
        return "neutral"

    text_lower = text.lower()
    tone_scores = {}

    for tone, keywords in EMOTIONAL_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            tone_scores[tone] = score

    if not tone_scores:
        return "neutral"

    # Return the dominant tone
    return max(tone_scores.items(), key=lambda x: x[1])[0]


def identify_recurring_concerns(posts: List[dict]) -> List[str]:
    """
    Identify concerns that appear across multiple reflections.

    Args:
        posts: List of post documents with 'content' field

    Returns:
        List of recurring concerns/themes
    """
    if not posts or len(posts) < 2:
        return []

    # Count theme occurrences across posts
    theme_occurrences = {}

    for post in posts:
        content = post.get("content", "")
        if not content:
            continue

        post_themes = extract_themes(content, max_themes=3)
        for theme in post_themes:
            theme_occurrences[theme] = theme_occurrences.get(theme, 0) + 1

    # A concern is "recurring" if it appears in at least 30% of posts
    threshold = max(2, len(posts) * 0.3)
    recurring = [
        theme for theme, count in theme_occurrences.items()
        if count >= threshold
    ]

    return recurring[:3]  # Return top 3 recurring concerns


def identify_growth_indicators(posts: List[dict]) -> List[str]:
    """
    Identify signs of growth or positive change in reflections.

    Looks for progression from struggle to acceptance,
    or deepening of contemplative practice.

    Args:
        posts: List of post documents (most recent first)

    Returns:
        List of growth indicators observed
    """
    if not posts or len(posts) < 3:
        return []

    growth_indicators = []
    growth_keywords = {
        "awareness_growth": [
            "realized", "noticed", "became aware", "understand now",
            "see now", "clarity", "insight"
        ],
        "acceptance_growth": [
            "accepting", "letting go", "release", "surrendering",
            "making peace", "okay with"
        ],
        "practice_deepening": [
            "daily practice", "regular", "consistent", "deeper",
            "more often", "returning to"
        ],
        "gratitude_emergence": [
            "grateful", "thankful", "appreciate", "blessed"
        ]
    }

    # Check recent posts (first half) vs older posts (second half)
    mid = len(posts) // 2
    recent_text = " ".join(p.get("content", "") for p in posts[:mid]).lower()
    older_text = " ".join(p.get("content", "") for p in posts[mid:]).lower()

    for indicator, keywords in growth_keywords.items():
        recent_count = sum(1 for kw in keywords if kw in recent_text)
        older_count = sum(1 for kw in keywords if kw in older_text)

        # If recent reflections show more of this indicator
        if recent_count > older_count:
            indicator_name = indicator.replace("_", " ").title()
            growth_indicators.append(indicator_name)

    return growth_indicators[:3]


def analyze_reflection_patterns(posts: List[dict]) -> ReflectionPatterns:
    """
    Comprehensive analysis of user's reflection patterns.

    Combines theme extraction, emotional tone detection,
    and pattern identification into a single analysis.

    Args:
        posts: List of post documents with 'content' field

    Returns:
        ReflectionPatterns with all identified patterns
    """
    if not posts:
        return ReflectionPatterns(
            themes=[],
            emotional_tone="neutral",
            recurring_concerns=[],
            growth_indicators=[],
            summary=""
        )

    # Combine all text
    all_text = " ".join(p.get("content", "") for p in posts)

    # Extract various patterns
    themes = extract_themes(all_text)
    emotional_tone = detect_emotional_tone(all_text)
    recurring = identify_recurring_concerns(posts)
    growth = identify_growth_indicators(posts)

    # Build human-readable summary for AI context
    summary_parts = []

    if themes:
        summary_parts.append(f"exploring themes of {', '.join(themes[:3])}")

    if emotional_tone != "neutral":
        tone_descriptions = {
            "positive": "in a place of peace and gratitude",
            "contemplative": "in a space of deep inquiry",
            "struggling": "working through some challenges",
            "seeking": "searching for meaning or direction"
        }
        summary_parts.append(tone_descriptions.get(emotional_tone, ""))

    if recurring:
        summary_parts.append(f"with recurring attention to {', '.join(recurring)}")

    if growth:
        summary_parts.append(f"showing signs of {', '.join(growth).lower()}")

    summary = "; ".join(part for part in summary_parts if part)

    return ReflectionPatterns(
        themes=themes,
        emotional_tone=emotional_tone,
        recurring_concerns=recurring,
        growth_indicators=growth,
        summary=summary
    )


def summarize_posts_for_context(
    posts: List[dict],
    max_chars: int = 2000,
    max_post_length: int = 500
) -> str:
    """
    Summarize user's posts into context for AI prompts.

    Combines recent post content into a single context string,
    respecting character limits.

    Args:
        posts: List of post documents (should have 'content' field)
        max_chars: Maximum total characters in summary
        max_post_length: Maximum characters per individual post

    Returns:
        Summarized context string
    """
    if not posts:
        return ""

    texts = []
    total_chars = 0

    for post in posts:
        content = post.get("content", "").strip()
        if not content:
            continue

        # Truncate individual posts
        if len(content) > max_post_length:
            content = content[:max_post_length] + "..."

        # Check if adding this would exceed limit
        if total_chars + len(content) > max_chars:
            break

        texts.append(content)
        total_chars += len(content)

    if not texts:
        return ""

    return "\n\n---\n\n".join(texts)


def build_personalized_context(posts: List[dict]) -> Optional[str]:
    """
    Build a rich personalized context string for AI prompts.

    Combines summarized posts with pattern analysis.

    Args:
        posts: List of user's recent posts

    Returns:
        Formatted context string or None if no posts
    """
    if not posts:
        return None

    # Get patterns analysis
    patterns = analyze_reflection_patterns(posts)

    # Get summarized content
    content_summary = summarize_posts_for_context(posts, max_chars=1500)

    # Build context
    context_parts = []

    if patterns.summary:
        context_parts.append(f"This person is {patterns.summary}.")

    if content_summary:
        context_parts.append(f"\nRecent reflections:\n{content_summary}")

    if not context_parts:
        return None

    return "\n".join(context_parts)


def get_theme_description(theme: str) -> str:
    """
    Get a human-readable description of a theme.

    Args:
        theme: Theme name

    Returns:
        Description of the theme
    """
    descriptions = {
        "impermanence": "exploring change and the transient nature of things",
        "presence": "cultivating awareness of the present moment",
        "gratitude": "appreciating the blessings in life",
        "seeking": "searching for meaning and direction",
        "stillness": "finding peace and quiet within",
        "connection": "nurturing relationships and belonging",
        "growth": "evolving and developing as a person",
        "acceptance": "embracing things as they are",
        "struggle": "working through challenges and difficulties",
        "self-inquiry": "exploring questions of identity and self"
    }
    return descriptions.get(theme, theme)
