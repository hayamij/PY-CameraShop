"""
Test suite for DeleteProductUseCase

Test Coverage:
- Success cases: Delete product (soft delete)
- Validation cases: Invalid product ID
- Not found cases: Product doesn't exist
- Already hidden cases: Product already hidden
- Repository exception cases
- Output structure validation
"""

import pytest
from unittest.mock import Mock

from app.business.use_cases.delete_product_use_case import (
    DeleteProductUseCase,
    DeleteProductInputData,
    DeleteProductOutputData
)
from app.domain.entities.product import Product
from app.domain.exceptions import ProductNotFoundException, ValidationException


class TestDeleteProductUseCase:
    """Test cases for DeleteProductUseCase"""
    
    # ============ FIXTURES ============
    
    @pytest.fixture
    def product_repository(self):
        """Mock product repository"""
        return Mock()
    
    @pytest.fixture
    def use_case(self, product_repository):
        """Create use case instance"""
        return DeleteProductUseCase(product_repository)
    
    # ============ HELPER METHODS ============
    
    def create_mock_product(self, product_id, name, is_visible=True):
        """Create mock product"""
        product = Mock(spec=Product)
        product.id = product_id
        product.name = name
        product.is_visible = is_visible
        product.hide = Mock()
        product.show = Mock()
        return product
    
    # ============ SUCCESS CASES ============
    
    def test_delete_product_success(self, use_case, product_repository):
        """Test successfully deleting (hiding) a product"""
        # Arrange
        product = self.create_mock_product(10, "Canon EOS R5", is_visible=True)
        
        product_repository.find_by_id.side_effect = lambda pid: product if pid == 10 else None
        product_repository.save.return_value = product
        
        input_data = DeleteProductInputData(product_id=10)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.product_id == 10
        assert "thành công" in output.message.lower()
        
        # Verify product was hidden
        product.hide.assert_called_once()
        product_repository.save.assert_called_once_with(product)
    
    def test_delete_product_verifies_soft_delete(self, use_case, product_repository):
        """Test that delete is soft delete (hide only)"""
        # Arrange
        product = self.create_mock_product(15, "Sony A7", is_visible=True)
        
        product_repository.find_by_id.side_effect = lambda pid: product if pid == 15 else None
        product_repository.save.return_value = product
        
        input_data = DeleteProductInputData(product_id=15)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        product.hide.assert_called_once()
        # Repository should save (not delete)
        product_repository.save.assert_called_once()
    
    # ============ VALIDATION CASES ============
    
    def test_delete_product_with_invalid_product_id_zero_fails(self, use_case, product_repository):
        """Test deleting with invalid product ID (zero)"""
        # Arrange
        input_data = DeleteProductInputData(product_id=0)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "id" in output.message.lower()
        product_repository.find_by_id.assert_not_called()
    
    def test_delete_product_with_negative_product_id_fails(self, use_case, product_repository):
        """Test deleting with negative product ID"""
        # Arrange
        input_data = DeleteProductInputData(product_id=-1)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "id" in output.message.lower()
        product_repository.find_by_id.assert_not_called()
    
    # ============ NOT FOUND CASES ============
    
    def test_delete_nonexistent_product_fails(self, use_case, product_repository):
        """Test deleting non-existent product"""
        # Arrange
        product_repository.find_by_id.side_effect = lambda pid: None
        
        input_data = DeleteProductInputData(product_id=999)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "not found" in output.message.lower() or "không tìm thấy" in output.message.lower()
        product_repository.save.assert_not_called()
    
    # ============ ALREADY HIDDEN CASES ============
    
    def test_delete_already_hidden_product_raises_exception(self, use_case, product_repository):
        """Test deleting product that is already hidden"""
        # Arrange
        product = self.create_mock_product(10, "Hidden Product", is_visible=False)
        product.hide.side_effect = ValueError("Product is already hidden")
        
        product_repository.find_by_id.side_effect = lambda pid: product if pid == 10 else None
        
        input_data = DeleteProductInputData(product_id=10)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "already hidden" in output.message.lower() or "lỗi" in output.message.lower()
    
    # ============ REPOSITORY EXCEPTION CASES ============
    
    def test_repository_exception_product_find(self, use_case, product_repository):
        """Test repository exception during product find"""
        # Arrange
        product_repository.find_by_id.side_effect = Exception("Database connection error")
        
        input_data = DeleteProductInputData(product_id=10)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "lỗi" in output.message.lower()
    
    def test_repository_exception_product_save(self, use_case, product_repository):
        """Test repository exception during product save"""
        # Arrange
        product = self.create_mock_product(10, "Product", is_visible=True)
        
        product_repository.find_by_id.side_effect = lambda pid: product if pid == 10 else None
        product_repository.save.side_effect = Exception("Database save error")
        
        input_data = DeleteProductInputData(product_id=10)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "lỗi" in output.message.lower()
    
    # ============ OUTPUT STRUCTURE VALIDATION ============
    
    def test_output_data_structure_on_success(self, use_case, product_repository):
        """Test output data structure on success"""
        # Arrange
        product = self.create_mock_product(10, "Canon EOS R5", is_visible=True)
        
        product_repository.find_by_id.side_effect = lambda pid: product if pid == 10 else None
        product_repository.save.return_value = product
        
        input_data = DeleteProductInputData(product_id=10)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert hasattr(output, 'success')
        assert hasattr(output, 'product_id')
        assert hasattr(output, 'message')
        
        assert isinstance(output.success, bool)
        assert isinstance(output.product_id, int)
        assert isinstance(output.message, str)
    
    def test_output_data_structure_on_failure(self, use_case, product_repository):
        """Test output data structure on failure"""
        # Arrange
        input_data = DeleteProductInputData(product_id=0)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert hasattr(output, 'message')
        assert isinstance(output.message, str)
        assert len(output.message) > 0
