"""Add to Cart Use Case - Add product to user's cart"""
from dataclasses import dataclass
from typing import Optional
from app.business.ports.cart_repository import ICartRepository
from app.business.ports.product_repository import IProductRepository
from app.domain.exceptions import (
    ProductNotFoundException,
    InsufficientStockException,
    ValidationException
)


@dataclass
class AddToCartInputData:
    """Input data for adding to cart"""
    user_id: int
    product_id: int
    quantity: int = 1


@dataclass
class AddToCartOutputData:
    """Output data for adding to cart"""
    success: bool
    cart_id: Optional[int] = None
    cart_item_id: Optional[int] = None
    message: str = ""
    error_message: str = ""
    total_items: int = 0
    cart_total: float = 0.0


class AddToCartUseCase:
    """Use case for adding a product to the shopping cart"""

    def __init__(
        self,
        cart_repository: ICartRepository,
        product_repository: IProductRepository
    ):
        self.cart_repository = cart_repository
        self.product_repository = product_repository

    def execute(self, input_data: AddToCartInputData) -> AddToCartOutputData:
        """
        Execute the add to cart use case
        
        Business Rules:
        - User must be authenticated (user_id provided)
        - Product must exist and be visible
        - Product must have sufficient stock
        - Quantity must be positive
        - If item already in cart, update quantity
        - Total quantity cannot exceed stock
        """
        try:
            # Validate input
            self._validate_input(input_data)
            
            # Find product
            product = self.product_repository.find_by_id(input_data.product_id)
            if not product:
                raise ProductNotFoundException(
                    f"Product with ID {input_data.product_id} not found"
                )
            
            # Check if product is visible
            if not product.is_visible:
                return AddToCartOutputData(
                    success=False,
                    error_message="This product is not available"
                )
            
            # Check stock availability
            if product.stock_quantity < input_data.quantity:
                raise InsufficientStockException(
                    f"Only {product.stock_quantity} items available in stock"
                )
            
            # Get or create cart for user
            cart = self.cart_repository.find_by_user_id(input_data.user_id)
            if not cart:
                cart = self.cart_repository.create_cart(input_data.user_id)
            
            # Check if product already in cart
            existing_item = self.cart_repository.find_cart_item(
                cart.id,
                input_data.product_id
            )
            
            if existing_item:
                # Update quantity of existing item
                new_quantity = existing_item.quantity + input_data.quantity
                
                # Check if new quantity exceeds stock
                if new_quantity > product.stock_quantity:
                    raise InsufficientStockException(
                        f"Cannot add {input_data.quantity} more items. "
                        f"Only {product.stock_quantity - existing_item.quantity} more available"
                    )
                
                # Update quantity
                updated_item = self.cart_repository.update_cart_item_quantity(
                    existing_item.cart_item_id,
                    new_quantity
                )
                
                message = f"Updated quantity to {new_quantity}"
                cart_item_id = updated_item.cart_item_id
            else:
                # Add new item to cart
                cart_item = self.cart_repository.add_item_to_cart(
                    cart.id,
                    input_data.product_id,
                    input_data.quantity
                )
                
                message = f"Added {input_data.quantity} item(s) to cart"
                cart_item_id = cart_item.cart_item_id
            
            # Get updated cart totals
            cart = self.cart_repository.find_by_user_id(input_data.user_id)
            total_items = len(cart.items)  # Count distinct items, not quantity sum
            # Calculate cart total using domain method
            cart_total = cart.get_total() if hasattr(cart, 'get_total') else 0
            
            return AddToCartOutputData(
                success=True,
                cart_id=cart.id,
                cart_item_id=cart_item_id,
                message=message,
                total_items=total_items,
                cart_total=cart_total
            )
            
        except (ProductNotFoundException, InsufficientStockException, ValidationException) as e:
            return AddToCartOutputData(
                success=False,
                error_message=str(e)
            )
        except Exception as e:
            return AddToCartOutputData(
                success=False,
                error_message=f"An error occurred while adding to cart: {str(e)}"
            )

    def _validate_input(self, input_data: AddToCartInputData) -> None:
        """Validate input data"""
        if input_data.user_id <= 0:
            raise ValidationException("Invalid user ID")
        
        if input_data.product_id <= 0:
            raise ValidationException("Invalid product ID")
        
        if input_data.quantity <= 0:
            raise ValidationException("Quantity must be positive")
        
        if input_data.quantity > 100:
            raise ValidationException("Cannot add more than 100 items at once")
