"""
Create Product Use Case - Admin creates new product
Clean Architecture - Business Layer
"""
from typing import Optional
from decimal import Decimal
from app.business.ports.product_repository import IProductRepository
from app.business.ports.category_repository import ICategoryRepository
from app.business.ports.brand_repository import IBrandRepository
from app.domain.entities.product import Product
from app.domain.value_objects.money import Money
from app.domain.exceptions import (
    ValidationException,
    CategoryNotFoundException,
    BrandNotFoundException
)


class CreateProductInputData:
    """Input data for creating a product"""
    
    def __init__(
        self,
        name: str,
        description: str,
        price: float,
        stock_quantity: int,
        category_id: int,
        brand_id: int,
        image_url: Optional[str] = None,
        is_visible: bool = True
    ):
        self.name = name
        self.description = description
        self.price = price
        self.stock_quantity = stock_quantity
        self.category_id = category_id
        self.brand_id = brand_id
        self.image_url = image_url
        self.is_visible = is_visible


class CreateProductOutputData:
    """Output data for product creation"""
    
    def __init__(
        self,
        success: bool,
        product_id: Optional[int] = None,
        product_name: Optional[str] = None,
        message: Optional[str] = None
    ):
        self.success = success
        self.product_id = product_id
        self.product_name = product_name
        self.message = message


class CreateProductUseCase:
    """
    Use case for creating a new product (Admin only)
    Validates business rules and creates product entity
    """
    
    def __init__(
        self,
        product_repository: IProductRepository,
        category_repository: ICategoryRepository,
        brand_repository: IBrandRepository
    ):
        self.product_repository = product_repository
        self.category_repository = category_repository
        self.brand_repository = brand_repository
    
    def execute(self, input_data: CreateProductInputData) -> CreateProductOutputData:
        """
        Execute the create product use case
        
        Args:
            input_data: CreateProductInputData with product details
            
        Returns:
            CreateProductOutputData with creation result
        """
        try:
            # Step 1: Validate input
            self._validate_input(input_data)
            
            # Step 2: Verify category exists
            category = self.category_repository.find_by_id(input_data.category_id)
            if not category:
                raise CategoryNotFoundException(input_data.category_id)
            
            # Step 3: Verify brand exists
            brand = self.brand_repository.find_by_id(input_data.brand_id)
            if not brand:
                raise BrandNotFoundException(input_data.brand_id)
            
            # Step 4: Check for duplicate product name
            existing_product = self.product_repository.find_by_name(input_data.name)
            if existing_product:
                raise ValidationException(f"Sản phẩm với tên '{input_data.name}' đã tồn tại")
            
            # Step 5: Create product entity with business logic
            product = Product(
                name=input_data.name,
                description=input_data.description,
                price=Money(Decimal(str(input_data.price)), 'VND'),
                stock_quantity=input_data.stock_quantity,
                category_id=input_data.category_id,
                brand_id=input_data.brand_id,
                image_url=input_data.image_url or '/static/images/default-product.jpg'
            )
            
            # Set visibility if needed (default is True in Product.__init__)
            if not input_data.is_visible:
                product.hide()
            
            # Step 6: Save to repository
            saved_product = self.product_repository.save(product)
            
            return CreateProductOutputData(
                success=True,
                product_id=saved_product.id,
                product_name=saved_product.name,
                message=f"Sản phẩm '{saved_product.name}' đã được tạo thành công"
            )
            
        except (ValidationException, CategoryNotFoundException, BrandNotFoundException) as e:
            return CreateProductOutputData(
                success=False,
                message=str(e)
            )
        except Exception as e:
            return CreateProductOutputData(
                success=False,
                message=f"Lỗi không xác định: {str(e)}"
            )
    
    def _validate_input(self, input_data: CreateProductInputData):
        """Validate input data"""
        if not input_data.name or len(input_data.name.strip()) < 3:
            raise ValidationException("Tên sản phẩm phải có ít nhất 3 ký tự")
        
        if not input_data.description or len(input_data.description.strip()) < 10:
            raise ValidationException("Mô tả sản phẩm phải có ít nhất 10 ký tự")
        
        if input_data.price <= 0:
            raise ValidationException("Giá sản phẩm phải lớn hơn 0")
        
        if input_data.stock_quantity < 0:
            raise ValidationException("Số lượng tồn kho không thể âm")
        
        if input_data.category_id <= 0:
            raise ValidationException("Danh mục không hợp lệ")
        
        if input_data.brand_id <= 0:
            raise ValidationException("Thương hiệu không hợp lệ")
