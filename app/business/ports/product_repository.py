"""
Product Repository Interface (Port)
Business layer defines the contract - Infrastructure implements it
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from ...domain.entities import Product


class IProductRepository(ABC):
    """Interface for Product repository operations"""
    
    @abstractmethod
    def save(self, product: Product) -> Product:
        """
        Save a product (create or update)
        
        Args:
            product: Product entity to save
            
        Returns:
            Saved product with ID assigned
        """
        pass
    
    @abstractmethod
    def find_by_id(self, product_id: int) -> Optional[Product]:
        """
        Find product by ID
        
        Args:
            product_id: Product ID
            
        Returns:
            Product entity or None if not found
        """
        pass
    
    @abstractmethod
    def find_all(
        self,
        skip: int = 0,
        limit: int = 100,
        visible_only: bool = True
    ) -> List[Product]:
        """
        Find all products with pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            visible_only: If True, return only visible products
            
        Returns:
            List of product entities
        """
        pass
    
    @abstractmethod
    def find_by_category(
        self,
        category_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """
        Find products by category
        
        Args:
            category_id: Category ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of product entities
        """
        pass
    
    @abstractmethod
    def find_by_brand(
        self,
        brand_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """
        Find products by brand
        
        Args:
            brand_id: Brand ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of product entities
        """
        pass
    
    @abstractmethod
    def search_by_name(self, query: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Search products by name
        
        Args:
            query: Search query
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of product entities matching query
        """
        pass
    
    @abstractmethod
    def find_by_ids(self, product_ids: List[int]) -> List[Product]:
        """
        Find multiple products by IDs
        
        Args:
            product_ids: List of product IDs
            
        Returns:
            List of product entities
        """
        pass
    
    @abstractmethod
    def delete(self, product_id: int) -> bool:
        """
        Delete product
        
        Args:
            product_id: Product ID
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def count(self, visible_only: bool = True) -> int:
        """
        Count total products
        
        Args:
            visible_only: If True, count only visible products
            
        Returns:
            Total number of products
        """
        pass
    
    @abstractmethod
    def count_by_category(self, category_id: int) -> int:
        """
        Count products in category
        
        Args:
            category_id: Category ID
            
        Returns:
            Number of products in category
        """
        pass
    
    @abstractmethod
    def count_by_brand(self, brand_id: int) -> int:
        """
        Count products by brand
        
        Args:
            brand_id: Brand ID
            
        Returns:
            Number of products by brand
        """
        pass
