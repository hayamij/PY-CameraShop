"""Remove Cart Item Use Case - Remove item from cart"""
from dataclasses import dataclass
from app.business.ports.cart_repository import ICartRepository
from app.domain.exceptions import (
    CartItemNotFoundException,
    ValidationException
)


@dataclass
class RemoveCartItemInputData:
    """Input data for removing cart item"""
    user_id: int
    cart_item_id: int


@dataclass
class RemoveCartItemOutputData:
    """Output data for removing cart item"""
    success: bool
    message: str = ""
    error_message: str = ""


class RemoveCartItemUseCase:
    """Use case for removing an item from the shopping cart"""

    def __init__(self, cart_repository: ICartRepository):
        self.cart_repository = cart_repository

    def execute(self, input_data: RemoveCartItemInputData) -> RemoveCartItemOutputData:
        """
        Execute the remove cart item use case
        
        Business Rules:
        - User must be authenticated
        - Cart item must exist and belong to user
        """
        try:
            # Validate input
            self._validate_input(input_data)
            
            # Find cart item
            cart_item = self.cart_repository.find_cart_item_by_id(input_data.cart_item_id)
            if not cart_item:
                raise CartItemNotFoundException(
                    f"Cart item with ID {input_data.cart_item_id} not found"
                )
            
            # Verify cart belongs to user
            cart = self.cart_repository.find_by_user_id(input_data.user_id)
            if not cart or cart.cart_id != cart_item.cart_id:
                raise ValidationException("This cart item does not belong to you")
            
            # Remove item
            self.cart_repository.remove_cart_item(input_data.cart_item_id)
            
            return RemoveCartItemOutputData(
                success=True,
                message="Item removed from cart successfully"
            )
            
        except (CartItemNotFoundException, ValidationException) as e:
            return RemoveCartItemOutputData(
                success=False,
                error_message=str(e)
            )
        except Exception as e:
            return RemoveCartItemOutputData(
                success=False,
                error_message=f"An error occurred while removing cart item: {str(e)}"
            )

    def _validate_input(self, input_data: RemoveCartItemInputData) -> None:
        """Validate input data"""
        if input_data.user_id <= 0:
            raise ValidationException("Invalid user ID")
        
        if input_data.cart_item_id <= 0:
            raise ValidationException("Invalid cart item ID")
