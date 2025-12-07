"""
Delete Product Use Case - Admin deletes product (soft delete)
Clean Architecture - Business Layer
"""
from typing import Optional
from app.business.ports.product_repository import IProductRepository
from app.domain.exceptions import ProductNotFoundException, ValidationException


class DeleteProductInputData:
    """Input data for deleting a product"""
    
    def __init__(self, product_id: int):
        self.product_id = product_id


class DeleteProductOutputData:
    """Output data for product deletion"""
    
    def __init__(
        self,
        success: bool,
        product_id: Optional[int] = None,
        message: Optional[str] = None
    ):
        self.success = success
        self.product_id = product_id
        self.message = message


class DeleteProductUseCase:
    """
    Use case for deleting a product (Admin only)
    Performs soft delete by hiding the product
    """
    
    def __init__(self, product_repository: IProductRepository):
        self.product_repository = product_repository
    
    def execute(self, input_data: DeleteProductInputData) -> DeleteProductOutputData:
        """
        Execute the delete product use case
        
        Args:
            input_data: DeleteProductInputData with product ID
            
        Returns:
            DeleteProductOutputData with deletion result
        """
        try:
            # Step 1: Validate input
            if input_data.product_id <= 0:
                raise ValidationException("ID sản phẩm không hợp lệ")
            
            # Step 2: Get product
            product = self.product_repository.find_by_id(input_data.product_id)
            if not product:
                raise ProductNotFoundException(product_id=input_data.product_id)
            
            # Step 3: Soft delete by hiding product
            product.hide()
            
            # Step 4: Save changes
            self.product_repository.save(product)
            
            return DeleteProductOutputData(
                success=True,
                product_id=product.id,
                message=f"Sản phẩm '{product.name}' đã được xóa thành công"
            )
            
        except (ProductNotFoundException, ValidationException) as e:
            return DeleteProductOutputData(
                success=False,
                message=str(e)
            )
        except Exception as e:
            return DeleteProductOutputData(
                success=False,
                message=f"Lỗi không xác định: {str(e)}"
            )


class ToggleProductVisibilityUseCase:
    """
    Use case for toggling product visibility (Admin only)
    Shows or hides product from customer view
    """
    
    def __init__(self, product_repository: IProductRepository):
        self.product_repository = product_repository
    
    def execute(self, input_data: DeleteProductInputData) -> DeleteProductOutputData:
        """
        Execute the toggle visibility use case
        
        Args:
            input_data: Product ID to toggle
            
        Returns:
            DeleteProductOutputData with toggle result
        """
        try:
            # Step 1: Validate input
            if input_data.product_id <= 0:
                raise ValidationException("ID sản phẩm không hợp lệ")
            
            # Step 2: Get product
            product = self.product_repository.find_by_id(input_data.product_id)
            if not product:
                raise ProductNotFoundException(product_id=input_data.product_id)
            
            # Step 3: Toggle visibility
            if product.is_visible:
                product.hide()
                action = "ẩn"
            else:
                product.show()
                action = "hiện"
            
            # Step 4: Save changes
            self.product_repository.save(product)
            
            return DeleteProductOutputData(
                success=True,
                product_id=product.id,
                message=f"Sản phẩm '{product.name}' đã được {action}"
            )
            
        except (ProductNotFoundException, ValidationException) as e:
            return DeleteProductOutputData(
                success=False,
                message=str(e)
            )
        except Exception as e:
            return DeleteProductOutputData(
                success=False,
                message=f"Lỗi không xác định: {str(e)}"
            )
