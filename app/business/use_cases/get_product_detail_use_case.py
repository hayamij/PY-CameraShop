"""
Get Product Detail Use Case - Business Layer
Retrieves detailed information about a single product
"""
from typing import Optional
from dataclasses import dataclass
from ...business.ports import IProductRepository, ICategoryRepository, IBrandRepository
from ...domain.exceptions import ProductNotFoundException


@dataclass
class GetProductDetailInputData:
    """Input data for getting product detail"""
    product_id: int


@dataclass
class GetProductDetailOutputData:
    """Output data for product detail"""
    success: bool
    product_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    stock_quantity: Optional[int] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    brand_id: Optional[int] = None
    brand_name: Optional[str] = None
    image_url: Optional[str] = None
    is_visible: Optional[bool] = None
    is_available: Optional[bool] = None
    error_message: Optional[str] = None


class GetProductDetailUseCase:
    """Use case for getting product detail"""
    
    def __init__(
        self,
        product_repository: IProductRepository,
        category_repository: ICategoryRepository,
        brand_repository: IBrandRepository
    ):
        """
        Initialize use case with repository dependencies
        
        Args:
            product_repository: Repository for product data access
            category_repository: Repository for category data access
            brand_repository: Repository for brand data access
        """
        self.product_repository = product_repository
        self.category_repository = category_repository
        self.brand_repository = brand_repository
    
    def execute(self, input_data: GetProductDetailInputData) -> GetProductDetailOutputData:
        """
        Execute use case to get product detail
        
        Args:
            input_data: Input with product ID
            
        Returns:
            GetProductDetailOutputData with product information
        """
        try:
            # Validate input
            if not input_data.product_id or input_data.product_id < 1:
                return GetProductDetailOutputData(
                    success=False,
                    error_message="Invalid product ID"
                )
            
            # Find product
            product = self.product_repository.find_by_id(input_data.product_id)
            
            if not product:
                raise ProductNotFoundException(product_id=input_data.product_id)
            
            # Get category name
            category_name = None
            if product.category_id:
                category = self.category_repository.find_by_id(product.category_id)
                if category:
                    category_name = category.name
            
            # Get brand name
            brand_name = None
            if product.brand_id:
                brand = self.brand_repository.find_by_id(product.brand_id)
                if brand:
                    brand_name = brand.name
            
            return GetProductDetailOutputData(
                success=True,
                product_id=product.product_id,
                name=product.name,
                description=product.description,
                price=float(product.price.amount),
                currency=product.price.currency,
                stock_quantity=product.stock_quantity,
                category_id=product.category_id,
                category_name=category_name,
                brand_id=product.brand_id,
                brand_name=brand_name,
                image_url=product.image_url,
                is_visible=product.is_visible,
                is_available=product.is_available_for_purchase()
            )
            
        except ProductNotFoundException as e:
            return GetProductDetailOutputData(
                success=False,
                error_message=e.message
            )
        except Exception as e:
            return GetProductDetailOutputData(
                success=False,
                error_message=f"Error retrieving product: {str(e)}"
            )
