"""
Tests for PhoneNumber value object
"""
import pytest
from app.domain.value_objects.phone_number import PhoneNumber


class TestPhoneNumberCreation:
    """Test PhoneNumber value object creation"""
    
    def test_create_valid_phone_number(self):
        """Should create phone number with valid Vietnamese format"""
        phone = PhoneNumber("0123456789")
        
        assert phone.number == "0123456789"
    
    def test_create_phone_number_strips_whitespace(self):
        """Should strip whitespace"""
        phone = PhoneNumber("  0123456789  ")
        
        assert phone.number == "0123456789"
    
    def test_create_phone_number_various_valid_formats(self):
        """Should accept various valid Vietnamese phone numbers"""
        valid_numbers = [
            "0123456789",
            "0987654321",
            "0901234567",
            "0812345678"
        ]
        
        for number in valid_numbers:
            phone = PhoneNumber(number)
            assert phone.number == number
    
    def test_create_phone_number_invalid_empty(self):
        """Should raise error for empty phone number"""
        with pytest.raises(ValueError, match="Phone number cannot be empty"):
            PhoneNumber("")
    
    def test_create_phone_number_invalid_too_short(self):
        """Should raise error for phone number with less than 10 digits"""
        with pytest.raises(ValueError, match="Invalid Vietnamese phone number format"):
            PhoneNumber("012345678")  # 9 digits
    
    def test_create_phone_number_invalid_too_long(self):
        """Should raise error for phone number with more than 10 digits"""
        with pytest.raises(ValueError, match="Invalid Vietnamese phone number format"):
            PhoneNumber("01234567890")  # 11 digits
    
    def test_create_phone_number_invalid_not_starting_with_zero(self):
        """Should raise error for phone number not starting with 0"""
        with pytest.raises(ValueError, match="Invalid Vietnamese phone number format"):
            PhoneNumber("1234567890")
    
    def test_create_phone_number_invalid_contains_letters(self):
        """Should raise error for phone number with letters"""
        with pytest.raises(ValueError, match="Invalid Vietnamese phone number format"):
            PhoneNumber("012345678a")
    
    def test_create_phone_number_invalid_contains_special_chars(self):
        """Should raise error for phone number with special characters"""
        with pytest.raises(ValueError, match="Invalid Vietnamese phone number format"):
            PhoneNumber("0123-456-789")


class TestPhoneNumberProperties:
    """Test PhoneNumber value object properties"""
    
    def test_phone_number_formatted(self):
        """Should format phone number with dashes"""
        phone = PhoneNumber("0123456789")
        
        assert phone.formatted == "0123-456-789"
    
    def test_phone_number_formatted_various_numbers(self):
        """Should format various phone numbers correctly"""
        test_cases = [
            ("0123456789", "0123-456-789"),
            ("0987654321", "0987-654-321"),
            ("0901234567", "0901-234-567")
        ]
        
        for number, expected_format in test_cases:
            phone = PhoneNumber(number)
            assert phone.formatted == expected_format


class TestPhoneNumberEquality:
    """Test PhoneNumber equality comparison"""
    
    def test_phone_numbers_with_same_number_are_equal(self):
        """Should consider phone numbers with same number as equal"""
        phone1 = PhoneNumber("0123456789")
        phone2 = PhoneNumber("0123456789")
        
        assert phone1 == phone2
    
    def test_phone_numbers_with_different_number_are_not_equal(self):
        """Should consider phone numbers with different numbers as not equal"""
        phone1 = PhoneNumber("0123456789")
        phone2 = PhoneNumber("0987654321")
        
        assert phone1 != phone2
    
    def test_phone_number_not_equal_to_string(self):
        """Should not be equal to string"""
        phone = PhoneNumber("0123456789")
        
        assert phone != "0123456789"
    
    def test_phone_number_not_equal_to_non_phone_number(self):
        """Should not be equal to non-PhoneNumber object"""
        phone = PhoneNumber("0123456789")
        
        assert phone != 123456789


class TestPhoneNumberHash:
    """Test PhoneNumber hash functionality"""
    
    def test_phone_number_hashable(self):
        """Should be hashable for use in sets/dicts"""
        phone1 = PhoneNumber("0123456789")
        phone2 = PhoneNumber("0123456789")
        
        phone_set = {phone1, phone2}
        assert len(phone_set) == 1  # Same phone number, so only one in set
    
    def test_phone_numbers_different_hash(self):
        """Should have different hashes for different numbers"""
        phone1 = PhoneNumber("0123456789")
        phone2 = PhoneNumber("0987654321")
        
        phone_set = {phone1, phone2}
        assert len(phone_set) == 2  # Different numbers


class TestPhoneNumberRepresentation:
    """Test PhoneNumber string representation"""
    
    def test_phone_number_str_representation(self):
        """Should have readable string representation"""
        phone = PhoneNumber("0123456789")
        
        assert str(phone) == "0123-456-789"
    
    def test_phone_number_repr_representation(self):
        """Should have developer-friendly repr"""
        phone = PhoneNumber("0123456789")
        
        assert "0123456789" in repr(phone)


class TestPhoneNumberEdgeCases:
    """Test PhoneNumber edge cases"""
    
    def test_phone_number_all_zeros_after_first(self):
        """Should accept phone number with all zeros after first digit"""
        phone = PhoneNumber("0000000000")
        
        assert phone.number == "0000000000"
    
    def test_phone_number_all_nines(self):
        """Should accept phone number with all nines"""
        phone = PhoneNumber("0999999999")
        
        assert phone.number == "0999999999"
