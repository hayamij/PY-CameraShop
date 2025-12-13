"""
Order Domain Entity - Rich aggregate root with business logic
NO framework dependencies!
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from ..enums import OrderStatus, PaymentMethod
from ..value_objects import Money
from ..exceptions import (
    EmptyOrderException,
    InvalidOrderStatusTransitionException,
    OrderAlreadyShippedException
)


class OrderItem:
    """
    Order item value object (part of Order aggregate)
    
    Business Rules:
    - Quantity must be positive
    - Price is captured at order time (not reference to product)
    """
    
    def __init__(self, product_id: int, product_name: str, quantity: int, unit_price: Money):
        """
        Create order item
        
        Args:
            product_id: Product ID
            product_name: Product name (captured at order time)
            quantity: Quantity ordered
            unit_price: Price per unit at order time
            
        Raises:
            ValueError: If validation fails
        """
        if product_id <= 0:
            raise ValueError("Invalid product ID")
        if not product_name:
            raise ValueError("Product name cannot be empty")
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if unit_price.amount <= 0:
            raise ValueError("Unit price must be positive")
        
        self._product_id = product_id
        self._product_name = product_name
        self._quantity = quantity
        self._unit_price = unit_price
    
    @property
    def product_id(self) -> int:
        return self._product_id
    
    @property
    def product_name(self) -> str:
        return self._product_name
    
    @property
    def quantity(self) -> int:
        return self._quantity
    
    @property
    def unit_price(self) -> Money:
        return self._unit_price
    
    def calculate_subtotal(self) -> Money:
        """Calculate subtotal for this item"""
        return self._unit_price.multiply(Decimal(self._quantity))
    
    def __repr__(self) -> str:
        return f"OrderItem(product_id={self._product_id}, quantity={self._quantity}, unit_price={self._unit_price})"


class Order:
    """
    Order domain entity (Aggregate Root)
    
    Business Rules:
    - Order must have at least one item
    - Total is calculated from items
    - Status transitions are restricted
    - Only PENDING orders can be cancelled
    - Shipped orders cannot be modified
    """
    
    def __init__(
        self,
        customer_id: int,
        items: List[OrderItem],
        payment_method: PaymentMethod,
        shipping_address: str,
        phone_number: str,
        notes: Optional[str] = ""
    ):
        """
        Create a new order
        
        Args:
            customer_id: Customer user ID
            items: List of order items
            payment_method: Payment method
            shipping_address: Shipping address
            phone_number: Customer phone number
            notes: Optional order notes
            
        Raises:
            EmptyOrderException: If order has no items
            ValueError: If validation fails
        """
        if not items or len(items) == 0:
            raise EmptyOrderException()
        if customer_id <= 0:
            raise ValueError("Invalid customer ID")
        if not shipping_address or len(shipping_address) < 10:
            raise ValueError("Shipping address must be at least 10 characters")
        if not phone_number or len(phone_number) < 10:
            raise ValueError("Phone number must be at least 10 characters")
        
        self._id: Optional[int] = None
        self._customer_id = customer_id
        self._items = items.copy()  # Defensive copy
        self._payment_method = payment_method
        self._shipping_address = shipping_address.strip()
        self._phone_number = phone_number.strip()
        self._notes = notes.strip() if notes else ""
        self._status = OrderStatus.PENDING
        self._total_amount = self._calculate_total()
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
    
    @staticmethod
    def reconstruct(
        order_id: int,
        customer_id: int,
        items: List[OrderItem],
        payment_method: PaymentMethod,
        shipping_address: str,
        phone_number: str,
        notes: str,
        status: OrderStatus,
        total_amount: Money,
        created_at: datetime,
        updated_at: datetime
    ) -> 'Order':
        """Reconstruct order from database (no validation)"""
        order = object.__new__(Order)
        order._id = order_id
        order._customer_id = customer_id
        order._items = items
        order._payment_method = payment_method
        order._shipping_address = shipping_address
        order._phone_number = phone_number
        order._notes = notes
        order._status = status
        order._total_amount = total_amount
        order._created_at = created_at
        order._updated_at = updated_at
        return order
    
    # Getters
    @property
    def id(self) -> Optional[int]:
        return self._id
    
    @property
    def customer_id(self) -> int:
        return self._customer_id
    
    @property
    def items(self) -> List[OrderItem]:
        return self._items.copy()  # Return defensive copy
    
    @property
    def payment_method(self) -> PaymentMethod:
        return self._payment_method
    
    @property
    def shipping_address(self) -> str:
        return self._shipping_address
    
    @property
    def phone_number(self) -> str:
        return self._phone_number
    
    @property
    def notes(self) -> str:
        return self._notes
    
    @property
    def status(self) -> OrderStatus:
        return self._status
    
    @property
    def total_amount(self) -> Money:
        return self._total_amount
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    # Business methods
    def _calculate_total(self) -> Money:
        """Calculate total amount from items"""
        total = Money(Decimal('0'), 'VND')
        for item in self._items:
            total = total.add(item.calculate_subtotal())
        return total
    
    def ship(self):
        """
        Mark order as shipping
        
        Raises:
            InvalidOrderStatusTransitionException: If transition is invalid
        """
        if not self._status.can_transition_to(OrderStatus.SHIPPING):
            allowed = []
            if self._status == OrderStatus.PENDING:
                allowed = ["SHIPPING", "CANCELLED"]
            raise InvalidOrderStatusTransitionException(
                str(self._status),
                str(OrderStatus.SHIPPING),
                allowed
            )
        self._status = OrderStatus.SHIPPING
        self._updated_at = datetime.now()
    
    def complete(self):
        """
        Mark order as completed
        
        Raises:
            InvalidOrderStatusTransitionException: If transition is invalid
        """
        if not self._status.can_transition_to(OrderStatus.COMPLETED):
            allowed = []
            if self._status == OrderStatus.SHIPPING:
                allowed = ["COMPLETED"]
            raise InvalidOrderStatusTransitionException(
                str(self._status),
                str(OrderStatus.COMPLETED),
                allowed
            )
        self._status = OrderStatus.COMPLETED
        self._updated_at = datetime.now()
    
    def cancel(self):
        """
        Cancel the order
        
        Raises:
            InvalidOrderStatusTransitionException: If order cannot be cancelled
            OrderAlreadyShippedException: If order is already shipped
        """
        if self._status == OrderStatus.SHIPPING or self._status == OrderStatus.COMPLETED:
            raise OrderAlreadyShippedException(self._id or 0)
        
        if not self._status.can_transition_to(OrderStatus.CANCELLED):
            allowed = []
            if self._status == OrderStatus.PENDING:
                allowed = ["SHIPPING", "CANCELLED"]
            raise InvalidOrderStatusTransitionException(
                str(self._status),
                str(OrderStatus.CANCELLED),
                allowed
            )
        
        self._status = OrderStatus.CANCELLED
        self._updated_at = datetime.now()
    
    def update_status(self, new_status: OrderStatus):
        """
        Generic method to update order status
        Used by admin panel for flexible status updates
        
        Args:
            new_status: New order status
            
        Raises:
            InvalidOrderStatusTransitionException: If transition is invalid
        """
        if not self._status.can_transition_to(new_status):
            raise InvalidOrderStatusTransitionException(
                str(self._status),
                str(new_status)
            )
        
        self._status = new_status
        self._updated_at = datetime.now()
    
    def is_pending(self) -> bool:
        """Check if order is pending"""
        return self._status == OrderStatus.PENDING
    
    def is_shipping(self) -> bool:
        """Check if order is shipping"""
        return self._status == OrderStatus.SHIPPING
    
    def is_completed(self) -> bool:
        """Check if order is completed"""
        return self._status == OrderStatus.COMPLETED
    
    def is_cancelled(self) -> bool:
        """Check if order is cancelled"""
        return self._status == OrderStatus.CANCELLED
    
    def can_be_cancelled(self) -> bool:
        """Check if order can be cancelled"""
        return self._status.is_modifiable()
    
    def can_be_modified(self) -> bool:
        """Check if order can be modified"""
        return self._status.is_modifiable()
    
    def get_item_count(self) -> int:
        """Get total number of items"""
        return len(self._items)
    
    def get_total_quantity(self) -> int:
        """Get total quantity of all items"""
        return sum(item.quantity for item in self._items)
    
    def belongs_to_customer(self, customer_id: int) -> bool:
        """Check if order belongs to customer"""
        return self._customer_id == customer_id
    
    def __eq__(self, other) -> bool:
        """Check equality based on ID"""
        if not isinstance(other, Order):
            return False
        return self._id is not None and self._id == other._id
    
    def __hash__(self) -> int:
        """Hash based on ID"""
        return hash(self._id) if self._id else hash((self._customer_id, self._created_at))
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"Order(id={self._id}, customer_id={self._customer_id}, status={self._status}, total={self._total_amount})"
