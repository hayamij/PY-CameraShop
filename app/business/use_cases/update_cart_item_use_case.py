"""Update Cart Item Use Case - Update quantity of cart item"""
from dataclasses import dataclass
from typing import Optional
from app.business.ports.cart_repository import ICartRepository
from app.business.ports.product_repository import IProductRepository
from app.domain.exceptions import (
    CartItemNotFoundException,
    InsufficientStockException,
    ValidationException
)


@dataclass
class UpdateCartItemInputData:
    """Input data for updating cart item"""
    user_id: int
    cart_item_id: int
    new_quantity: int


@dataclass
class UpdateCartItemOutputData:
    """Output data for updating cart item"""
    success: bool
    cart_item_id: Optional[int] = None
    new_quantity: int = 0
    message: str = ""
    error_message: str = ""


class UpdateCartItemUseCase:
    """Use case for updating cart item quantity"""

    def __init__(
        self,
        cart_repository: ICartRepository,
        product_repository: IProductRepository
    ):
        self.cart_repository = cart_repository
        self.product_repository = product_repository

    def execute(self, input_data: UpdateCartItemInputData) -> UpdateCartItemOutputData:
        """
        Execute the update cart item use case
        
        Business Rules:
        - User must be authenticated
        - Cart item must exist and belong to user
        - New quantity must be positive
        - Cannot exceed available stock
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
            
            # Get product to check stock
            product = self.product_repository.find_by_id(cart_item.product_id)
            if not product:
                raise ValidationException("Product no longer available")
            
            # Check stock availability
            if product.stock_quantity < input_data.new_quantity:
                raise InsufficientStockException(
                    f"Only {product.stock_quantity} items available in stock"
                )
            
            # Update quantity
            updated_item = self.cart_repository.update_cart_item_quantity(
                input_data.cart_item_id,
                input_data.new_quantity
            )
            
            return UpdateCartItemOutputData(
                success=True,
                cart_item_id=updated_item.cart_item_id,
                new_quantity=updated_item.quantity,
                message=f"Quantity updated to {input_data.new_quantity}"
            )
            
        except (CartItemNotFoundException, InsufficientStockException, ValidationException) as e:
            return UpdateCartItemOutputData(
                success=False,
                error_message=str(e)
            )
        except Exception as e:
            return UpdateCartItemOutputData(
                success=False,
                error_message=f"An error occurred while updating cart item: {str(e)}"
            )

    def _validate_input(self, input_data: UpdateCartItemInputData) -> None:
        """Validate input data"""
        if input_data.user_id <= 0:
            raise ValidationException("Invalid user ID")
        
        if input_data.cart_item_id <= 0:
            raise ValidationException("Invalid cart item ID")
        
        if input_data.new_quantity <= 0:
            raise ValidationException("Quantity must be positive")
        
        if input_data.new_quantity > 100:
            raise ValidationException("Cannot have more than 100 items")
