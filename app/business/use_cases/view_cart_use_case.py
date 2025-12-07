"""View Cart Use Case - Retrieve user's cart with items"""
from dataclasses import dataclass
from typing import List, Optional
from decimal import Decimal
from app.business.ports.cart_repository import ICartRepository
from app.business.ports.product_repository import IProductRepository
from app.domain.exceptions import ValidationException


@dataclass
class CartItemOutputData:
    """Output data for a single cart item"""
    cart_item_id: int
    product_id: int
    product_name: str
    product_image: Optional[str]
    price: Decimal
    currency: str
    quantity: int
    subtotal: Decimal
    stock_available: int
    is_available: bool


@dataclass
class ViewCartOutputData:
    """Output data for viewing cart"""
    success: bool
    cart_id: Optional[int] = None
    items: List[CartItemOutputData] = None
    total_items: int = 0
    subtotal: Decimal = Decimal('0.00')
    tax: Decimal = Decimal('0.00')
    shipping: Decimal = Decimal('0.00')
    total: Decimal = Decimal('0.00')
    error_message: str = ""
    
    def __post_init__(self):
        if self.items is None:
            self.items = []


class ViewCartUseCase:
    """Use case for viewing the shopping cart"""

    def __init__(
        self,
        cart_repository: ICartRepository,
        product_repository: IProductRepository
    ):
        self.cart_repository = cart_repository
        self.product_repository = product_repository

    def execute(self, user_id: int) -> ViewCartOutputData:
        """
        Execute the view cart use case
        
        Business Rules:
        - User must be authenticated
        - Show all items in cart with current product info
        - Calculate totals (subtotal, tax, shipping, total)
        - Indicate if items are out of stock
        - Show available stock for each item
        """
        try:
            # Validate user ID
            if user_id <= 0:
                raise ValidationException("Invalid user ID")
            
            # Find cart for user
            cart = self.cart_repository.find_by_user_id(user_id)
            
            # If no cart exists, return empty cart
            if not cart or not cart.items:
                return ViewCartOutputData(
                    success=True,
                    cart_id=None,
                    items=[],
                    total_items=0,
                    subtotal=Decimal('0.00'),
                    tax=Decimal('0.00'),
                    shipping=Decimal('0.00'),
                    total=Decimal('0.00')
                )
            
            # Build cart items with product information
            cart_items = []
            subtotal = Decimal('0.00')
            
            for item in cart.items:
                # Get current product information
                product = self.product_repository.find_by_id(item.product_id)
                
                if product:
                    # Calculate item subtotal
                    item_subtotal = product.price * item.quantity
                    subtotal += item_subtotal
                    
                    # Check stock availability
                    is_available = (
                        product.is_visible and
                        product.stock_quantity >= item.quantity
                    )
                    
                    cart_items.append(CartItemOutputData(
                        cart_item_id=item.cart_item_id,
                        product_id=product.product_id,
                        product_name=product.name,
                        product_image=product.image_url,
                        price=product.price,
                        currency=product.currency,
                        quantity=item.quantity,
                        subtotal=item_subtotal,
                        stock_available=product.stock_quantity,
                        is_available=is_available
                    ))
            
            # Calculate tax and shipping
            tax = self._calculate_tax(subtotal)
            shipping = self._calculate_shipping(subtotal)
            total = subtotal + tax + shipping
            
            return ViewCartOutputData(
                success=True,
                cart_id=cart.cart_id,
                items=cart_items,
                total_items=len(cart_items),
                subtotal=subtotal,
                tax=tax,
                shipping=shipping,
                total=total
            )
            
        except ValidationException as e:
            return ViewCartOutputData(
                success=False,
                error_message=str(e)
            )
        except Exception as e:
            return ViewCartOutputData(
                success=False,
                error_message=f"An error occurred while viewing cart: {str(e)}"
            )

    def _calculate_tax(self, subtotal: Decimal) -> Decimal:
        """
        Calculate tax amount
        Business rule: 10% tax on subtotal
        """
        tax_rate = Decimal('0.10')
        return (subtotal * tax_rate).quantize(Decimal('0.01'))

    def _calculate_shipping(self, subtotal: Decimal) -> Decimal:
        """
        Calculate shipping cost
        Business rule: Free shipping for orders over $500, otherwise $20
        """
        free_shipping_threshold = Decimal('500.00')
        standard_shipping = Decimal('20.00')
        
        if subtotal >= free_shipping_threshold:
            return Decimal('0.00')
        else:
            return standard_shipping
