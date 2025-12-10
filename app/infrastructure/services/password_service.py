"""
Password Hashing Service (Infrastructure Layer)

This service provides password hashing functionality using bcrypt.
It's placed in infrastructure layer because bcrypt is an external dependency.

Clean Architecture:
- Infrastructure layer (Layer 4)
- Used by Adapters layer for password operations
- NOT imported by Domain or Business layers
"""
import bcrypt


class PasswordHashingService:
    """
    Service for password hashing operations
    
    Uses bcrypt for secure password hashing with salts.
    This is infrastructure concern - never import in domain/business layers.
    """
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a plain text password using bcrypt
        
        Args:
            password: Plain text password to hash
        
        Returns:
            Hashed password as string (bcrypt hash decoded to UTF-8)
        
        Example:
            >>> password_hash = PasswordHashingService.hash_password("mypassword123")
            >>> # Returns: "$2b$12$..." (60 char bcrypt hash)
        """
        if not password:
            raise ValueError("Password cannot be empty")
        
        # Generate salt and hash password
        salt = bcrypt.gensalt()
        password_bytes = password.encode('utf-8')
        password_hash = bcrypt.hashpw(password_bytes, salt)
        
        # Return as string (decoded from bytes)
        return password_hash.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain text password against a hashed password
        
        Args:
            plain_password: Plain text password to verify
            hashed_password: Bcrypt hashed password to check against
        
        Returns:
            True if password matches, False otherwise
        
        Example:
            >>> is_valid = PasswordHashingService.verify_password("mypassword123", hash)
            >>> # Returns: True or False
        """
        if not plain_password or not hashed_password:
            return False
        
        try:
            password_bytes = plain_password.encode('utf-8')
            stored_hash_bytes = hashed_password.encode('utf-8')
            
            return bcrypt.checkpw(password_bytes, stored_hash_bytes)
        except Exception:
            return False
