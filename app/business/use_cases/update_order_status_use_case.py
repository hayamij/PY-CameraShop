"""
Update Order Status Use Case - Admin updates order workflow status
Clean Architecture - Business Layer
"""
from typing import Optional
from app.business.ports.order_repository import IOrderRepository
from app.domain.entities.order import OrderStatus
from app.domain.exceptions import (
    OrderNotFoundException,
    InvalidOrderStatusTransitionException,
    ValidationException
)


class UpdateOrderStatusInputData:
    """Input data for updating order status"""
    
    def __init__(self, order_id: int, new_status: str, admin_notes: Optional[str] = None):
        self.order_id = order_id
        self.new_status = new_status
        self.admin_notes = admin_notes


class UpdateOrderStatusOutputData:
    """Output data for order status update"""
    
    def __init__(
        self,
        success: bool,
        order_id: Optional[int] = None,
        old_status: Optional[str] = None,
        new_status: Optional[str] = None,
        message: Optional[str] = None
    ):
        self.success = success
        self.order_id = order_id
        self.old_status = old_status
        self.new_status = new_status
        self.message = message


class UpdateOrderStatusUseCase:
    """
    Use case for updating order status (Admin only)
    Implements business rules for valid status transitions
    """
    
    # Valid status transitions (aligned with OrderStatus enum)
    VALID_TRANSITIONS = {
        OrderStatus.PENDING: [OrderStatus.SHIPPING, OrderStatus.CANCELLED],
        OrderStatus.SHIPPING: [OrderStatus.COMPLETED],
        OrderStatus.COMPLETED: [],  # Final state
        OrderStatus.CANCELLED: []   # Final state
    }
    
    def __init__(self, order_repository: IOrderRepository):
        self.order_repository = order_repository
    
    def execute(self, input_data: UpdateOrderStatusInputData) -> UpdateOrderStatusOutputData:
        """
        Execute the update order status use case
        
        Args:
            input_data: UpdateOrderStatusInputData with order_id and new_status
            
        Returns:
            UpdateOrderStatusOutputData with update result
        """
        try:
            # Validate input
            self._validate_input(input_data)
            
            # Get order
            order = self.order_repository.find_by_id(input_data.order_id)
            if not order:
                raise OrderNotFoundException(input_data.order_id)
            
            # Parse new status
            try:
                new_status = OrderStatus(input_data.new_status.upper())
            except ValueError:
                valid_statuses = [status.value for status in OrderStatus]
                raise ValidationException(
                    f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                )
            
            # Check if transition is valid
            old_status = order.status
            if not self._is_valid_transition(old_status, new_status):
                raise InvalidOrderStatusTransitionException(
                    old_status.value,
                    new_status.value,
                    self._get_allowed_transitions(old_status)
                )
            
            # Update order status
            order.update_status(new_status)
            
            # Save order
            self.order_repository.save(order)
            
            return UpdateOrderStatusOutputData(
                success=True,
                order_id=order.order_id,
                old_status=old_status.value,
                new_status=new_status.value,
                message=f"Order status updated from {old_status.value} to {new_status.value}"
            )
            
        except (OrderNotFoundException, InvalidOrderStatusTransitionException, ValidationException) as e:
            return UpdateOrderStatusOutputData(
                success=False,
                order_id=input_data.order_id,
                message=str(e)
            )
        except Exception as e:
            return UpdateOrderStatusOutputData(
                success=False,
                order_id=input_data.order_id,
                message=f"Error updating order status: {str(e)}"
            )
    
    def _validate_input(self, input_data: UpdateOrderStatusInputData):
        """Validate input data"""
        if input_data.order_id <= 0:
            raise ValidationException("Invalid order ID")
        
        if not input_data.new_status:
            raise ValidationException("New status is required")
    
    def _is_valid_transition(self, current_status: OrderStatus, new_status: OrderStatus) -> bool:
        """Check if status transition is valid"""
        allowed_transitions = self.VALID_TRANSITIONS.get(current_status, [])
        return new_status in allowed_transitions
    
    def _get_allowed_transitions(self, current_status: OrderStatus) -> list:
        """Get list of allowed status transitions"""
        allowed = self.VALID_TRANSITIONS.get(current_status, [])
        return [status.value for status in allowed]
