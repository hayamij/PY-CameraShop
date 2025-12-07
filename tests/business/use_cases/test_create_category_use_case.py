"""
Test suite for CreateCategoryUseCase

Test Coverage:
- Success cases: Create category with valid data
- Validation cases: Invalid name (empty, too short, too long)
- Duplicate cases: Category name already exists
- Repository exception cases
- Output structure validation
"""

import pytest
from unittest.mock import Mock

from app.business.use_cases.create_category_use_case import (
    CreateCategoryUseCase,
    CreateCategoryInputData,
    CreateCategoryOutputData
)
from app.domain.entities.category import Category
from app.domain.exceptions import ValidationException, CategoryAlreadyExistsException


class TestCreateCategoryUseCase:
    """Test cases for CreateCategoryUseCase"""
    
    # ============ FIXTURES ============
    
    @pytest.fixture
    def category_repository(self):
        """Mock category repository"""
        return Mock()
    
    @pytest.fixture
    def use_case(self, category_repository):
        """Create use case instance"""
        return CreateCategoryUseCase(category_repository)
    
    # ============ HELPER METHODS ============
    
    def create_mock_category(self, category_id, name):
        """Create mock category"""
        category = Mock(spec=Category)
        category.id = category_id
        category.name = name
        return category
    
    # ============ SUCCESS CASES ============
    
    def test_create_category_success(self, use_case, category_repository):
        """Test successfully creating a category"""
        # Arrange
        saved_category = self.create_mock_category(1, "Cameras")
        
        category_repository.find_by_name.side_effect = lambda name: None
        category_repository.save.return_value = saved_category
        
        input_data = CreateCategoryInputData(
            name="Cameras",
            description="All types of cameras"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.category_id == 1
        assert output.category_name == "Cameras"
        assert "successfully" in output.message.lower()
        
        # Verify repository calls
        category_repository.find_by_name.assert_called_once_with("Cameras")
        category_repository.save.assert_called_once()
    
    def test_create_category_with_minimal_data(self, use_case, category_repository):
        """Test creating category with minimal required fields"""
        # Arrange
        saved_category = self.create_mock_category(2, "Lenses")
        
        category_repository.find_by_name.side_effect = lambda name: None
        category_repository.save.return_value = saved_category
        
        input_data = CreateCategoryInputData(name="Lenses")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.category_id == 2
    
    def test_create_category_with_description(self, use_case, category_repository):
        """Test creating category with description"""
        # Arrange
        saved_category = self.create_mock_category(3, "Accessories")
        
        category_repository.find_by_name.side_effect = lambda name: None
        category_repository.save.return_value = saved_category
        
        input_data = CreateCategoryInputData(
            name="Accessories",
            description="Camera accessories and add-ons"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
    
    def test_create_category_with_exactly_3_characters(self, use_case, category_repository):
        """Test creating category with exactly 3 character name (boundary)"""
        # Arrange
        saved_category = self.create_mock_category(4, "DSL")
        
        category_repository.find_by_name.side_effect = lambda name: None
        category_repository.save.return_value = saved_category
        
        input_data = CreateCategoryInputData(name="DSL")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
    
    # ============ VALIDATION CASES - NAME ============
    
    def test_create_category_with_empty_name_fails(self, use_case, category_repository):
        """Test creating category with empty name"""
        # Arrange
        input_data = CreateCategoryInputData(name="")
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            use_case.execute(input_data)
        
        assert "name" in str(exc_info.value).lower()
        assert "3 characters" in str(exc_info.value).lower()
        category_repository.save.assert_not_called()
    
    def test_create_category_with_short_name_fails(self, use_case, category_repository):
        """Test creating category with name too short"""
        # Arrange
        input_data = CreateCategoryInputData(name="AB")
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            use_case.execute(input_data)
        
        assert "name" in str(exc_info.value).lower()
        assert "3 characters" in str(exc_info.value).lower()
        category_repository.save.assert_not_called()
    
    def test_create_category_with_whitespace_only_name_fails(self, use_case, category_repository):
        """Test creating category with whitespace-only name"""
        # Arrange
        input_data = CreateCategoryInputData(name="   ")
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            use_case.execute(input_data)
        
        assert "name" in str(exc_info.value).lower()
        category_repository.save.assert_not_called()
    
    def test_create_category_with_name_too_long_fails(self, use_case, category_repository):
        """Test creating category with name exceeding max length"""
        # Arrange
        long_name = "A" * 101  # 101 characters
        input_data = CreateCategoryInputData(name=long_name)
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            use_case.execute(input_data)
        
        assert "100 characters" in str(exc_info.value).lower()
        category_repository.save.assert_not_called()
    
    def test_create_category_with_exactly_100_characters_success(self, use_case, category_repository):
        """Test creating category with exactly 100 character name (boundary)"""
        # Arrange
        exact_name = "A" * 100  # Exactly 100 characters
        saved_category = self.create_mock_category(5, exact_name)
        
        category_repository.find_by_name.side_effect = lambda name: None
        category_repository.save.return_value = saved_category
        
        input_data = CreateCategoryInputData(name=exact_name)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
    
    # ============ DUPLICATE CASES ============
    
    def test_create_category_with_duplicate_name_fails(self, use_case, category_repository):
        """Test creating category with duplicate name"""
        # Arrange
        existing_category = self.create_mock_category(10, "Cameras")
        
        category_repository.find_by_name.side_effect = lambda name: existing_category if name == "Cameras" else None
        
        input_data = CreateCategoryInputData(name="Cameras")
        
        # Act & Assert
        with pytest.raises(CategoryAlreadyExistsException) as exc_info:
            use_case.execute(input_data)
        
        assert "Cameras" in str(exc_info.value)
        assert "already exists" in str(exc_info.value).lower()
        category_repository.save.assert_not_called()
    
    def test_create_category_case_sensitive_duplicate_check(self, use_case, category_repository):
        """Test that duplicate check is case-sensitive at repository level"""
        # Arrange
        saved_category = self.create_mock_category(6, "cameras")
        
        # Repository returns None for "cameras" (case-sensitive check)
        category_repository.find_by_name.side_effect = lambda name: None
        category_repository.save.return_value = saved_category
        
        input_data = CreateCategoryInputData(name="cameras")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        category_repository.find_by_name.assert_called_once_with("cameras")
    
    # ============ REPOSITORY EXCEPTION CASES ============
    
    def test_repository_exception_find_by_name(self, use_case, category_repository):
        """Test repository exception during find_by_name"""
        # Arrange
        category_repository.find_by_name.side_effect = Exception("Database connection error")
        
        input_data = CreateCategoryInputData(name="Cameras")
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            use_case.execute(input_data)
        
        assert "Database connection error" in str(exc_info.value)
    
    def test_repository_exception_save(self, use_case, category_repository):
        """Test repository exception during save"""
        # Arrange
        category_repository.find_by_name.side_effect = lambda name: None
        category_repository.save.side_effect = Exception("Database save error")
        
        input_data = CreateCategoryInputData(name="Cameras")
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            use_case.execute(input_data)
        
        assert "Database save error" in str(exc_info.value)
    
    # ============ OUTPUT STRUCTURE VALIDATION ============
    
    def test_output_data_structure(self, use_case, category_repository):
        """Test output data structure"""
        # Arrange
        saved_category = self.create_mock_category(1, "Cameras")
        
        category_repository.find_by_name.side_effect = lambda name: None
        category_repository.save.return_value = saved_category
        
        input_data = CreateCategoryInputData(name="Cameras")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert hasattr(output, 'success')
        assert hasattr(output, 'category_id')
        assert hasattr(output, 'category_name')
        assert hasattr(output, 'message')
        
        assert isinstance(output.success, bool)
        assert isinstance(output.category_id, int)
        assert isinstance(output.category_name, str)
        assert isinstance(output.message, str)
