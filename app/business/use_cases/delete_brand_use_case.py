"""
Use Case: Delete Brand

Business Logic:
- Validates brand exists
- Checks that no products are associated with the brand
- Deletes brand from repository
"""

from dataclasses import dataclass
from app.business.ports.brand_repository import IBrandRepository
from app.business.ports.product_repository import IProductRepository
from app.domain.exceptions import ValidationException, BrandNotFoundException, BrandHasProductsException


@dataclass
class DeleteBrandInputData:
    """Input data for deleting a brand"""
    brand_id: int


@dataclass
class DeleteBrandOutputData:
    """Output data after deleting a brand"""
    success: bool
    brand_id: int
    message: str


class DeleteBrandUseCase:
    """Use case for deleting a brand"""
    
    def __init__(
        self,
        brand_repository: IBrandRepository,
        product_repository: IProductRepository
    ):
        """
        Initialize the use case.
        
        Args:
            brand_repository: Repository for brand persistence
            product_repository: Repository for product queries
        """
        self.brand_repository = brand_repository
        self.product_repository = product_repository
    
    def execute(self, input_data: DeleteBrandInputData) -> DeleteBrandOutputData:
        """
        Execute the delete brand use case.
        
        Args:
            input_data: Input data containing brand ID
            
        Returns:
            DeleteBrandOutputData with operation result
            
        Raises:
            ValidationException: If input validation fails
            BrandNotFoundException: If brand does not exist
            BrandHasProductsException: If brand has associated products
        """
        # Validate input
        if input_data.brand_id <= 0:
            raise ValidationException("Invalid brand ID")
        
        # Get brand
        brand = self.brand_repository.find_by_id(input_data.brand_id)
        if brand is None:
            raise BrandNotFoundException(input_data.brand_id)
        
        # Check if brand has products
        product_count = self.product_repository.count_by_brand(input_data.brand_id)
        if product_count > 0:
            raise BrandHasProductsException(
                brand.name,
                product_count
            )
        
        # Delete brand
        brand_name = brand.name
        self.brand_repository.delete(input_data.brand_id)
        
        return DeleteBrandOutputData(
            success=True,
            brand_id=input_data.brand_id,
            message=f"Brand '{brand_name}' deleted successfully"
        )
