"""
Use Case: Get My Orders

Business Logic:
- Retrieves all orders for a specific user
- Supports filtering by order status
- Returns orders sorted by creation date (newest first)
"""

from dataclasses import dataclass
from typing import List, Optional
from app.business.ports.order_repository import IOrderRepository
from app.domain.exceptions import ValidationException


@dataclass
class GetMyOrdersInputData:
    """Input data for getting user orders"""
    user_id: int
    status_filter: Optional[str] = None


@dataclass
class MyOrderItemData:
    """Order item data for output"""
    order_id: int
    total_amount: float
    status: str
    payment_method: str
    shipping_address: str
    phone_number: str
    notes: str
    created_at: str
    item_count: int


@dataclass
class GetMyOrdersOutputData:
    """Output data containing user orders"""
    success: bool
    orders: List[MyOrderItemData]
    total_orders: int
    message: str


class GetMyOrdersUseCase:
    """Use case for retrieving user's orders"""
    
    def __init__(self, order_repository: IOrderRepository):
        """
        Initialize the use case.
        
        Args:
            order_repository: Repository for order queries
        """
        self.order_repository = order_repository
    
    def execute(self, input_data: GetMyOrdersInputData) -> GetMyOrdersOutputData:
        """
        Execute the get my orders use case.
        
        Args:
            input_data: Input data containing user ID and optional filters
            
        Returns:
            GetMyOrdersOutputData with user's orders
            
        Raises:
            ValidationException: If validation fails
        """
        # Validate input
        if input_data.user_id <= 0:
            raise ValidationException("Invalid user ID")
        
        # Get orders
        if input_data.status_filter:
            orders = self.order_repository.find_by_user_and_status(
                input_data.user_id,
                input_data.status_filter
            )
        else:
            orders = self.order_repository.find_by_customer_id(input_data.user_id)
        
        # Convert to output data
        order_items = []
        for order in orders:
            order_items.append(MyOrderItemData(
                order_id=order.id,
                total_amount=order.total_amount.amount,
                status=order.status.value,
                payment_method=order.payment_method.value,
                shipping_address=order.shipping_address,
                phone_number=order.phone_number,
                notes=order.notes,
                created_at=order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                item_count=len(order.items)
            ))
        
        return GetMyOrdersOutputData(
            success=True,
            orders=order_items,
            total_orders=len(order_items),
            message=f"Retrieved {len(order_items)} order(s)"
        )
