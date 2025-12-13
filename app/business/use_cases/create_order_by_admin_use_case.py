"""Create order by admin use case"""
from dataclasses import dataclass
from typing import List
from decimal import Decimal
from app.business.ports.order_repository import IOrderRepository
from app.business.ports.product_repository import IProductRepository
from app.business.ports.user_repository import IUserRepository
from app.domain.entities.order import Order, OrderItem
from app.domain.value_objects.email import Email
from app.domain.value_objects.money import Money
from app.domain.enums import OrderStatus, PaymentMethod


@dataclass
class OrderItemInput:
    """Input data for an order item"""
    product_id: int
    quantity: int
    unit_price: float


@dataclass
class CreateOrderByAdminInputData:
    """Input data for creating an order by admin"""
    customer_email: str
    customer_phone: str
    shipping_address: str
    payment_method: str
    items: List[OrderItemInput]
    notes: str = ""
    user_id: int = None  # Optional: can be None for guest orders


@dataclass
class CreateOrderByAdminOutputData:
    """Output data for creating an order"""
    success: bool
    order_id: int = None
    message: str = ""


class CreateOrderByAdminUseCase:
    """Use case for creating an order by admin"""
    
    def __init__(
        self,
        order_repository: IOrderRepository,
        product_repository: IProductRepository,
        user_repository: IUserRepository
    ):
        self.order_repository = order_repository
        self.product_repository = product_repository
        self.user_repository = user_repository
    
    def execute(self, input_data: CreateOrderByAdminInputData) -> CreateOrderByAdminOutputData:
        """Execute the create order use case"""
        try:
            # Verify user exists if user_id is provided
            user_id = input_data.user_id
            if user_id:
                user = self.user_repository.get_by_id(user_id)
                if not user:
                    return CreateOrderByAdminOutputData(
                        success=False,
                        message=f"User {user_id} not found"
                    )
            
            # Validate items
            if not input_data.items or len(input_data.items) == 0:
                return CreateOrderByAdminOutputData(
                    success=False,
                    message="Order must have at least one item"
                )
            
            # Create order items
            order_items = []
            subtotal = 0.0
            
            for item_input in input_data.items:
                # Verify product exists
                product = self.product_repository.find_by_id(item_input.product_id)
                if not product:
                    return CreateOrderByAdminOutputData(
                        success=False,
                        message=f"Product {item_input.product_id} not found"
                    )
                
                # Create order item
                unit_price_money = Money(Decimal(str(item_input.unit_price)))
                order_item = OrderItem(
                    product_id=item_input.product_id,
                    product_name=product.name,
                    quantity=item_input.quantity,
                    unit_price=unit_price_money
                )
                order_items.append(order_item)
                subtotal += item_input.quantity * item_input.unit_price
            
            # Get customer_id (use user_id if provided, otherwise use 1 as guest placeholder)
            # Note: For guest orders, we use customer_id=1 (admin/system user) as placeholder
            customer_id = input_data.user_id if input_data.user_id else 1
            
            # For guest orders (customer_id=0), we should store email and phone in notes
            notes = input_data.notes
            if not input_data.user_id:
                notes = f"Guest Order - Email: {input_data.customer_email}, Phone: {input_data.customer_phone}"
                if input_data.notes:
                    notes += f"\nNotes: {input_data.notes}"
            
            # Create order
            order = Order(
                customer_id=customer_id,
                items=order_items,
                payment_method=PaymentMethod[input_data.payment_method],
                shipping_address=input_data.shipping_address,
                phone_number=input_data.customer_phone,
                notes=notes
            )
            
            # Save order
            saved_order = self.order_repository.save(order)
            order_id = saved_order.id
            
            return CreateOrderByAdminOutputData(
                success=True,
                order_id=order_id,
                message="Order created successfully"
            )
            
        except Exception as e:
            return CreateOrderByAdminOutputData(
                success=False,
                message=f"Failed to create order: {str(e)}"
            )
