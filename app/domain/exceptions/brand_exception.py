"""Brand-specific domain exceptions"""


class BrandException(Exception):
    """Base exception for brand-related errors"""
    pass


class BrandNotFoundException(BrandException):
    """Raised when a brand is not found"""
    
    def __init__(self, brand_id: int):
        self.brand_id = brand_id
        super().__init__(f"Brand with ID {brand_id} not found")


class BrandAlreadyExistsException(BrandException):
    """Raised when attempting to create a brand with duplicate name"""
    
    def __init__(self, brand_name: str):
        self.brand_name = brand_name
        super().__init__(f"Brand '{brand_name}' already exists")


class BrandHasProductsException(BrandException):
    """Raised when attempting to delete a brand that has products"""
    
    def __init__(self, brand_name: str, product_count: int):
        self.brand_name = brand_name
        self.product_count = product_count
        super().__init__(
            f"Cannot delete brand '{brand_name}' because it has {product_count} product(s)"
        )
