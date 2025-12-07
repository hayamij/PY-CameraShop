"""
PhoneNumber Value Object - Immutable representation of phone numbers
"""
import re


class PhoneNumber:
    """Immutable phone number value object with Vietnamese format validation"""
    
    # Vietnamese phone number pattern (10 digits starting with 0)
    PHONE_PATTERN = re.compile(r'^0\d{9}$')
    
    def __init__(self, number: str):
        """
        Initialize PhoneNumber value object
        
        Args:
            number: Phone number string
            
        Raises:
            ValueError: If phone number format is invalid
        """
        if not number:
            raise ValueError("Phone number cannot be empty")
        
        # Strip whitespace but validate contains only digits
        stripped = number.strip()
        
        # Check if contains only digits
        if not stripped.isdigit():
            raise ValueError(f"Invalid Vietnamese phone number format: {number}. Expected format: 0xxxxxxxxx (10 digits)")
        
        if not self.PHONE_PATTERN.match(stripped):
            raise ValueError(f"Invalid Vietnamese phone number format: {number}. Expected format: 0xxxxxxxxx (10 digits)")
        
        self._number = stripped
    
    @property
    def number(self) -> str:
        """Get the phone number"""
        return self._number
    
    @property
    def formatted(self) -> str:
        """Get formatted phone number (0xxx-xxx-xxx)"""
        return f"{self._number[:4]}-{self._number[4:7]}-{self._number[7:]}"
    
    def __eq__(self, other) -> bool:
        """Check equality"""
        if not isinstance(other, PhoneNumber):
            return False
        return self._number == other._number
    
    def __hash__(self) -> int:
        """Hash for use in sets and dicts"""
        return hash(self._number)
    
    def __str__(self) -> str:
        """String representation"""
        return self.formatted
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"PhoneNumber('{self._number}')"
