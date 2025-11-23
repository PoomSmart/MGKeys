import pytest
from obfuscate import calculate_obfuscated_key, md5_string_for_obfuscated_key


class TestCalculateObfuscatedKey:
    """Test the calculate_obfuscated_key function."""
    
    def test_known_key_boot_nonce(self):
        """Test with a known key 'boot-nonce'."""
        result = calculate_obfuscated_key("boot-nonce")
        assert result == "/2V8H9h/+z0UxNUr9aRLeQ"
    
    def test_known_key_chip_id(self):
        """Test with a known key 'chip-id'."""
        result = calculate_obfuscated_key("/l0Kz2akvSvEHTNmZeY0nQ")
        # This will fail, but let's test the function works
        # The input should be the deobfuscated key
        result = calculate_obfuscated_key("chip-id")
        assert result == "/l0Kz2akvSvEHTNmZeY0nQ"
    
    def test_known_key_device_class(self):
        """Test with a known key 'DeviceClass'."""
        result = calculate_obfuscated_key("DeviceClass")
        assert result == "+3Uf0Pm5F8Xy7Onyvko0vA"
    
    def test_empty_string(self):
        """Test with empty string."""
        result = calculate_obfuscated_key("")
        assert isinstance(result, str)
        assert len(result) == 22
    
    def test_special_characters(self):
        """Test with special characters."""
        result = calculate_obfuscated_key("test-key-123")
        assert isinstance(result, str)
        assert len(result) == 22
    
    def test_escaped_quotes(self):
        """Test with escaped quotes."""
        # The function should handle escaped quotes
        result1 = calculate_obfuscated_key('test\\"key')
        result2 = calculate_obfuscated_key('test"key')
        assert result1 == result2
        assert len(result1) == 22
    
    def test_output_format(self):
        """Test that output is base64-like and 22 characters."""
        result = calculate_obfuscated_key("SomeTestKey")
        assert isinstance(result, str)
        assert len(result) == 22
        # Check it's base64-like (alphanumeric + / +)
        assert all(c.isalnum() or c in ['+', '/'] for c in result)


class TestMd5StringForObfuscatedKey:
    """Test the md5_string_for_obfuscated_key function."""
    
    def test_valid_key(self):
        """Test with a valid obfuscated key."""
        result = md5_string_for_obfuscated_key("/2V8H9h/+z0UxNUr9aRLeQ")
        assert result is not None
        assert isinstance(result, str)
        assert len(result) == 32  # MD5 hash is 32 hex characters
        assert all(c in '0123456789abcdef' for c in result)
    
    def test_another_valid_key(self):
        """Test with another valid key."""
        result = md5_string_for_obfuscated_key("+3Uf0Pm5F8Xy7Onyvko0vA")
        assert result is not None
        assert len(result) == 32
    
    def test_empty_string(self):
        """Test with empty string."""
        result = md5_string_for_obfuscated_key("")
        assert result is None
    
    def test_invalid_base64(self):
        """Test with invalid base64."""
        result = md5_string_for_obfuscated_key("not-valid-base64!!!")
        assert result is None
    
    def test_wrong_length_after_decode(self):
        """Test with key that decodes to wrong length."""
        # A valid base64 string that doesn't decode to 16 bytes
        result = md5_string_for_obfuscated_key("AAAA")
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
