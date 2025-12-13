"""
Domain Exceptions - Business rule violation exceptions
"""


class DomainException(Exception):
    """Base exception for all domain-level errors"""
    
    def __init__(self, message: str, error_code: str):
        """
        Initialize domain exception
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code


# User-related exceptions
class InvalidCredentialsException(DomainException):
    """Raised when user credentials are invalid"""
    
    def __init__(self):
        super().__init__(
            "Invalid username or password",
            "INVALID_CREDENTIALS"
        )


class UserAlreadyExistsException(DomainException):
    """Raised when trying to create a user that already exists"""
    
    def __init__(self, identifier: str):
        super().__init__(
            f"User with {identifier} already exists",
            "USER_ALREADY_EXISTS"
        )


class UserNotFoundException(DomainException):
    """Raised when user is not found"""
    
    def __init__(self, user_id: int):
        super().__init__(
            f"User with ID {user_id} not found",
            "USER_NOT_FOUND"
        )


# Product-related exceptions
class InsufficientStockException(DomainException):
    """Raised when product stock is insufficient"""
    
    def __init__(self, message: str = None, product_id: int = None, requested: int = None, available: int = None):
        if message:
            super().__init__(message, "INSUFFICIENT_STOCK")
        else:
            super().__init__(
                f"Product {product_id}: requested {requested}, but only {available} available",
                "INSUFFICIENT_STOCK"
            )


class ProductNotFoundException(DomainException):
    """Raised when product is not found"""
    
    def __init__(self, message: str = None, product_id: int = None):
        if message:
            super().__init__(message, "PRODUCT_NOT_FOUND")
        else:
            super().__init__(
                f"Product with ID {product_id} not found",
                "PRODUCT_NOT_FOUND"
            )


class InvalidProductPriceException(DomainException):
    """Raised when product price is invalid"""
    
    def __init__(self, price):
        super().__init__(
            f"Invalid product price: {price}",
            "INVALID_PRODUCT_PRICE"
        )


# Order-related exceptions
class EmptyOrderException(DomainException):
    """Raised when trying to create an order with no items"""
    
    def __init__(self):
        super().__init__(
            "Order must have at least one item",
            "EMPTY_ORDER"
        )


class OrderNotFoundException(DomainException):
    """Raised when order is not found"""
    
    def __init__(self, order_id: int):
        super().__init__(
            f"Order with ID {order_id} not found",
            "ORDER_NOT_FOUND"
        )


class OrderAlreadyShippedException(DomainException):
    """Raised when trying to modify a shipped order"""
    
    def __init__(self, order_id: int):
        super().__init__(
            f"Order {order_id} has already been shipped and cannot be modified",
            "ORDER_ALREADY_SHIPPED"
        )


# Cart-related exceptions
class CartNotFoundException(DomainException):
    """Raised when cart is not found"""
    
    def __init__(self, cart_id: int):
        super().__init__(
            f"Cart with ID {cart_id} not found",
            "CART_NOT_FOUND"
        )


class EmptyCartException(DomainException):
    """Raised when trying to checkout an empty cart"""
    
    def __init__(self):
        super().__init__(
            "Cannot checkout an empty cart",
            "EMPTY_CART"
        )


class InvalidQuantityException(DomainException):
    """Raised when quantity is invalid"""
    
    def __init__(self, quantity: int):
        super().__init__(
            f"Invalid quantity: {quantity}. Must be greater than 0",
            "INVALID_QUANTITY"
        )


# Authorization exceptions
class UnauthorizedAccessException(DomainException):
    """Raised when user tries to access unauthorized resource"""
    
    def __init__(self, resource: str):
        super().__init__(
            f"Unauthorized access to {resource}",
            "UNAUTHORIZED_ACCESS"
        )


class InsufficientPermissionsException(DomainException):
    """Raised when user lacks required permissions"""
    
    def __init__(self, required_role: str):
        super().__init__(
            f"Insufficient permissions. Required role: {required_role}",
            "INSUFFICIENT_PERMISSIONS"
        )


class ValidationException(DomainException):
    """Raised when input validation fails"""
    
    def __init__(self, message: str):
        super().__init__(
            message,
            "VALIDATION_ERROR"
        )


class CartItemNotFoundException(DomainException):
    """Raised when cart item is not found"""
    
    def __init__(self, cart_item_id: int):
        super().__init__(
            f"Cart item with ID {cart_item_id} not found",
            "CART_ITEM_NOT_FOUND"
        )


class InvalidOrderStatusTransitionException(DomainException):
    """Raised when trying to transition order to an invalid status"""
    
    def __init__(self, current_status: str, attempted_status: str, allowed_statuses: list):
        allowed = ', '.join(allowed_statuses) if allowed_statuses else 'none'
        super().__init__(
            f"Cannot transition order from {current_status} to {attempted_status}. Allowed transitions: {allowed}",
            "INVALID_ORDER_STATUS_TRANSITION"
        )


# Category-related exceptions
class CategoryNotFoundException(DomainException):
    """Raised when a category is not found"""
    
    def __init__(self, category_id: int):
        self.category_id = category_id
        super().__init__(
            f"Category with ID {category_id} not found",
            "CATEGORY_NOT_FOUND"
        )


class CategoryAlreadyExistsException(DomainException):
    """Raised when attempting to create a category with duplicate name"""
    
    def __init__(self, category_name: str):
        self.category_name = category_name
        super().__init__(
            f"Category '{category_name}' already exists",
            "CATEGORY_ALREADY_EXISTS"
        )


class CategoryHasProductsException(DomainException):
    """Raised when attempting to delete a category that has products"""
    
    def __init__(self, category_name: str, product_count: int):
        self.category_name = category_name
        self.product_count = product_count
        super().__init__(
            f"Cannot delete category '{category_name}' because it has {product_count} product(s)",
            "CATEGORY_HAS_PRODUCTS"
        )


# Brand-related exceptions
class BrandNotFoundException(DomainException):
    """Raised when a brand is not found"""
    
    def __init__(self, brand_id: int):
        self.brand_id = brand_id
        super().__init__(
            f"Brand with ID {brand_id} not found",
            "BRAND_NOT_FOUND"
        )


class BrandAlreadyExistsException(DomainException):
    """Raised when attempting to create a brand with duplicate name"""
    
    def __init__(self, brand_name: str):
        self.brand_name = brand_name
        super().__init__(
            f"Brand '{brand_name}' already exists",
            "BRAND_ALREADY_EXISTS"
        )


class BrandHasProductsException(DomainException):
    """Raised when attempting to delete a brand that has products"""
    
    def __init__(self, brand_name: str, product_count: int):
        self.brand_name = brand_name
        self.product_count = product_count
        super().__init__(
            f"Cannot delete brand '{brand_name}' because it has {product_count} product(s)",
            "BRAND_HAS_PRODUCTS"
        )
