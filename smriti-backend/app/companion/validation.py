"""
Response validation for AI Companion.

Ensures AI responses are appropriate, spiritual in tone,
and don't contain inappropriate advice or content.
"""

import re
from typing import Tuple, List
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of response validation."""
    is_valid: bool
    issues: List[str]
    severity: str  # 'none', 'warning', 'error'


# Red flags that should cause rejection
RED_FLAG_PHRASES = [
    # Medical/Psychological advice
    "you should immediately",
    "you must urgently",
    "seek professional help",
    "see a doctor",
    "see a therapist",
    "i diagnose",
    "as your therapist",
    "you have depression",
    "you have anxiety",
    "this sounds like",
    "medication",
    "treatment plan",

    # Urgent/Crisis language
    "emergency",
    "crisis hotline",
    "call 911",
    "danger to yourself",
    "suicidal",

    # Inappropriate AI self-reference
    "as an ai",
    "i am an ai",
    "i'm an artificial",
    "as a language model",

    # Advice-giving
    "you should",
    "you must",
    "you need to",
    "you have to",
    "my advice is",
    "i advise you",
    "i recommend that you",

    # Productivity language (not in line with app philosophy)
    "optimize",
    "maximize",
    "increase your productivity",
    "goal setting",
    "achieve your goals",
    "action items",
    "to-do list",
]

# Warning phrases that may be okay in context but worth checking
WARNING_PHRASES = [
    # Could be okay depending on context
    "professional",
    "help",
    "support",
    "consider talking to",

    # Slightly too directive
    "try to",
    "make sure",
    "don't forget",

    # Not contemplative enough
    "tips",
    "strategies",
    "techniques",
    "steps",
]

# Phrases that indicate good spiritual/contemplative content
POSITIVE_INDICATORS = [
    "notice",
    "observe",
    "allow",
    "what if",
    "consider",
    "perhaps",
    "might",
    "wonder",
    "breath",
    "present",
    "moment",
    "stillness",
    "awareness",
    "gentle",
    "softly",
    "rest",
    "sit with",
    "explore",
    "inquire",
]


def validate_response(response: str) -> ValidationResult:
    """
    Validate that an AI response meets quality standards.

    Checks for:
    - Presence of content
    - Absence of red flag phrases
    - Warning phrases (noted but not rejected)
    - Presence of contemplative indicators

    Args:
        response: The AI-generated response

    Returns:
        ValidationResult with validity, issues, and severity
    """
    if not response or not response.strip():
        return ValidationResult(
            is_valid=False,
            issues=["Response is empty"],
            severity="error"
        )

    response_lower = response.lower()
    issues = []

    # Check for red flags (immediate rejection)
    for phrase in RED_FLAG_PHRASES:
        if phrase in response_lower:
            issues.append(f"Contains red flag phrase: '{phrase}'")

    if issues:
        return ValidationResult(
            is_valid=False,
            issues=issues,
            severity="error"
        )

    # Check for warnings (allow but note)
    warnings = []
    for phrase in WARNING_PHRASES:
        if phrase in response_lower:
            warnings.append(f"Contains potentially inappropriate phrase: '{phrase}'")

    # Check for positive indicators (good sign)
    positive_count = sum(1 for phrase in POSITIVE_INDICATORS if phrase in response_lower)

    # Determine severity
    if warnings and positive_count < 2:
        return ValidationResult(
            is_valid=True,  # Allow but with warnings
            issues=warnings,
            severity="warning"
        )

    return ValidationResult(
        is_valid=True,
        issues=[],
        severity="none"
    )


def validate_reflection_prompt(prompt: str) -> ValidationResult:
    """
    Validate a reflection prompt specifically.

    Additional checks:
    - Should be a question or invitation
    - Should not be too long
    - Should not start with "I"

    Args:
        prompt: The generated reflection prompt

    Returns:
        ValidationResult
    """
    # First do general validation
    result = validate_response(prompt)
    if not result.is_valid:
        return result

    issues = list(result.issues)

    # Check length (prompts should be concise)
    if len(prompt) > 500:
        issues.append("Prompt is too long (over 500 characters)")

    # Check it's a question or invitation
    prompt_lower = prompt.lower().strip()
    if not (
        prompt.strip().endswith("?") or
        any(word in prompt_lower for word in ["consider", "notice", "allow", "invite", "what if"])
    ):
        issues.append("Prompt should be a question or gentle invitation")

    # Should not start with "I"
    if prompt.strip().startswith("I "):
        issues.append("Prompt should not start with 'I'")

    # Check for exclamation marks (against style guidelines)
    if "!" in prompt:
        issues.append("Prompt should not contain exclamation marks")

    if issues and len(issues) > len(result.issues):
        return ValidationResult(
            is_valid=len(issues) <= 2,  # Allow minor issues
            issues=issues,
            severity="warning" if len(issues) <= 2 else "error"
        )

    return result


def validate_contemplative_question(question: str) -> ValidationResult:
    """
    Validate a contemplative question.

    Args:
        question: The generated question

    Returns:
        ValidationResult
    """
    result = validate_response(question)
    if not result.is_valid:
        return result

    issues = list(result.issues)

    # Should end with question mark
    if not question.strip().endswith("?"):
        issues.append("Contemplative question should end with '?'")

    # Should not be yes/no question
    yes_no_starters = ["do you", "are you", "have you", "is there", "can you", "will you"]
    if any(question.lower().strip().startswith(s) for s in yes_no_starters):
        issues.append("Question should not be a yes/no question")

    # Check for exclamation marks
    if "!" in question:
        issues.append("Question should not contain exclamation marks")

    if issues and len(issues) > len(result.issues):
        return ValidationResult(
            is_valid=len(issues) <= 1,
            issues=issues,
            severity="warning" if len(issues) <= 1 else "error"
        )

    return result


def validate_meditation_guidance(guidance: dict) -> ValidationResult:
    """
    Validate meditation guidance content.

    Args:
        guidance: Dict with 'opening', 'settling', 'intervals', 'closing'

    Returns:
        ValidationResult
    """
    issues = []

    # Check all required sections exist and have content
    required_sections = ["opening", "settling", "closing"]
    for section in required_sections:
        content = guidance.get(section, "")
        if not content:
            issues.append(f"Missing meditation section: {section}")
            continue

        # Validate each section
        section_result = validate_response(content)
        if not section_result.is_valid:
            issues.extend([f"{section}: {i}" for i in section_result.issues])

    # Check intervals if present
    intervals = guidance.get("intervals", [])
    for i, interval in enumerate(intervals):
        if interval:
            interval_result = validate_response(interval)
            if not interval_result.is_valid:
                issues.extend([f"interval {i+1}: {issue}" for issue in interval_result.issues])

    # Check for exclamation marks anywhere
    all_text = " ".join([
        guidance.get("opening", ""),
        guidance.get("settling", ""),
        guidance.get("closing", ""),
        " ".join(guidance.get("intervals", []))
    ])
    if "!" in all_text:
        issues.append("Meditation guidance should not contain exclamation marks")

    return ValidationResult(
        is_valid=len(issues) == 0,
        issues=issues,
        severity="error" if issues else "none"
    )


def sanitize_response(response: str) -> str:
    """
    Attempt to sanitize a response by removing problematic content.

    This is a last resort - prefer rejection and fallback.

    Args:
        response: Raw AI response

    Returns:
        Sanitized response (may be empty if too problematic)
    """
    if not response:
        return ""

    # Remove exclamation marks
    sanitized = response.replace("!", ".")

    # Remove any medical/professional advice sentences
    advice_patterns = [
        r"(?:^|\. )(?:You should|You must|I recommend)[^.]*\.",
        r"(?:^|\. )(?:Seek|Consider seeking)[^.]*professional[^.]*\.",
    ]

    for pattern in advice_patterns:
        sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)

    # Clean up multiple periods/spaces
    sanitized = re.sub(r'\.+', '.', sanitized)
    sanitized = re.sub(r'\s+', ' ', sanitized)

    return sanitized.strip()


def is_appropriate_for_spiritual_context(text: str) -> bool:
    """
    Quick check if text is appropriate for spiritual/contemplative context.

    Args:
        text: Text to check

    Returns:
        True if appropriate, False otherwise
    """
    result = validate_response(text)
    return result.is_valid
