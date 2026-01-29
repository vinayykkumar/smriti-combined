"""
Response parsing utilities for AI companion.

Handles parsing of AI responses into structured data,
with fallback handling for malformed responses.
"""

import json
import re
from typing import Optional


def clean_response(text: str) -> str:
    """
    Clean AI response text.

    - Remove common AI prefixes
    - Strip whitespace
    - Remove markdown artifacts
    - Remove surrounding quotes

    Args:
        text: Raw AI response text

    Returns:
        Cleaned text
    """
    if not text:
        return text

    # Remove common AI response prefixes
    prefixes_to_remove = [
        "Here's a reflection prompt:",
        "Here is a reflection prompt:",
        "Reflection prompt:",
        "Question:",
        "Here's a contemplative question:",
        "Here is a contemplative question:",
        "Contemplative question:",
        "Here's your prompt:",
        "Sure, here's a prompt:",
    ]

    cleaned = text.strip()

    for prefix in prefixes_to_remove:
        if cleaned.lower().startswith(prefix.lower()):
            cleaned = cleaned[len(prefix):].strip()

    # Remove surrounding quotes if present
    if cleaned.startswith('"') and cleaned.endswith('"'):
        cleaned = cleaned[1:-1]
    if cleaned.startswith("'") and cleaned.endswith("'"):
        cleaned = cleaned[1:-1]

    # Remove markdown bold/italic but preserve text
    cleaned = re.sub(r'\*\*([^*]+)\*\*', r'\1', cleaned)  # **bold**
    cleaned = re.sub(r'\*([^*]+)\*', r'\1', cleaned)      # *italic*
    cleaned = re.sub(r'__([^_]+)__', r'\1', cleaned)      # __bold__
    cleaned = re.sub(r'_([^_]+)_', r'\1', cleaned)        # _italic_

    return cleaned.strip()


def parse_question_response(response: str) -> dict:
    """
    Parse AI response for contemplative questions.

    Expected format:
    {
        "question": "...",
        "follow_ups": ["...", "..."]
    }

    Args:
        response: Raw AI response

    Returns:
        Dict with 'question' and 'follow_ups' keys
    """
    # Try JSON parsing first
    try:
        # Find JSON object in response (may have surrounding text)
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            data = json.loads(json_match.group())
            question = data.get("question", "").strip()
            follow_ups = data.get("follow_ups", [])

            # Validate question exists
            if question:
                return {
                    "question": clean_response(question),
                    "follow_ups": [clean_response(f) for f in follow_ups if f]
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

    Args:
        response: Raw AI response

    Returns:
        Dict with meditation guidance sections
    """
    try:
        # Find JSON object in response
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            data = json.loads(json_match.group())

            # Validate required fields
            opening = data.get("opening", "").strip()
            if opening:
                return {
                    "opening": clean_response(opening),
                    "settling": clean_response(data.get("settling", "")),
                    "intervals": [clean_response(i) for i in data.get("intervals", []) if i],
                    "closing": clean_response(data.get("closing", ""))
                }
    except json.JSONDecodeError:
        pass

    # Fallback: use response as opening, provide defaults for rest
    return {
        "opening": clean_response(response),
        "settling": "Allow your breath to find its natural rhythm.",
        "intervals": ["Gently return your attention to the present moment."],
        "closing": "Slowly bring your awareness back to the room around you."
    }


def extract_json_safely(text: str) -> Optional[dict]:
    """
    Safely extract JSON from text that may contain other content.

    Args:
        text: Text that may contain JSON

    Returns:
        Parsed dict or None if no valid JSON found
    """
    try:
        # Try direct parsing first
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON object
    try:
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            return json.loads(json_match.group())
    except json.JSONDecodeError:
        pass

    # Try to find JSON array
    try:
        json_match = re.search(r'\[[\s\S]*\]', text)
        if json_match:
            return json.loads(json_match.group())
    except json.JSONDecodeError:
        pass

    return None
