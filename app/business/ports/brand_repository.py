"""
Brand Repository Interface (Port)
Business layer defines the contract - Infrastructure implements it
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from ...domain.entities import Brand


class IBrandRepository(ABC):
    """Interface for Brand repository operations"""
    
    @abstractmethod
    def save(self, brand: Brand) -> Brand:
        """
        Save a brand (create or update)
        
        Args:
            brand: Brand entity to save
            
        Returns:
            Saved brand with ID assigned
        """
        pass
    
    @abstractmethod
    def find_by_id(self, brand_id: int) -> Optional[Brand]:
        """
        Find brand by ID
        
        Args:
            brand_id: Brand ID
            
        Returns:
            Brand entity or None if not found
        """
        pass
    
    @abstractmethod
    def find_by_name(self, name: str) -> Optional[Brand]:
        """
        Find brand by name
        
        Args:
            name: Brand name
            
        Returns:
            Brand entity or None if not found
        """
        pass
    
    @abstractmethod
    def find_all(self, active_only: bool = True) -> List[Brand]:
        """
        Find all brands
        
        Args:
            active_only: If True, return only active brands
            
        Returns:
            List of brand entities
        """
        pass
    
    @abstractmethod
    def delete(self, brand_id: int) -> bool:
        """
        Delete brand
        
        Args:
            brand_id: Brand ID
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def exists_by_name(self, name: str) -> bool:
        """
        Check if brand name exists
        
        Args:
            name: Brand name
            
        Returns:
            True if exists, False otherwise
        """
        pass
    
    @abstractmethod
    def count(self, active_only: bool = True) -> int:
        """
        Count total brands
        
        Args:
            active_only: If True, count only active brands
            
        Returns:
            Total number of brands
        """
        pass
