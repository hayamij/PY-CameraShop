"""
Category Repository Interface (Port)
Business layer defines the contract - Infrastructure implements it
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from ...domain.entities import Category


class ICategoryRepository(ABC):
    """Interface for Category repository operations"""
    
    @abstractmethod
    def save(self, category: Category) -> Category:
        """
        Save a category (create or update)
        
        Args:
            category: Category entity to save
            
        Returns:
            Saved category with ID assigned
        """
        pass
    
    @abstractmethod
    def find_by_id(self, category_id: int) -> Optional[Category]:
        """
        Find category by ID
        
        Args:
            category_id: Category ID
            
        Returns:
            Category entity or None if not found
        """
        pass
    
    @abstractmethod
    def find_by_name(self, name: str) -> Optional[Category]:
        """
        Find category by name
        
        Args:
            name: Category name
            
        Returns:
            Category entity or None if not found
        """
        pass
    
    @abstractmethod
    def find_all(self, active_only: bool = True) -> List[Category]:
        """
        Find all categories
        
        Args:
            active_only: If True, return only active categories
            
        Returns:
            List of category entities
        """
        pass
    
    @abstractmethod
    def delete(self, category_id: int) -> bool:
        """
        Delete category
        
        Args:
            category_id: Category ID
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def exists_by_name(self, name: str) -> bool:
        """
        Check if category name exists
        
        Args:
            name: Category name
            
        Returns:
            True if exists, False otherwise
        """
        pass
    
    @abstractmethod
    def count(self, active_only: bool = True) -> int:
        """
        Count total categories
        
        Args:
            active_only: If True, count only active categories
            
        Returns:
            Total number of categories
        """
        pass
