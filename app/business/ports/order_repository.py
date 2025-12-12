"""
Order Repository Interface (Port)
Business layer defines the contract - Infrastructure implements it
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime
from ...domain.entities import Order
from ...domain.enums import OrderStatus


class IOrderRepository(ABC):
    """Interface for Order repository operations"""
    
    @abstractmethod
    def save(self, order: Order) -> Order:
        """
        Save an order (create or update)
        
        Args:
            order: Order entity to save
            
        Returns:
            Saved order with ID assigned
        """
        pass
    
    @abstractmethod
    def find_by_id(self, order_id: int) -> Optional[Order]:
        """
        Find order by ID
        
        Args:
            order_id: Order ID
            
        Returns:
            Order entity or None if not found
        """
        pass
    
    @abstractmethod
    def find_by_customer_id(
        self,
        customer_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """
        Find orders by customer ID
        
        Args:
            customer_id: Customer ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of order entities
        """
        pass
    
    @abstractmethod
    def find_by_status(
        self,
        status: OrderStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """
        Find orders by status
        
        Args:
            status: Order status
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of order entities
        """
        pass
    
    @abstractmethod
    def find_by_user_and_status(
        self,
        customer_id: int,
        status: str
    ) -> List[Order]:
        """
        Find orders by customer and status
        
        Args:
            customer_id: Customer ID
            status: Order status string
            
        Returns:
            List of order entities matching criteria
        """
        pass
    
    @abstractmethod
    def find_all(self, skip: int = 0, limit: int = 100) -> List[Order]:
        """
        Find all orders with pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of order entities
        """
        pass
    
    @abstractmethod
    def find_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """
        Find orders within date range
        
        Args:
            start_date: Start date
            end_date: End date
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of order entities
        """
        pass
    
    @abstractmethod
    def delete(self, order_id: int) -> bool:
        """
        Delete order
        
        Args:
            order_id: Order ID
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def count(self) -> int:
        """
        Count total orders
        
        Returns:
            Total number of orders
        """
        pass
    
    @abstractmethod
    def count_by_status(self, status: OrderStatus) -> int:
        """
        Count orders by status
        
        Args:
            status: Order status
            
        Returns:
            Number of orders with status
        """
        pass
    
    @abstractmethod
    def count_by_customer(self, customer_id: int) -> int:
        """
        Count orders for customer
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Number of orders for customer
        """
        pass
    
    @abstractmethod
    def find_with_filters(
        self,
        filters: dict,
        page: int = 1,
        per_page: int = 20,
        sort_by: str = 'newest'
    ) -> tuple[List[Order], int]:
        """
        Find orders with advanced filters and pagination
        
        Args:
            filters: Dictionary of filters (status, customer_id, start_date, end_date, search_query)
            page: Page number (1-indexed)
            per_page: Number of records per page
            sort_by: Sort option ('newest', 'oldest', 'total_asc', 'total_desc')
            
        Returns:
            Tuple of (list of orders, total count)
        """
        pass
    
    @abstractmethod
    def get_order_statistics(self, filters: Optional[dict] = None) -> dict:
        """
        Get order statistics (for admin dashboard)
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            Dictionary with statistics:
            - total_revenue: Total revenue from orders
            - pending_count: Count of pending orders
            - processing_count: Count of processing orders
            - completed_count: Count of completed orders
            - cancelled_count: Count of cancelled orders
        """
        pass
