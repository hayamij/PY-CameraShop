"""
Tests for Email value object
"""
import pytest
from app.domain.value_objects.email import Email


class TestEmailCreation:
    """Test Email value object creation"""
    
    def test_create_valid_email(self):
        """Should create email with valid address"""
        email = Email("user@example.com")
        
        assert email.address == "user@example.com"
    
    def test_create_email_converts_to_lowercase(self):
        """Should convert email to lowercase"""
        email = Email("User@Example.COM")
        
        assert email.address == "user@example.com"
    
    def test_create_email_strips_whitespace(self):
        """Should strip whitespace"""
        email = Email("  user@example.com  ")
        
        assert email.address == "user@example.com"
    
    def test_create_email_with_plus_sign(self):
        """Should accept email with plus sign"""
        email = Email("user+tag@example.com")
        
        assert email.address == "user+tag@example.com"
    
    def test_create_email_with_dots(self):
        """Should accept email with dots in local part"""
        email = Email("first.last@example.com")
        
        assert email.address == "first.last@example.com"
    
    def test_create_email_with_subdomain(self):
        """Should accept email with subdomain"""
        email = Email("user@mail.example.com")
        
        assert email.address == "user@mail.example.com"
    
    def test_create_email_invalid_empty(self):
        """Should raise error for empty email"""
        with pytest.raises(ValueError, match="Email address cannot be empty"):
            Email("")
    
    def test_create_email_invalid_no_at_sign(self):
        """Should raise error for email without @ sign"""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("userexample.com")
    
    def test_create_email_invalid_no_domain(self):
        """Should raise error for email without domain"""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("user@")
    
    def test_create_email_invalid_no_local_part(self):
        """Should raise error for email without local part"""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("@example.com")
    
    def test_create_email_invalid_no_tld(self):
        """Should raise error for email without TLD"""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("user@example")
    
    def test_create_email_invalid_multiple_at_signs(self):
        """Should raise error for email with multiple @ signs"""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("user@@example.com")


class TestEmailProperties:
    """Test Email value object properties"""
    
    def test_email_domain_property(self):
        """Should extract domain from email"""
        email = Email("user@example.com")
        
        assert email.domain == "example.com"
    
    def test_email_domain_with_subdomain(self):
        """Should extract full domain including subdomain"""
        email = Email("user@mail.example.com")
        
        assert email.domain == "mail.example.com"
    
    def test_email_local_part_property(self):
        """Should extract local part from email"""
        email = Email("user@example.com")
        
        assert email.local_part == "user"
    
    def test_email_local_part_with_plus(self):
        """Should extract local part with plus sign"""
        email = Email("user+tag@example.com")
        
        assert email.local_part == "user+tag"


class TestEmailEquality:
    """Test Email equality comparison"""
    
    def test_emails_with_same_address_are_equal(self):
        """Should consider emails with same address as equal"""
        email1 = Email("user@example.com")
        email2 = Email("user@example.com")
        
        assert email1 == email2
    
    def test_emails_case_insensitive_equality(self):
        """Should be case-insensitive when comparing"""
        email1 = Email("User@Example.COM")
        email2 = Email("user@example.com")
        
        assert email1 == email2
    
    def test_emails_with_different_address_are_not_equal(self):
        """Should consider emails with different addresses as not equal"""
        email1 = Email("user1@example.com")
        email2 = Email("user2@example.com")
        
        assert email1 != email2
    
    def test_email_not_equal_to_string(self):
        """Should not be equal to string"""
        email = Email("user@example.com")
        
        assert email != "user@example.com"


class TestEmailHash:
    """Test Email hash functionality"""
    
    def test_email_hashable(self):
        """Should be hashable for use in sets/dicts"""
        email1 = Email("user@example.com")
        email2 = Email("user@example.com")
        
        email_set = {email1, email2}
        assert len(email_set) == 1  # Same email, so only one in set


class TestEmailRepresentation:
    """Test Email string representation"""
    
    def test_email_str_representation(self):
        """Should have readable string representation"""
        email = Email("user@example.com")
        
        assert str(email) == "user@example.com"
    
    def test_email_repr_representation(self):
        """Should have developer-friendly repr"""
        email = Email("user@example.com")
        
        assert "user@example.com" in repr(email)
