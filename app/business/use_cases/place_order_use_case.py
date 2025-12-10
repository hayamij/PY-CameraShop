"""
Use Case: Place Order

Business Logic:
- Validates user has items in cart
- Validates shipping information
- Validates payment method
- Creates order entity from cart items
- Clears cart after successful order placement
- Calculates order total from cart
"""

from dataclasses import dataclass
from typing import Optional
from app.domain.entities.order import Order
from app.domain.value_objects.money import Money
from app.domain.enums import PaymentMethod
from app.business.ports.order_repository import IOrderRepository
from app.business.ports.cart_repository import ICartRepository
from app.business.ports.product_repository import IProductRepository
from app.domain.exceptions import ValidationException, InsufficientStockException


@dataclass
class PlaceOrderInputData:
    """Input data for placing an order"""
    user_id: int
    shipping_address: str
    phone_number: str
    payment_method: str
    notes: Optional[str] = ""


@dataclass
@dataclass
class PlaceOrderOutputData:
    """Output data after placing an order"""
    success: bool
    message: str = ""
    error_message: str = ""
    order_id: Optional[int] = None
    order_total: Optional[float] = 0
    total_amount: Optional[float] = 0  # Alias for compatibility


class PlaceOrderUseCase:
    """Use case for placing a new order from cart"""
    
    def __init__(
        self,
        order_repository: IOrderRepository,
        cart_repository: ICartRepository,
        product_repository: IProductRepository
    ):
        """
        Initialize the use case.
        
        Args:
            order_repository: Repository for order persistence
            cart_repository: Repository for cart operations
            product_repository: Repository for product stock management
        """
        self.order_repository = order_repository
        self.cart_repository = cart_repository
        self.product_repository = product_repository
    
    def execute(self, input_data: PlaceOrderInputData) -> PlaceOrderOutputData:
        """
        Execute the place order use case.
        
        Args:
            input_data: Input data containing order information
            
        Returns:
            PlaceOrderOutputData with operation result
            
        """
        try:
            # Validate input
            self._validate_input(input_data)
            
            # Get user's cart
            cart = self.cart_repository.find_by_user_id(input_data.user_id)
            if cart is None or not cart.items:
                raise ValidationException("Cart is empty. Cannot place order.")
            
            # Validate stock availability for all items
            for cart_item in cart.items:
                product = self.product_repository.find_by_id(cart_item.product_id)
                if product is None:
                    raise ValidationException(f"Product with ID {cart_item.product_id} not found")
                
                if not product.is_visible:
                    raise ValidationException(f"Product '{product.name}' is no longer available")
                
                if product.stock_quantity < cart_item.quantity:
                    raise InsufficientStockException(
                        product_id=product.id,  # Product entity uses .id, not .product_id
                        requested=cart_item.quantity,
                        available=product.stock_quantity
                    )
            
            # Calculate total from cart by loading each product
            from decimal import Decimal
            total_amount = Decimal('0')
            for item in cart.items:
                product = self.product_repository.find_by_id(item.product_id)
                if product:
                    total_amount += product.price.amount * item.quantity
            
            # Parse payment method
            try:
                payment_method_enum = PaymentMethod[input_data.payment_method.upper()]
            except KeyError:
                raise ValidationException(f"Invalid payment method: {input_data.payment_method}")
            
            # Create OrderItem entities from cart items
            from app.domain.entities.order import OrderItem
            order_items = []
            for cart_item in cart.items:
                product = self.product_repository.find_by_id(cart_item.product_id)
                order_item = OrderItem(
                    product_id=product.id,  # Product entity uses .id, not .product_id
                    product_name=product.name,
                    quantity=cart_item.quantity,
                    unit_price=product.price
                )
                order_items.append(order_item)
            
            # Create order entity
            order = Order(
                customer_id=input_data.user_id,
                items=order_items,
                payment_method=payment_method_enum,
                shipping_address=input_data.shipping_address,
                phone_number=input_data.phone_number,
                notes=input_data.notes
            )
            
            # Reduce product stock for each item
            for order_item in order.items:
                product = self.product_repository.find_by_id(order_item.product_id)
                product.reduce_stock(order_item.quantity)
                self.product_repository.save(product)
            
            # Save order
            saved_order = self.order_repository.save(order)
        
            # Clear cart after successful order
            self.cart_repository.clear_cart(input_data.user_id)
            
            return PlaceOrderOutputData(
                success=True,
                order_id=saved_order.id,
                order_total=saved_order.total_amount.amount,
                total_amount=saved_order.total_amount.amount,
                message=f"Order #{saved_order.id} placed successfully"
            )
        
        except (ValidationException, InsufficientStockException) as e:
            return PlaceOrderOutputData(
                success=False,
                error_message=str(e)
            )
        except Exception as e:
            return PlaceOrderOutputData(
                success=False,
                error_message=f"An error occurred while placing order: {str(e)}"
            )
    
    def _validate_input(self, input_data: PlaceOrderInputData) -> None:
        """
        Validate input data.
        
        Args:
            input_data: Input data to validate
            
        Raises:
            ValidationException: If validation fails
        """
        if input_data.user_id <= 0:
            raise ValidationException("Invalid user ID")
        
        if not input_data.shipping_address or len(input_data.shipping_address.strip()) < 10:
            raise ValidationException("Shipping address must be at least 10 characters")
        
        if not input_data.phone_number or len(input_data.phone_number.strip()) < 10:
            raise ValidationException("Phone number must be at least 10 digits")
        
        if not input_data.payment_method:
            raise ValidationException("Payment method is required")
