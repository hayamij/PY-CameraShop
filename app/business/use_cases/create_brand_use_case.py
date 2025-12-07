"""
Use Case: Create Brand

Business Logic:
- Validates brand name (minimum 2 characters)
- Checks for duplicate brand names
- Creates brand entity
- Saves brand to repository
"""

from dataclasses import dataclass
from app.domain.entities.brand import Brand
from app.business.ports.brand_repository import IBrandRepository
from app.domain.exceptions import ValidationException, BrandAlreadyExistsException


@dataclass
class CreateBrandInputData:
    """Input data for creating a brand"""
    name: str
    description: str = ""
    logo_url: str = ""


@dataclass
class CreateBrandOutputData:
    """Output data after creating a brand"""
    success: bool
    brand_id: int
    brand_name: str
    message: str


class CreateBrandUseCase:
    """Use case for creating a new brand"""
    
    def __init__(self, brand_repository: IBrandRepository):
        """
        Initialize the use case.
        
        Args:
            brand_repository: Repository for brand persistence
        """
        self.brand_repository = brand_repository
    
    def execute(self, input_data: CreateBrandInputData) -> CreateBrandOutputData:
        """
        Execute the create brand use case.
        
        Args:
            input_data: Input data containing brand information
            
        Returns:
            CreateBrandOutputData with operation result
            
        Raises:
            ValidationException: If input validation fails
            BrandAlreadyExistsException: If brand name already exists
        """
        # Validate input
        self._validate_input(input_data)
        
        # Check for duplicate name
        existing_brand = self.brand_repository.find_by_name(input_data.name)
        if existing_brand is not None:
            raise BrandAlreadyExistsException(input_data.name)
        
        # Create brand entity
        brand = Brand(
            name=input_data.name,
            description=input_data.description,
            logo_url=input_data.logo_url
        )
        
        # Save brand
        saved_brand = self.brand_repository.save(brand)
        
        return CreateBrandOutputData(
            success=True,
            brand_id=saved_brand.id,
            brand_name=saved_brand.name,
            message=f"Brand '{saved_brand.name}' created successfully"
        )
    
    def _validate_input(self, input_data: CreateBrandInputData) -> None:
        """
        Validate input data.
        
        Args:
            input_data: Input data to validate
            
        Raises:
            ValidationException: If validation fails
        """
        if not input_data.name or len(input_data.name.strip()) < 2:
            raise ValidationException("Brand name must be at least 2 characters")
        
        if len(input_data.name) > 100:
            raise ValidationException("Brand name must not exceed 100 characters")
