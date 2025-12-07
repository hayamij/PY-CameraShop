"""
Test suite for DeleteCategoryUseCase

Test Coverage:
- Success cases: Delete category with no products
- Validation cases: Invalid category_id
- Not found cases: Category doesn't exist
- Constraint cases: Category has products
- Repository exception cases
"""

import pytest
from unittest.mock import Mock

from app.business.use_cases.delete_category_use_case import (
    DeleteCategoryUseCase,
    DeleteCategoryInputData,
    DeleteCategoryOutputData
)
from app.domain.entities.category import Category
from app.domain.exceptions import ValidationException, CategoryNotFoundException, CategoryHasProductsException


class TestDeleteCategoryUseCase:
    """Test cases for DeleteCategoryUseCase"""
    
    @pytest.fixture
    def category_repository(self):
        return Mock()
    
    @pytest.fixture
    def product_repository(self):
        return Mock()
    
    @pytest.fixture
    def use_case(self, category_repository, product_repository):
        return DeleteCategoryUseCase(category_repository, product_repository)
    
    def create_mock_category(self, category_id, name):
        category = Mock(spec=Category)
        category.id = category_id
        category.name = name
        return category
    
    def test_delete_category_success(self, use_case, category_repository, product_repository):
        category = self.create_mock_category(1, "Old Category")
        category_repository.find_by_id.return_value = category
        product_repository.count_by_category.return_value = 0
        
        output = use_case.execute(DeleteCategoryInputData(1))
        
        assert output.success is True
        assert output.category_id == 1
        category_repository.delete.assert_called_once_with(1)
    
    def test_delete_verifies_no_products(self, use_case, category_repository, product_repository):
        category = self.create_mock_category(2, "Category")
        category_repository.find_by_id.return_value = category
        product_repository.count_by_category.return_value = 0
        
        use_case.execute(DeleteCategoryInputData(2))
        
        product_repository.count_by_category.assert_called_once_with(2)
    
    def test_invalid_category_id_zero(self, use_case, category_repository):
        with pytest.raises(ValidationException):
            use_case.execute(DeleteCategoryInputData(0))
        category_repository.find_by_id.assert_not_called()
    
    def test_invalid_category_id_negative(self, use_case):
        with pytest.raises(ValidationException):
            use_case.execute(DeleteCategoryInputData(-1))
    
    def test_nonexistent_category_fails(self, use_case, category_repository):
        category_repository.find_by_id.return_value = None
        
        with pytest.raises(CategoryNotFoundException):
            use_case.execute(DeleteCategoryInputData(999))
    
    def test_category_with_products_fails(self, use_case, category_repository, product_repository):
        category = self.create_mock_category(1, "Popular Category")
        category_repository.find_by_id.return_value = category
        product_repository.count_by_category.return_value = 5
        
        with pytest.raises(CategoryHasProductsException):
            use_case.execute(DeleteCategoryInputData(1))
        category_repository.delete.assert_not_called()
    
    def test_category_with_one_product_fails(self, use_case, category_repository, product_repository):
        category = self.create_mock_category(2, "Category")
        category_repository.find_by_id.return_value = category
        product_repository.count_by_category.return_value = 1
        
        with pytest.raises(CategoryHasProductsException):
            use_case.execute(DeleteCategoryInputData(2))
    
    def test_repository_exception_find(self, use_case, category_repository):
        category_repository.find_by_id.side_effect = Exception("DB error")
        
        with pytest.raises(Exception):
            use_case.execute(DeleteCategoryInputData(1))
    
    def test_repository_exception_count(self, use_case, category_repository, product_repository):
        category = self.create_mock_category(1, "Category")
        category_repository.find_by_id.return_value = category
        product_repository.count_by_category.side_effect = Exception("DB error")
        
        with pytest.raises(Exception):
            use_case.execute(DeleteCategoryInputData(1))
    
    def test_output_structure(self, use_case, category_repository, product_repository):
        category = self.create_mock_category(1, "Category")
        category_repository.find_by_id.return_value = category
        product_repository.count_by_category.return_value = 0
        
        output = use_case.execute(DeleteCategoryInputData(1))
        
        assert hasattr(output, 'success')
        assert hasattr(output, 'category_id')
        assert hasattr(output, 'message')
        assert isinstance(output.success, bool)
