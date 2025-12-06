import pytest
from unittest.mock import patch
from guess_keys import generate_guesses


class TestGenerateGuesses:
    """Test the generate_guesses function."""

    def test_basic_camelcase_hint(self):
        """Test with a basic CamelCase hint."""
        guesses = generate_guesses("TestKey", None)
        assert "TestKey" in guesses
        assert "testKey" in guesses  # lowercase first letter
        assert "DeviceTestKey" in guesses
        assert "DeviceSupportsTestKey" in guesses
        assert "SupportsTestKey" in guesses

    def test_hint_already_has_device_prefix(self):
        """Test when hint already has 'Device' prefix."""
        guesses = generate_guesses("DeviceSupportsXYZ", None)
        assert "DeviceSupportsXYZ" in guesses
        assert "deviceSupportsXYZ" in guesses
        # Should not add Device prefix again

    def test_hint_already_has_supports(self):
        """Test when hint already contains 'Supports'."""
        guesses = generate_guesses("SupportsFeature", None)
        assert "SupportsFeature" in guesses
        assert "supportsFeature" in guesses

    def test_with_start_char_filter(self):
        """Test filtering by start character."""
        guesses = generate_guesses("TestKey", "D")
        # Should only include guesses starting with 'D'
        assert all(g.startswith("D") for g in guesses if g)
        assert "DeviceTestKey" in guesses
        assert "DeviceSupportsTestKey" in guesses

    def test_start_char_with_common_prefixes(self):
        """Test that common prefixes are tried when start_char is provided."""
        guesses = generate_guesses("Feature", "H")
        assert any(g.startswith("H") for g in guesses)
        # Should try "Has" prefix
        assert "HasFeature" in guesses

    def test_start_char_filters_out_non_matching(self):
        """Test that start_char filters out non-matching guesses."""
        guesses = generate_guesses("Something", "X")
        # Original guesses won't start with X, so should try prefixes
        # But none of the common prefixes start with X
        # So this might be empty or have constructed candidates
        assert all(g.startswith("X") or g == "Something" for g in guesses)

    def test_lowercase_hint(self):
        """Test with lowercase hint."""
        guesses = generate_guesses("lowercase", None)
        assert "lowercase" in guesses

    def test_empty_hint(self):
        """Test with empty hint (edge case)."""
        # This might cause issues, but function should handle it
        guesses = generate_guesses("", None)
        assert "" in guesses

    def test_hint_with_hyphens(self):
        """Test with kebab-case hint."""
        guesses = generate_guesses("test-key", None)
        assert "test-key" in guesses

    def test_common_prefix_device(self):
        """Test that Device prefix is added."""
        guesses = generate_guesses("ColorPolicy", "D")
        assert "DeviceColorPolicy" in guesses

    def test_common_prefix_supports(self):
        """Test that Supports prefix is added."""
        guesses = generate_guesses("Feature", "S")
        assert "SupportsFeature" in guesses

    def test_common_prefix_is(self):
        """Test that Is prefix is added."""
        guesses = generate_guesses("Virtual", "I")
        assert "IsVirtual" in guesses

    def test_common_prefix_allow(self):
        """Test that Allow prefix is added."""
        guesses = generate_guesses("YouTube", "A")
        assert "AllowYouTube" in guesses


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
