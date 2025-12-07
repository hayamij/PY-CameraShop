"""
Cart Repository Interface (Port)
Business layer defines the contract - Infrastructure implements it
"""
from abc import ABC, abstractmethod
from typing import Optional
from ...domain.entities import Cart


class ICartRepository(ABC):
    """Interface for Cart repository operations"""
    
    @abstractmethod
    def save(self, cart: Cart) -> Cart:
        """
        Save a cart (create or update)
        
        Args:
            cart: Cart entity to save
            
        Returns:
            Saved cart with ID assigned
        """
        pass
    
    @abstractmethod
    def find_by_id(self, cart_id: int) -> Optional[Cart]:
        """
        Find cart by ID
        
        Args:
            cart_id: Cart ID
            
        Returns:
            Cart entity or None if not found
        """
        pass
    
    @abstractmethod
    def find_by_customer_id(self, customer_id: int) -> Optional[Cart]:
        """
        Find cart by customer ID
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Cart entity or None if not found
        """
        pass
    
    @abstractmethod
    def delete(self, cart_id: int) -> bool:
        """
        Delete cart
        
        Args:
            cart_id: Cart ID
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def clear_cart(self, customer_id: int) -> bool:
        """
        Clear all items from customer's cart
        
        Args:
            customer_id: Customer ID
            
        Returns:
            True if cleared, False if cart not found
        """
        pass
