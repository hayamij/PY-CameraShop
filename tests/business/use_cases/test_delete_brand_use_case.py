"""
Test suite for DeleteBrandUseCase

Test Coverage:
- Success cases: Delete brand with no products
- Validation cases: Invalid brand_id
- Not found cases: Brand doesn't exist
- Constraint cases: Brand has associated products
- Repository exception cases
- Output structure validation
"""

import pytest
from unittest.mock import Mock

from app.business.use_cases.delete_brand_use_case import (
    DeleteBrandUseCase,
    DeleteBrandInputData,
    DeleteBrandOutputData
)
from app.domain.entities.brand import Brand
from app.domain.exceptions import ValidationException, BrandNotFoundException, BrandHasProductsException


class TestDeleteBrandUseCase:
    """Test cases for DeleteBrandUseCase"""
    
    # ============ FIXTURES ============
    
    @pytest.fixture
    def brand_repository(self):
        """Mock brand repository"""
        return Mock()
    
    @pytest.fixture
    def product_repository(self):
        """Mock product repository"""
        return Mock()
    
    @pytest.fixture
    def use_case(self, brand_repository, product_repository):
        """Create use case instance"""
        return DeleteBrandUseCase(brand_repository, product_repository)
    
    # ============ HELPER METHODS ============
    
    def create_mock_brand(self, brand_id, name):
        """Create mock brand"""
        brand = Mock(spec=Brand)
        brand.id = brand_id
        brand.name = name
        return brand
    
    # ============ SUCCESS CASES ============
    
    def test_delete_brand_success(self, use_case, brand_repository, product_repository):
        """Test successfully deleting a brand"""
        # Arrange
        brand = self.create_mock_brand(1, "Old Brand")
        
        brand_repository.find_by_id.side_effect = lambda bid: brand if bid == 1 else None
        product_repository.count_by_brand.return_value = 0
        brand_repository.delete.return_value = None
        
        input_data = DeleteBrandInputData(brand_id=1)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.brand_id == 1
        assert "successfully" in output.message.lower()
        
        product_repository.count_by_brand.assert_called_once_with(1)
        brand_repository.delete.assert_called_once_with(1)
    
    def test_delete_brand_verifies_no_products(self, use_case, brand_repository, product_repository):
        """Test that delete checks for associated products"""
        # Arrange
        brand = self.create_mock_brand(2, "Brand Name")
        
        brand_repository.find_by_id.side_effect = lambda bid: brand if bid == 2 else None
        product_repository.count_by_brand.return_value = 0
        brand_repository.delete.return_value = None
        
        input_data = DeleteBrandInputData(brand_id=2)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        product_repository.count_by_brand.assert_called_once_with(2)
    
    # ============ VALIDATION CASES ============
    
    def test_delete_brand_with_invalid_brand_id_zero_fails(self, use_case, brand_repository):
        """Test deleting with invalid brand ID (zero)"""
        # Arrange
        input_data = DeleteBrandInputData(brand_id=0)
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            use_case.execute(input_data)
        
        assert "brand id" in str(exc_info.value).lower()
        brand_repository.find_by_id.assert_not_called()
    
    def test_delete_brand_with_negative_brand_id_fails(self, use_case, brand_repository):
        """Test deleting with negative brand ID"""
        # Arrange
        input_data = DeleteBrandInputData(brand_id=-1)
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            use_case.execute(input_data)
        
        assert "brand id" in str(exc_info.value).lower()
        brand_repository.find_by_id.assert_not_called()
    
    # ============ NOT FOUND CASES ============
    
    def test_delete_nonexistent_brand_fails(self, use_case, brand_repository):
        """Test deleting non-existent brand"""
        # Arrange
        brand_repository.find_by_id.side_effect = lambda bid: None
        
        input_data = DeleteBrandInputData(brand_id=999)
        
        # Act & Assert
        with pytest.raises(BrandNotFoundException) as exc_info:
            use_case.execute(input_data)
        
        assert "999" in str(exc_info.value)
        brand_repository.delete.assert_not_called()
    
    # ============ CONSTRAINT CASES ============
    
    def test_delete_brand_with_products_fails(self, use_case, brand_repository, product_repository):
        """Test deleting brand that has associated products"""
        # Arrange
        brand = self.create_mock_brand(1, "Popular Brand")
        
        brand_repository.find_by_id.side_effect = lambda bid: brand if bid == 1 else None
        product_repository.count_by_brand.return_value = 5  # Has 5 products
        
        input_data = DeleteBrandInputData(brand_id=1)
        
        # Act & Assert
        with pytest.raises(BrandHasProductsException) as exc_info:
            use_case.execute(input_data)
        
        assert "Popular Brand" in str(exc_info.value)
        assert "5" in str(exc_info.value)
        brand_repository.delete.assert_not_called()
    
    def test_delete_brand_with_one_product_fails(self, use_case, brand_repository, product_repository):
        """Test deleting brand with exactly one product"""
        # Arrange
        brand = self.create_mock_brand(2, "Brand")
        
        brand_repository.find_by_id.side_effect = lambda bid: brand if bid == 2 else None
        product_repository.count_by_brand.return_value = 1
        
        input_data = DeleteBrandInputData(brand_id=2)
        
        # Act & Assert
        with pytest.raises(BrandHasProductsException):
            use_case.execute(input_data)
        
        brand_repository.delete.assert_not_called()
    
    # ============ REPOSITORY EXCEPTION CASES ============
    
    def test_repository_exception_find_by_id(self, use_case, brand_repository):
        """Test repository exception during find_by_id"""
        # Arrange
        brand_repository.find_by_id.side_effect = Exception("Database connection error")
        
        input_data = DeleteBrandInputData(brand_id=1)
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            use_case.execute(input_data)
        
        assert "Database connection error" in str(exc_info.value)
    
    def test_repository_exception_count_by_brand(self, use_case, brand_repository, product_repository):
        """Test repository exception during count_by_brand"""
        # Arrange
        brand = self.create_mock_brand(1, "Brand")
        
        brand_repository.find_by_id.side_effect = lambda bid: brand if bid == 1 else None
        product_repository.count_by_brand.side_effect = Exception("Database query error")
        
        input_data = DeleteBrandInputData(brand_id=1)
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            use_case.execute(input_data)
        
        assert "Database query error" in str(exc_info.value)
    
    def test_repository_exception_delete(self, use_case, brand_repository, product_repository):
        """Test repository exception during delete"""
        # Arrange
        brand = self.create_mock_brand(1, "Brand")
        
        brand_repository.find_by_id.side_effect = lambda bid: brand if bid == 1 else None
        product_repository.count_by_brand.return_value = 0
        brand_repository.delete.side_effect = Exception("Database delete error")
        
        input_data = DeleteBrandInputData(brand_id=1)
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            use_case.execute(input_data)
        
        assert "Database delete error" in str(exc_info.value)
    
    # ============ OUTPUT STRUCTURE VALIDATION ============
    
    def test_output_data_structure(self, use_case, brand_repository, product_repository):
        """Test output data structure"""
        # Arrange
        brand = self.create_mock_brand(1, "Brand")
        
        brand_repository.find_by_id.side_effect = lambda bid: brand if bid == 1 else None
        product_repository.count_by_brand.return_value = 0
        brand_repository.delete.return_value = None
        
        input_data = DeleteBrandInputData(brand_id=1)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert hasattr(output, 'success')
        assert hasattr(output, 'brand_id')
        assert hasattr(output, 'message')
        
        assert isinstance(output.success, bool)
        assert isinstance(output.brand_id, int)
        assert isinstance(output.message, str)
