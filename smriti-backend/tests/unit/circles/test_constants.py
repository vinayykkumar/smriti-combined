"""
Unit tests for Circle constants and utility functions.
"""
import pytest
import re

from app.circles.constants import (
    COLLECTION_NAME,
    MAX_MEMBERS_PER_CIRCLE,
    MAX_CIRCLES_PER_USER,
    INVITE_CODE_LENGTH,
    INVITE_CODE_ALPHABET,
    CIRCLE_COLORS,
    generate_invite_code,
    get_random_color,
    is_valid_color,
)


class TestConstants:
    """Tests for circle constants."""

    def test_collection_name(self):
        """Test that collection name is set."""
        assert COLLECTION_NAME == "circles"

    def test_max_members_per_circle(self):
        """Test max members limit."""
        assert MAX_MEMBERS_PER_CIRCLE == 5

    def test_max_circles_per_user(self):
        """Test max circles per user limit."""
        assert MAX_CIRCLES_PER_USER == 20

    def test_invite_code_length(self):
        """Test invite code length."""
        assert INVITE_CODE_LENGTH == 8

    def test_invite_code_alphabet_no_confusing_chars(self):
        """Test that confusing characters are excluded from alphabet."""
        # These should NOT be in the alphabet: 0, O, 1, I, L
        confusing_chars = ['0', 'O', '1', 'I', 'L']
        for char in confusing_chars:
            assert char not in INVITE_CODE_ALPHABET, f"Confusing char '{char}' should not be in alphabet"

    def test_circle_colors_are_valid_hex(self):
        """Test that all colors are valid hex codes."""
        hex_pattern = re.compile(r'^#[0-9A-Fa-f]{6}$')
        for color in CIRCLE_COLORS:
            assert hex_pattern.match(color), f"Invalid hex color: {color}"


class TestGenerateInviteCode:
    """Tests for generate_invite_code function."""

    def test_invite_code_length(self):
        """Test that generated code has correct length."""
        code = generate_invite_code()
        assert len(code) == INVITE_CODE_LENGTH

    def test_invite_code_characters(self):
        """Test that code only contains allowed characters."""
        code = generate_invite_code()
        for char in code:
            assert char in INVITE_CODE_ALPHABET, f"Invalid char '{char}' in invite code"

    def test_invite_code_uniqueness(self):
        """Test that multiple generated codes are likely unique."""
        codes = [generate_invite_code() for _ in range(100)]
        # All 100 should be unique (collision probability is astronomically low)
        assert len(set(codes)) == 100, "Generated codes should be unique"

    def test_invite_code_is_uppercase(self):
        """Test that generated code is uppercase."""
        code = generate_invite_code()
        assert code == code.upper()


class TestGetRandomColor:
    """Tests for get_random_color function."""

    def test_returns_valid_color(self):
        """Test that returned color is from the palette."""
        color = get_random_color()
        assert color in CIRCLE_COLORS

    def test_returns_hex_format(self):
        """Test that color is in hex format."""
        color = get_random_color()
        assert color.startswith('#')
        assert len(color) == 7

    def test_randomness(self):
        """Test that multiple calls return varied colors."""
        colors = [get_random_color() for _ in range(50)]
        # Should have some variety (not all the same)
        unique_colors = set(colors)
        assert len(unique_colors) > 1, "Random colors should vary"


class TestIsValidColor:
    """Tests for is_valid_color function."""

    def test_valid_color_from_palette(self):
        """Test that palette colors are valid."""
        for color in CIRCLE_COLORS:
            assert is_valid_color(color) is True

    def test_valid_color_lowercase(self):
        """Test that lowercase version is also valid."""
        color = CIRCLE_COLORS[0].lower()
        assert is_valid_color(color) is True

    def test_invalid_color(self):
        """Test that non-palette colors are invalid."""
        assert is_valid_color("#FFFFFF") is False
        assert is_valid_color("#000000") is False
        assert is_valid_color("#123456") is False

    def test_none_color(self):
        """Test that None is invalid."""
        assert is_valid_color(None) is False

    def test_empty_color(self):
        """Test that empty string is invalid."""
        assert is_valid_color("") is False
