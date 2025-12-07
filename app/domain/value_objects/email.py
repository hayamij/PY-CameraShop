"""
Email Value Object - Immutable representation of email addresses
"""
import re


class Email:
    """Immutable email value object with validation"""
    
    # Simple regex pattern for email validation
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    def __init__(self, address: str):
        """
        Initialize Email value object
        
        Args:
            address: Email address string
            
        Raises:
            ValueError: If email format is invalid
        """
        if not address:
            raise ValueError("Email address cannot be empty")
        
        address = address.strip().lower()
        
        if not self.EMAIL_PATTERN.match(address):
            raise ValueError(f"Invalid email format: {address}")
        
        self._address = address
    
    @property
    def address(self) -> str:
        """Get the email address"""
        return self._address
    
    @property
    def domain(self) -> str:
        """Get the domain part of email"""
        return self._address.split('@')[1]
    
    @property
    def local_part(self) -> str:
        """Get the local part of email (before @)"""
        return self._address.split('@')[0]
    
    def __eq__(self, other) -> bool:
        """Check equality"""
        if not isinstance(other, Email):
            return False
        return self._address == other._address
    
    def __hash__(self) -> int:
        """Hash for use in sets and dicts"""
        return hash(self._address)
    
    def __str__(self) -> str:
        """String representation"""
        return self._address
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"Email('{self._address}')"
