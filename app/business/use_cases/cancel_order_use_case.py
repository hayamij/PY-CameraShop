"""
Use Case: Cancel Order

Business Logic:
- Validates order exists and belongs to user
- Validates order status is PENDING (can only cancel pending orders)
- Cancels order and restores product stock
"""

from dataclasses import dataclass
from app.business.ports.order_repository import IOrderRepository
from app.business.ports.product_repository import IProductRepository
from app.domain.exceptions import ValidationException, OrderNotFoundException
from app.domain.enums import OrderStatus


@dataclass
class CancelOrderInputData:
    """Input data for canceling an order"""
    order_id: int
    user_id: int


@dataclass
class CancelOrderOutputData:
    """Output data after canceling an order"""
    success: bool
    order_id: int
    message: str


class CancelOrderUseCase:
    """Use case for canceling a pending order"""
    
    def __init__(
        self,
        order_repository: IOrderRepository,
        product_repository: IProductRepository
    ):
        """
        Initialize the use case.
        
        Args:
            order_repository: Repository for order operations
            product_repository: Repository for product stock restoration
        """
        self.order_repository = order_repository
        self.product_repository = product_repository
    
    def execute(self, input_data: CancelOrderInputData) -> CancelOrderOutputData:
        """
        Execute the cancel order use case.
        
        Args:
            input_data: Input data containing order ID and user ID
            
        Returns:
            CancelOrderOutputData with operation result
            
        Raises:
            ValidationException: If validation fails
            OrderNotFoundException: If order not found
        """
        # Validate input
        if input_data.order_id <= 0:
            raise ValidationException("Invalid order ID")
        
        if input_data.user_id <= 0:
            raise ValidationException("Invalid user ID")
        
        # Get order
        order = self.order_repository.find_by_id(input_data.order_id)
        if order is None:
            raise OrderNotFoundException(input_data.order_id)
        
        # Verify order belongs to user
        if order.customer_id != input_data.user_id:
            raise ValidationException("You don't have permission to cancel this order")
        
        # Verify order can be cancelled (only pending orders)
        if order.status != OrderStatus.PENDING:
            raise ValidationException(
                f"Cannot cancel order with status {order.status.value}. "
                "Only pending orders can be cancelled."
            )
        
        # Cancel order (domain method handles status transition)
        order.cancel()
        
        # Restore product stock for each item
        for order_item in order.items:
            product = self.product_repository.find_by_id(order_item.product_id)
            if product:
                product.increase_stock(order_item.quantity)
                self.product_repository.save(product)
        
        # Save cancelled order
        self.order_repository.save(order)
        
        return CancelOrderOutputData(
            success=True,
            order_id=order.id,
            message=f"Order #{order.id} has been cancelled successfully"
        )
