"""
Cart Domain Entity - Shopping cart aggregate root
NO framework dependencies!
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict
from ..value_objects import Money
from ..exceptions import InvalidQuantityException, EmptyCartException, ProductNotFoundException


class CartItem:
    """
    Cart item value object (part of Cart aggregate)
    
    Business Rules:
    - Quantity must be positive
    - Can update quantity
    """
    
    def __init__(self, product_id: int, quantity: int, cart_item_id: Optional[int] = None, cart_id: Optional[int] = None):
        """
        Create cart item
        
        Args:
            product_id: Product ID
            quantity: Quantity
            cart_item_id: Cart item ID (for persistence)
            cart_id: Cart ID (for persistence)
            
        Raises:
            InvalidQuantityException: If quantity is invalid
            ValueError: If product_id is invalid
        """
        if product_id <= 0:
            raise ValueError("Invalid product ID")
        if quantity <= 0:
            raise InvalidQuantityException(quantity)
        
        self._product_id = product_id
        self._quantity = quantity
        self._cart_item_id = cart_item_id
        self._cart_id = cart_id
    
    @property
    def product_id(self) -> int:
        return self._product_id
    
    @property
    def quantity(self) -> int:
        return self._quantity
    
    @property
    def cart_item_id(self) -> Optional[int]:
        return self._cart_item_id
    
    @property
    def cart_id(self) -> Optional[int]:
        return self._cart_id
    
    def update_quantity(self, new_quantity: int):
        """
        Update item quantity
        
        Args:
            new_quantity: New quantity
            
        Raises:
            InvalidQuantityException: If quantity is invalid
        """
        if new_quantity <= 0:
            raise InvalidQuantityException(new_quantity)
        self._quantity = new_quantity
    
    def increase_quantity(self, amount: int = 1):
        """Increase quantity by amount"""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self._quantity += amount
    
    def decrease_quantity(self, amount: int = 1):
        """
        Decrease quantity by amount
        
        Raises:
            InvalidQuantityException: If result would be <= 0
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")
        new_quantity = self._quantity - amount
        if new_quantity <= 0:
            raise InvalidQuantityException(new_quantity)
        self._quantity = new_quantity
    
    def __eq__(self, other) -> bool:
        """Check equality based on product_id"""
        if not isinstance(other, CartItem):
            return False
        return self._product_id == other._product_id
    
    def __hash__(self) -> int:
        """Hash based on product_id"""
        return hash(self._product_id)
    
    def __repr__(self) -> str:
        return f"CartItem(product_id={self._product_id}, quantity={self._quantity})"


class Cart:
    """
    Shopping Cart domain entity (Aggregate Root)
    
    Business Rules:
    - One cart per customer
    - Can add, remove, update items
    - Cart can be cleared
    - Must have items to checkout
    """
    
    def __init__(self, customer_id: int):
        """
        Create a new cart
        
        Args:
            customer_id: Customer user ID
            
        Raises:
            ValueError: If customer_id is invalid
        """
        if customer_id <= 0:
            raise ValueError("Invalid customer ID")
        
        self._id: Optional[int] = None
        self._customer_id = customer_id
        self._items: Dict[int, CartItem] = {}  # product_id -> CartItem
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
    
    @staticmethod
    def reconstruct(
        cart_id: int,
        customer_id: int,
        items: List[CartItem],
        created_at: datetime,
        updated_at: datetime
    ) -> 'Cart':
        """Reconstruct cart from database (no validation)"""
        cart = object.__new__(Cart)
        cart._id = cart_id
        cart._customer_id = customer_id
        cart._items = {item.product_id: item for item in items}
        cart._created_at = created_at
        cart._updated_at = updated_at
        return cart
    
    # Getters
    @property
    def id(self) -> Optional[int]:
        return self._id
    
    @property
    def customer_id(self) -> int:
        return self._customer_id
    
    @property
    def items(self) -> List[CartItem]:
        """Return list of cart items"""
        return list(self._items.values())
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    # Business methods
    def add_item(self, product_id: int, quantity: int = 1):
        """
        Add item to cart or increase quantity if already exists
        
        Args:
            product_id: Product ID
            quantity: Quantity to add
            
        Raises:
            ValueError: If product_id is invalid
            InvalidQuantityException: If quantity is invalid
        """
        if product_id <= 0:
            raise ValueError("Invalid product ID")
        if quantity <= 0:
            raise InvalidQuantityException(quantity)
        
        if product_id in self._items:
            # Product already in cart, increase quantity
            self._items[product_id].increase_quantity(quantity)
        else:
            # Add new item
            self._items[product_id] = CartItem(product_id, quantity)
        
        self._updated_at = datetime.now()
    
    def remove_item(self, product_id: int):
        """
        Remove item from cart
        
        Args:
            product_id: Product ID
            
        Raises:
            ProductNotFoundException: If product not in cart
        """
        if product_id not in self._items:
            raise ProductNotFoundException(product_id)
        
        del self._items[product_id]
        self._updated_at = datetime.now()
    
    def update_item_quantity(self, product_id: int, new_quantity: int):
        """
        Update item quantity
        
        Args:
            product_id: Product ID
            new_quantity: New quantity
            
        Raises:
            ProductNotFoundException: If product not in cart
            InvalidQuantityException: If quantity is invalid
        """
        if product_id not in self._items:
            raise ProductNotFoundException(product_id)
        
        self._items[product_id].update_quantity(new_quantity)
        self._updated_at = datetime.now()
    
    def clear(self):
        """Clear all items from cart"""
        self._items.clear()
        self._updated_at = datetime.now()
    
    def is_empty(self) -> bool:
        """Check if cart is empty"""
        return len(self._items) == 0
    
    def get_item_count(self) -> int:
        """Get number of distinct products in cart"""
        return len(self._items)
    
    def get_total_quantity(self) -> int:
        """Get total quantity of all items"""
        return sum(item.quantity for item in self._items.values())
    
    def has_item(self, product_id: int) -> bool:
        """Check if cart has specific product"""
        return product_id in self._items
    
    def get_item(self, product_id: int) -> Optional[CartItem]:
        """Get cart item by product ID"""
        return self._items.get(product_id)
    
    def ensure_not_empty(self):
        """
        Ensure cart is not empty
        
        Raises:
            EmptyCartException: If cart is empty
        """
        if self.is_empty():
            raise EmptyCartException()
    
    def belongs_to_customer(self, customer_id: int) -> bool:
        """Check if cart belongs to customer"""
        return self._customer_id == customer_id
    
    def __eq__(self, other) -> bool:
        """Check equality based on ID"""
        if not isinstance(other, Cart):
            return False
        return self._id is not None and self._id == other._id
    
    def __hash__(self) -> int:
        """Hash based on ID"""
        return hash(self._id) if self._id else hash(self._customer_id)
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"Cart(id={self._id}, customer_id={self._customer_id}, items={len(self._items)})"
