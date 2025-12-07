"""
Use Case: Create Category

Business Logic:
- Validates category name (minimum 3 characters)
- Checks for duplicate category names
- Creates category entity
- Saves category to repository
"""

from dataclasses import dataclass
from app.domain.entities.category import Category
from app.business.ports.category_repository import ICategoryRepository
from app.domain.exceptions import ValidationException, CategoryAlreadyExistsException


@dataclass
class CreateCategoryInputData:
    """Input data for creating a category"""
    name: str
    description: str = ""


@dataclass
class CreateCategoryOutputData:
    """Output data after creating a category"""
    success: bool
    category_id: int
    category_name: str
    message: str


class CreateCategoryUseCase:
    """Use case for creating a new category"""
    
    def __init__(self, category_repository: ICategoryRepository):
        """
        Initialize the use case.
        
        Args:
            category_repository: Repository for category persistence
        """
        self.category_repository = category_repository
    
    def execute(self, input_data: CreateCategoryInputData) -> CreateCategoryOutputData:
        """
        Execute the create category use case.
        
        Args:
            input_data: Input data containing category information
            
        Returns:
            CreateCategoryOutputData with operation result
            
        Raises:
            ValidationException: If input validation fails
            CategoryAlreadyExistsException: If category name already exists
        """
        # Validate input
        self._validate_input(input_data)
        
        # Check for duplicate name
        existing_category = self.category_repository.find_by_name(input_data.name)
        if existing_category is not None:
            raise CategoryAlreadyExistsException(input_data.name)
        
        # Create category entity
        category = Category(
            name=input_data.name,
            description=input_data.description
        )
        
        # Save category
        saved_category = self.category_repository.save(category)
        
        return CreateCategoryOutputData(
            success=True,
            category_id=saved_category.id,
            category_name=saved_category.name,
            message=f"Category '{saved_category.name}' created successfully"
        )
    
    def _validate_input(self, input_data: CreateCategoryInputData) -> None:
        """
        Validate input data.
        
        Args:
            input_data: Input data to validate
            
        Raises:
            ValidationException: If validation fails
        """
        if not input_data.name or len(input_data.name.strip()) < 3:
            raise ValidationException("Category name must be at least 3 characters")
        
        if len(input_data.name) > 100:
            raise ValidationException("Category name must not exceed 100 characters")
