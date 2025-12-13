"""Delete order use case"""
from dataclasses import dataclass
from app.business.ports.order_repository import IOrderRepository


@dataclass
class DeleteOrderInputData:
    """Input data for deleting an order"""
    order_id: int


@dataclass
class DeleteOrderOutputData:
    """Output data for deleting an order"""
    success: bool
    message: str


class DeleteOrderUseCase:
    """Use case for deleting an order (admin only)"""
    
    def __init__(self, order_repository: IOrderRepository):
        self.order_repository = order_repository
    
    def execute(self, input_data: DeleteOrderInputData) -> DeleteOrderOutputData:
        """Execute the delete order use case"""
        try:
            # Get the order first to verify it exists
            order = self.order_repository.find_by_id(input_data.order_id)
            
            if not order:
                return DeleteOrderOutputData(
                    success=False,
                    message=f"Order {input_data.order_id} not found"
                )
            
            # Delete the order
            self.order_repository.delete(input_data.order_id)
            
            return DeleteOrderOutputData(
                success=True,
                message=f"Order {input_data.order_id} deleted successfully"
            )
            
        except Exception as e:
            return DeleteOrderOutputData(
                success=False,
                message=f"Failed to delete order: {str(e)}"
            )
