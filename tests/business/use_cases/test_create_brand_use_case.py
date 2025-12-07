"""
Test suite for CreateBrandUseCase

Test Coverage:
- Success cases: Create brand with valid data
- Validation cases: Invalid name (empty, too short, too long)
- Duplicate cases: Brand name already exists
- Repository exception cases
- Output structure validation
"""

import pytest
from unittest.mock import Mock

from app.business.use_cases.create_brand_use_case import (
    CreateBrandUseCase,
    CreateBrandInputData,
    CreateBrandOutputData
)
from app.domain.entities.brand import Brand
from app.domain.exceptions import ValidationException, BrandAlreadyExistsException


class TestCreateBrandUseCase:
    """Test cases for CreateBrandUseCase"""
    
    # ============ FIXTURES ============
    
    @pytest.fixture
    def brand_repository(self):
        """Mock brand repository"""
        return Mock()
    
    @pytest.fixture
    def use_case(self, brand_repository):
        """Create use case instance"""
        return CreateBrandUseCase(brand_repository)
    
    # ============ HELPER METHODS ============
    
    def create_mock_brand(self, brand_id, name):
        """Create mock brand"""
        brand = Mock(spec=Brand)
        brand.id = brand_id
        brand.name = name
        return brand
    
    # ============ SUCCESS CASES ============
    
    def test_create_brand_success(self, use_case, brand_repository):
        """Test successfully creating a brand"""
        # Arrange
        saved_brand = self.create_mock_brand(1, "Canon")
        
        brand_repository.find_by_name.side_effect = lambda name: None
        brand_repository.save.return_value = saved_brand
        
        input_data = CreateBrandInputData(
            name="Canon",
            description="Leading camera manufacturer",
            logo_url="/images/brands/canon.png"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.brand_id == 1
        assert output.brand_name == "Canon"
        assert "successfully" in output.message.lower()
        
        # Verify repository calls
        brand_repository.find_by_name.assert_called_once_with("Canon")
        brand_repository.save.assert_called_once()
    
    def test_create_brand_with_minimal_data(self, use_case, brand_repository):
        """Test creating brand with minimal required fields"""
        # Arrange
        saved_brand = self.create_mock_brand(2, "Sony")
        
        brand_repository.find_by_name.side_effect = lambda name: None
        brand_repository.save.return_value = saved_brand
        
        input_data = CreateBrandInputData(name="Sony")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.brand_id == 2
    
    def test_create_brand_with_description_only(self, use_case, brand_repository):
        """Test creating brand with name and description"""
        # Arrange
        saved_brand = self.create_mock_brand(3, "Nikon")
        
        brand_repository.find_by_name.side_effect = lambda name: None
        brand_repository.save.return_value = saved_brand
        
        input_data = CreateBrandInputData(
            name="Nikon",
            description="Optical excellence"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
    
    def test_create_brand_with_logo_url(self, use_case, brand_repository):
        """Test creating brand with logo URL"""
        # Arrange
        saved_brand = self.create_mock_brand(4, "Fujifilm")
        
        brand_repository.find_by_name.side_effect = lambda name: None
        brand_repository.save.return_value = saved_brand
        
        input_data = CreateBrandInputData(
            name="Fujifilm",
            logo_url="/images/brands/fuji.png"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
    
    # ============ VALIDATION CASES - NAME ============
    
    def test_create_brand_with_empty_name_fails(self, use_case, brand_repository):
        """Test creating brand with empty name"""
        # Arrange
        input_data = CreateBrandInputData(name="")
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            use_case.execute(input_data)
        
        assert "name" in str(exc_info.value).lower()
        assert "2 characters" in str(exc_info.value).lower()
        brand_repository.save.assert_not_called()
    
    def test_create_brand_with_single_character_name_fails(self, use_case, brand_repository):
        """Test creating brand with name too short"""
        # Arrange
        input_data = CreateBrandInputData(name="A")
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            use_case.execute(input_data)
        
        assert "name" in str(exc_info.value).lower()
        assert "2 characters" in str(exc_info.value).lower()
        brand_repository.save.assert_not_called()
    
    def test_create_brand_with_whitespace_only_name_fails(self, use_case, brand_repository):
        """Test creating brand with whitespace-only name"""
        # Arrange
        input_data = CreateBrandInputData(name="   ")
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            use_case.execute(input_data)
        
        assert "name" in str(exc_info.value).lower()
        brand_repository.save.assert_not_called()
    
    def test_create_brand_with_name_too_long_fails(self, use_case, brand_repository):
        """Test creating brand with name exceeding max length"""
        # Arrange
        long_name = "A" * 101  # 101 characters
        input_data = CreateBrandInputData(name=long_name)
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            use_case.execute(input_data)
        
        assert "100 characters" in str(exc_info.value).lower()
        brand_repository.save.assert_not_called()
    
    def test_create_brand_with_exactly_100_characters_success(self, use_case, brand_repository):
        """Test creating brand with exactly 100 character name (boundary)"""
        # Arrange
        exact_name = "A" * 100  # Exactly 100 characters
        saved_brand = self.create_mock_brand(5, exact_name)
        
        brand_repository.find_by_name.side_effect = lambda name: None
        brand_repository.save.return_value = saved_brand
        
        input_data = CreateBrandInputData(name=exact_name)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
    
    # ============ DUPLICATE CASES ============
    
    def test_create_brand_with_duplicate_name_fails(self, use_case, brand_repository):
        """Test creating brand with duplicate name"""
        # Arrange
        existing_brand = self.create_mock_brand(10, "Canon")
        
        brand_repository.find_by_name.side_effect = lambda name: existing_brand if name == "Canon" else None
        
        input_data = CreateBrandInputData(name="Canon")
        
        # Act & Assert
        with pytest.raises(BrandAlreadyExistsException) as exc_info:
            use_case.execute(input_data)
        
        assert "Canon" in str(exc_info.value)
        assert "already exists" in str(exc_info.value).lower()
        brand_repository.save.assert_not_called()
    
    def test_create_brand_case_sensitive_duplicate_check(self, use_case, brand_repository):
        """Test that duplicate check is case-sensitive at repository level"""
        # Arrange
        saved_brand = self.create_mock_brand(6, "canon")
        
        # Repository returns None for "canon" (case-sensitive check)
        brand_repository.find_by_name.side_effect = lambda name: None
        brand_repository.save.return_value = saved_brand
        
        input_data = CreateBrandInputData(name="canon")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        brand_repository.find_by_name.assert_called_once_with("canon")
    
    # ============ REPOSITORY EXCEPTION CASES ============
    
    def test_repository_exception_find_by_name(self, use_case, brand_repository):
        """Test repository exception during find_by_name"""
        # Arrange
        brand_repository.find_by_name.side_effect = Exception("Database connection error")
        
        input_data = CreateBrandInputData(name="Canon")
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            use_case.execute(input_data)
        
        assert "Database connection error" in str(exc_info.value)
    
    def test_repository_exception_save(self, use_case, brand_repository):
        """Test repository exception during save"""
        # Arrange
        brand_repository.find_by_name.side_effect = lambda name: None
        brand_repository.save.side_effect = Exception("Database save error")
        
        input_data = CreateBrandInputData(name="Canon")
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            use_case.execute(input_data)
        
        assert "Database save error" in str(exc_info.value)
    
    # ============ OUTPUT STRUCTURE VALIDATION ============
    
    def test_output_data_structure(self, use_case, brand_repository):
        """Test output data structure"""
        # Arrange
        saved_brand = self.create_mock_brand(1, "Canon")
        
        brand_repository.find_by_name.side_effect = lambda name: None
        brand_repository.save.return_value = saved_brand
        
        input_data = CreateBrandInputData(name="Canon")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert hasattr(output, 'success')
        assert hasattr(output, 'brand_id')
        assert hasattr(output, 'brand_name')
        assert hasattr(output, 'message')
        
        assert isinstance(output.success, bool)
        assert isinstance(output.brand_id, int)
        assert isinstance(output.brand_name, str)
        assert isinstance(output.message, str)
