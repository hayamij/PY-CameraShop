"""
Test suite for UpdateCategoryUseCase

Test Coverage:
- Success cases: Update category with valid data
- Validation cases: Invalid category_id, name
- Not found cases: Category doesn't exist
- Duplicate cases: New name conflicts
- Repository exception cases
"""

import pytest
from unittest.mock import Mock

from app.business.use_cases.update_category_use_case import (
    UpdateCategoryUseCase,
    UpdateCategoryInputData,
    UpdateCategoryOutputData
)
from app.domain.entities.category import Category
from app.domain.exceptions import ValidationException, CategoryNotFoundException, CategoryAlreadyExistsException


class TestUpdateCategoryUseCase:
    """Test cases for UpdateCategoryUseCase"""
    
    @pytest.fixture
    def category_repository(self):
        return Mock()
    
    @pytest.fixture
    def use_case(self, category_repository):
        return UpdateCategoryUseCase(category_repository)
    
    def create_mock_category(self, category_id, name, description=""):
        category = Mock(spec=Category)
        category.id = category_id
        category.name = name
        category.description = description
        category.update_details = Mock()
        return category
    
    def test_update_category_success(self, use_case, category_repository):
        existing = self.create_mock_category(1, "Cameras", "Old")
        category_repository.find_by_id.side_effect = lambda cid: existing if cid == 1 else None
        category_repository.find_by_name.return_value = None
        category_repository.save.return_value = existing
        
        output = use_case.execute(UpdateCategoryInputData(1, "DSLR Cameras", "Updated"))
        
        assert output.success is True
        assert output.category_id == 1
        existing.update_details.assert_called_once()
    
    def test_update_category_keep_same_name(self, use_case, category_repository):
        existing = self.create_mock_category(1, "Cameras")
        category_repository.find_by_id.return_value = existing
        category_repository.save.return_value = existing
        
        output = use_case.execute(UpdateCategoryInputData(1, "Cameras", "New desc"))
        
        assert output.success is True
        category_repository.find_by_name.assert_not_called()
    
    def test_invalid_category_id_zero(self, use_case):
        with pytest.raises(ValidationException) as exc:
            use_case.execute(UpdateCategoryInputData(0, "Name"))
        assert "category id" in str(exc.value).lower()
    
    def test_invalid_category_id_negative(self, use_case):
        with pytest.raises(ValidationException):
            use_case.execute(UpdateCategoryInputData(-1, "Name"))
    
    def test_empty_name_fails(self, use_case):
        with pytest.raises(ValidationException) as exc:
            use_case.execute(UpdateCategoryInputData(1, ""))
        assert "name" in str(exc.value).lower()
    
    def test_short_name_fails(self, use_case):
        with pytest.raises(ValidationException) as exc:
            use_case.execute(UpdateCategoryInputData(1, "AB"))
        assert "3 characters" in str(exc.value).lower()
    
    def test_long_name_fails(self, use_case):
        with pytest.raises(ValidationException):
            use_case.execute(UpdateCategoryInputData(1, "A" * 101))
    
    def test_nonexistent_category_fails(self, use_case, category_repository):
        category_repository.find_by_id.return_value = None
        
        with pytest.raises(CategoryNotFoundException):
            use_case.execute(UpdateCategoryInputData(999, "Name"))
    
    def test_duplicate_name_fails(self, use_case, category_repository):
        existing = self.create_mock_category(1, "Cameras")
        other = self.create_mock_category(2, "Lenses")
        
        category_repository.find_by_id.return_value = existing
        category_repository.find_by_name.return_value = other
        
        with pytest.raises(CategoryAlreadyExistsException):
            use_case.execute(UpdateCategoryInputData(1, "Lenses"))
    
    def test_repository_exception_find(self, use_case, category_repository):
        category_repository.find_by_id.side_effect = Exception("DB error")
        
        with pytest.raises(Exception):
            use_case.execute(UpdateCategoryInputData(1, "Name"))
    
    def test_output_structure(self, use_case, category_repository):
        existing = self.create_mock_category(1, "Cameras")
        category_repository.find_by_id.return_value = existing
        category_repository.find_by_name.return_value = None
        category_repository.save.return_value = existing
        
        output = use_case.execute(UpdateCategoryInputData(1, "New Name"))
        
        assert hasattr(output, 'success')
        assert hasattr(output, 'category_id')
        assert hasattr(output, 'category_name')
        assert isinstance(output.success, bool)
