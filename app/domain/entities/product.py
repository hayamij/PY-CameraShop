"""
Product Domain Entity - Rich model with business logic
NO framework dependencies!
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from ..value_objects import Money
from ..exceptions import InvalidProductPriceException, InsufficientStockException


class Product:
    """
    Product domain entity with business rules
    
    Business Rules:
    - Price must be positive
    - Stock quantity cannot be negative
    - Products can be hidden without deletion
    - Stock reservation for orders
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        price: Money,
        stock_quantity: int,
        category_id: int,
        brand_id: int,
        image_url: Optional[str] = None
    ):
        """
        Create a new product
        
        Args:
            name: Product name
            description: Product description
            price: Money value object
            stock_quantity: Initial stock quantity
            category_id: Category ID
            brand_id: Brand ID
            image_url: Product image URL
            
        Raises:
            ValueError: If validation fails
            InvalidProductPriceException: If price is invalid
        """
        if not name or len(name) < 2:
            raise ValueError("Product name must be at least 2 characters")
        if not description:
            raise ValueError("Product description cannot be empty")
        if price.amount <= 0:
            raise InvalidProductPriceException(price)
        if stock_quantity < 0:
            raise ValueError("Stock quantity cannot be negative")
        if category_id <= 0:
            raise ValueError("Invalid category ID")
        if brand_id <= 0:
            raise ValueError("Invalid brand ID")
        
        self._id: Optional[int] = None
        self._name = name.strip()
        self._description = description.strip()
        self._price = price
        self._stock_quantity = stock_quantity
        self._category_id = category_id
        self._brand_id = brand_id
        self._image_url = image_url
        self._is_visible = True
        self._created_at = datetime.now()
    
    @staticmethod
    def reconstruct(
        product_id: int,
        name: str,
        description: str,
        price: Money,
        stock_quantity: int,
        category_id: int,
        brand_id: int,
        image_url: Optional[str],
        is_visible: bool,
        created_at: datetime
    ) -> 'Product':
        """Reconstruct product from database (no validation)"""
        product = object.__new__(Product)
        product._id = product_id
        product._name = name
        product._description = description
        product._price = price
        product._stock_quantity = stock_quantity
        product._category_id = category_id
        product._brand_id = brand_id
        product._image_url = image_url
        product._is_visible = is_visible
        product._created_at = created_at
        return product
    
    # Getters
    @property
    def id(self) -> Optional[int]:
        return self._id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def price(self) -> Money:
        return self._price
    
    @property
    def stock_quantity(self) -> int:
        return self._stock_quantity
    
    @property
    def category_id(self) -> int:
        return self._category_id
    
    @property
    def brand_id(self) -> int:
        return self._brand_id
    
    @property
    def image_url(self) -> Optional[str]:
        return self._image_url
    
    @property
    def is_visible(self) -> bool:
        return self._is_visible
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    # Business methods
    def update_details(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[Money] = None,
        category_id: Optional[int] = None,
        brand_id: Optional[int] = None,
        image_url: Optional[str] = None
    ):
        """Update product details"""
        if name:
            if len(name) < 2:
                raise ValueError("Product name must be at least 2 characters")
            self._name = name.strip()
        
        if description:
            self._description = description.strip()
        
        if price:
            if price.amount <= 0:
                raise InvalidProductPriceException(price)
            self._price = price
        
        if category_id:
            if category_id <= 0:
                raise ValueError("Invalid category ID")
            self._category_id = category_id
        
        if brand_id:
            if brand_id <= 0:
                raise ValueError("Invalid brand ID")
            self._brand_id = brand_id
        
        if image_url is not None:
            self._image_url = image_url
    
    def update_price(self, new_price: Money):
        """
        Update product price
        
        Args:
            new_price: New price
            
        Raises:
            InvalidProductPriceException: If price is invalid
        """
        if new_price.amount <= 0:
            raise InvalidProductPriceException(new_price)
        self._price = new_price
    
    def add_stock(self, quantity: int):
        """
        Add stock quantity
        
        Args:
            quantity: Quantity to add
            
        Raises:
            ValueError: If quantity is invalid
        """
        if quantity <= 0:
            raise ValueError("Quantity to add must be positive")
        self._stock_quantity += quantity
    
    def reduce_stock(self, quantity: int):
        """
        Reduce stock quantity (when order is placed)
        
        Args:
            quantity: Quantity to reduce
            
        Raises:
            InsufficientStockException: If not enough stock
        """
        if quantity <= 0:
            raise ValueError("Quantity to reduce must be positive")
        
        if self._stock_quantity < quantity:
            raise InsufficientStockException(
                self._id or 0,
                quantity,
                self._stock_quantity
            )
        
        self._stock_quantity -= quantity
    
    def restore_stock(self, quantity: int):
        """
        Restore stock quantity (when order is cancelled)
        
        Args:
            quantity: Quantity to restore
            
        Raises:
            ValueError: If quantity is invalid
        """
        if quantity <= 0:
            raise ValueError("Quantity to restore must be positive")
        self._stock_quantity += quantity
    
    def is_in_stock(self) -> bool:
        """Check if product is in stock"""
        return self._stock_quantity > 0
    
    def has_sufficient_stock(self, required_quantity: int) -> bool:
        """Check if there's sufficient stock for required quantity"""
        return self._stock_quantity >= required_quantity
    
    def hide(self):
        """Hide product from catalog"""
        if not self._is_visible:
            raise ValueError("Product is already hidden")
        self._is_visible = False
    
    def show(self):
        """Show product in catalog"""
        if self._is_visible:
            raise ValueError("Product is already visible")
        self._is_visible = True
    
    def is_available_for_purchase(self) -> bool:
        """Check if product is available for purchase"""
        return self._is_visible and self.is_in_stock()
    
    def calculate_total_price(self, quantity: int) -> Money:
        """
        Calculate total price for given quantity
        
        Args:
            quantity: Quantity of products
            
        Returns:
            Total price as Money object
            
        Raises:
            ValueError: If quantity is invalid
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        return self._price.multiply(Decimal(quantity))
    
    def __eq__(self, other) -> bool:
        """Check equality based on ID"""
        if not isinstance(other, Product):
            return False
        return self._id is not None and self._id == other._id
    
    def __hash__(self) -> int:
        """Hash based on ID"""
        return hash(self._id) if self._id else hash(self._name)
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"Product(id={self._id}, name='{self._name}', price={self._price})"
