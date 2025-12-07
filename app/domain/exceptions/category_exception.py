"""Category-specific domain exceptions"""


class CategoryException(Exception):
    """Base exception for category-related errors"""
    pass


class CategoryNotFoundException(CategoryException):
    """Raised when a category is not found"""
    
    def __init__(self, category_id: int):
        self.category_id = category_id
        super().__init__(f"Category with ID {category_id} not found")


class CategoryAlreadyExistsException(CategoryException):
    """Raised when attempting to create a category with duplicate name"""
    
    def __init__(self, category_name: str):
        self.category_name = category_name
        super().__init__(f"Category '{category_name}' already exists")


class CategoryHasProductsException(CategoryException):
    """Raised when attempting to delete a category that has products"""
    
    def __init__(self, category_name: str, product_count: int):
        self.category_name = category_name
        self.product_count = product_count
        super().__init__(
            f"Cannot delete category '{category_name}' because it has {product_count} product(s)"
        )
