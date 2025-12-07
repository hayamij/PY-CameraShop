"""
Use Case: Delete Category

Business Logic:
- Validates category exists
- Checks that no products are associated with the category
- Deletes category from repository
"""

from dataclasses import dataclass
from app.business.ports.category_repository import ICategoryRepository
from app.business.ports.product_repository import IProductRepository
from app.domain.exceptions import ValidationException, CategoryNotFoundException, CategoryHasProductsException


@dataclass
class DeleteCategoryInputData:
    """Input data for deleting a category"""
    category_id: int


@dataclass
class DeleteCategoryOutputData:
    """Output data after deleting a category"""
    success: bool
    category_id: int
    message: str


class DeleteCategoryUseCase:
    """Use case for deleting a category"""
    
    def __init__(
        self,
        category_repository: ICategoryRepository,
        product_repository: IProductRepository
    ):
        """
        Initialize the use case.
        
        Args:
            category_repository: Repository for category persistence
            product_repository: Repository for product queries
        """
        self.category_repository = category_repository
        self.product_repository = product_repository
    
    def execute(self, input_data: DeleteCategoryInputData) -> DeleteCategoryOutputData:
        """
        Execute the delete category use case.
        
        Args:
            input_data: Input data containing category ID
            
        Returns:
            DeleteCategoryOutputData with operation result
            
        Raises:
            ValidationException: If input validation fails
            CategoryNotFoundException: If category does not exist
            CategoryHasProductsException: If category has associated products
        """
        # Validate input
        if input_data.category_id <= 0:
            raise ValidationException("Invalid category ID")
        
        # Get category
        category = self.category_repository.find_by_id(input_data.category_id)
        if category is None:
            raise CategoryNotFoundException(input_data.category_id)
        
        # Check if category has products
        product_count = self.product_repository.count_by_category(input_data.category_id)
        if product_count > 0:
            raise CategoryHasProductsException(
                category.name,
                product_count
            )
        
        # Delete category
        category_name = category.name
        self.category_repository.delete(input_data.category_id)
        
        return DeleteCategoryOutputData(
            success=True,
            category_id=input_data.category_id,
            message=f"Category '{category_name}' deleted successfully"
        )
