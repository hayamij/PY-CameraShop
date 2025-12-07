"""
Use Case: Update Category

Business Logic:
- Validates category exists
- Validates new name and description
- Checks for duplicate category names (excluding self)
- Updates category information
- Saves changes to repository
"""

from dataclasses import dataclass
from app.domain.entities.category import Category
from app.business.ports.category_repository import ICategoryRepository
from app.domain.exceptions import ValidationException, CategoryNotFoundException, CategoryAlreadyExistsException


@dataclass
class UpdateCategoryInputData:
    """Input data for updating a category"""
    category_id: int
    name: str
    description: str = ""


@dataclass
class UpdateCategoryOutputData:
    """Output data after updating a category"""
    success: bool
    category_id: int
    category_name: str
    message: str


class UpdateCategoryUseCase:
    """Use case for updating an existing category"""
    
    def __init__(self, category_repository: ICategoryRepository):
        """
        Initialize the use case.
        
        Args:
            category_repository: Repository for category persistence
        """
        self.category_repository = category_repository
    
    def execute(self, input_data: UpdateCategoryInputData) -> UpdateCategoryOutputData:
        """
        Execute the update category use case.
        
        Args:
            input_data: Input data containing updated category information
            
        Returns:
            UpdateCategoryOutputData with operation result
            
        Raises:
            ValidationException: If input validation fails
            CategoryNotFoundException: If category does not exist
            CategoryAlreadyExistsException: If new name conflicts with existing category
        """
        # Validate input
        self._validate_input(input_data)
        
        # Get existing category
        category = self.category_repository.find_by_id(input_data.category_id)
        if category is None:
            raise CategoryNotFoundException(input_data.category_id)
        
        # Check for duplicate name (excluding self)
        if input_data.name != category.name:
            existing_category = self.category_repository.find_by_name(input_data.name)
            if existing_category is not None and existing_category.id != category.id:
                raise CategoryAlreadyExistsException(input_data.name)
        
        # Update category using domain method
        category.update_details(
            name=input_data.name,
            description=input_data.description
        )
        
        # Save changes
        updated_category = self.category_repository.save(category)
        
        return UpdateCategoryOutputData(
            success=True,
            category_id=updated_category.id,
            category_name=updated_category.name,
            message=f"Category '{updated_category.name}' updated successfully"
        )
    
    def _validate_input(self, input_data: UpdateCategoryInputData) -> None:
        """
        Validate input data.
        
        Args:
            input_data: Input data to validate
            
        Raises:
            ValidationException: If validation fails
        """
        if input_data.category_id <= 0:
            raise ValidationException("Invalid category ID")
        
        if not input_data.name or len(input_data.name.strip()) < 3:
            raise ValidationException("Category name must be at least 3 characters")
        
        if len(input_data.name) > 100:
            raise ValidationException("Category name must not exceed 100 characters")
