"""
Use Case: Update Brand

Business Logic:
- Validates brand exists
- Validates new name and description
- Checks for duplicate brand names (excluding self)
- Updates brand information
- Saves changes to repository
"""

from dataclasses import dataclass
from app.domain.entities.brand import Brand
from app.business.ports.brand_repository import IBrandRepository
from app.domain.exceptions import ValidationException, BrandNotFoundException, BrandAlreadyExistsException


@dataclass
class UpdateBrandInputData:
    """Input data for updating a brand"""
    brand_id: int
    name: str
    description: str = ""
    logo_url: str = ""


@dataclass
class UpdateBrandOutputData:
    """Output data after updating a brand"""
    success: bool
    brand_id: int
    brand_name: str
    message: str


class UpdateBrandUseCase:
    """Use case for updating an existing brand"""
    
    def __init__(self, brand_repository: IBrandRepository):
        """
        Initialize the use case.
        
        Args:
            brand_repository: Repository for brand persistence
        """
        self.brand_repository = brand_repository
    
    def execute(self, input_data: UpdateBrandInputData) -> UpdateBrandOutputData:
        """
        Execute the update brand use case.
        
        Args:
            input_data: Input data containing updated brand information
            
        Returns:
            UpdateBrandOutputData with operation result
            
        Raises:
            ValidationException: If input validation fails
            BrandNotFoundException: If brand does not exist
            BrandAlreadyExistsException: If new name conflicts with existing brand
        """
        # Validate input
        self._validate_input(input_data)
        
        # Get existing brand
        brand = self.brand_repository.find_by_id(input_data.brand_id)
        if brand is None:
            raise BrandNotFoundException(input_data.brand_id)
        
        # Check for duplicate name (excluding self)
        if input_data.name != brand.name:
            existing_brand = self.brand_repository.find_by_name(input_data.name)
            if existing_brand is not None and existing_brand.id != brand.id:
                raise BrandAlreadyExistsException(input_data.name)
        
        # Update brand using domain method
        brand.update_details(
            name=input_data.name,
            description=input_data.description,
            logo_url=input_data.logo_url
        )
        
        # Save changes
        updated_brand = self.brand_repository.save(brand)
        
        return UpdateBrandOutputData(
            success=True,
            brand_id=updated_brand.id,
            brand_name=updated_brand.name,
            message=f"Brand '{updated_brand.name}' updated successfully"
        )
    
    def _validate_input(self, input_data: UpdateBrandInputData) -> None:
        """
        Validate input data.
        
        Args:
            input_data: Input data to validate
            
        Raises:
            ValidationException: If validation fails
        """
        if input_data.brand_id <= 0:
            raise ValidationException("Invalid brand ID")
        
        if not input_data.name or len(input_data.name.strip()) < 2:
            raise ValidationException("Brand name must be at least 2 characters")
        
        if len(input_data.name) > 100:
            raise ValidationException("Brand name must not exceed 100 characters")
