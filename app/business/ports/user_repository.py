"""
User Repository Interface (Port)
Business layer defines the contract - Infrastructure implements it
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from ...domain.entities import User
from ...domain.value_objects import Email


class IUserRepository(ABC):
    """Interface for User repository operations"""
    
    @abstractmethod
    def save(self, user: User) -> User:
        """
        Save a user (create or update)
        
        Args:
            user: User entity to save
            
        Returns:
            Saved user with ID assigned
            
        Raises:
            UserAlreadyExistsException: If username or email already exists
        """
        pass
    
    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        """
        Find user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User entity or None if not found
        """
        pass
    
    @abstractmethod
    def find_by_username(self, username: str) -> Optional[User]:
        """
        Find user by username
        
        Args:
            username: Username
            
        Returns:
            User entity or None if not found
        """
        pass
    
    @abstractmethod
    def find_by_email(self, email: Email) -> Optional[User]:
        """
        Find user by email
        
        Args:
            email: Email value object
            
        Returns:
            User entity or None if not found
        """
        pass
    
    @abstractmethod
    def find_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Find all users with pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of user entities
        """
        pass
    
    @abstractmethod
    def find_by_role(self, role: str, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Find users by role
        
        Args:
            role: User role
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of user entities
        """
        pass
    
    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """
        Delete user
        
        Args:
            user_id: User ID
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def exists_by_username(self, username: str) -> bool:
        """
        Check if username exists
        
        Args:
            username: Username
            
        Returns:
            True if exists, False otherwise
        """
        pass
    
    @abstractmethod
    def exists_by_email(self, email: Email) -> bool:
        """
        Check if email exists
        
        Args:
            email: Email value object
            
        Returns:
            True if exists, False otherwise
        """
        pass
    
    @abstractmethod
    def count(self) -> int:
        """
        Count total users
        
        Returns:
            Total number of users
        """
        pass
