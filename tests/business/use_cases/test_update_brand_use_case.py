"""
Test suite for UpdateBrandUseCase

Test Coverage:
- Success cases: Update brand with valid data
- Validation cases: Invalid brand_id, name (empty, too short, too long)
- Not found cases: Brand doesn't exist
- Duplicate cases: New name conflicts with another brand
- Keep same name: Update other fields without changing name
- Repository exception cases
- Output structure validation
"""

import pytest
from unittest.mock import Mock

from app.business.use_cases.update_brand_use_case import (
    UpdateBrandUseCase,
    UpdateBrandInputData,
    UpdateBrandOutputData
)
from app.domain.entities.brand import Brand
from app.domain.exceptions import ValidationException, BrandNotFoundException, BrandAlreadyExistsException


class TestUpdateBrandUseCase:
    """Test cases for UpdateBrandUseCase"""
    
    # ============ FIXTURES ============
    
    @pytest.fixture
    def brand_repository(self):
        """Mock brand repository"""
        return Mock()
    
    @pytest.fixture
    def use_case(self, brand_repository):
        """Create use case instance"""
        return UpdateBrandUseCase(brand_repository)
    
    # ============ HELPER METHODS ============
    
    def create_mock_brand(self, brand_id, name, description="", logo_url=""):
        """Create mock brand"""
        brand = Mock(spec=Brand)
        brand.id = brand_id
        brand.name = name
        brand.description = description
        brand.logo_url = logo_url
        brand.update_details = Mock()
        return brand
    
    # ============ SUCCESS CASES ============
    
    def test_update_brand_success(self, use_case, brand_repository):
        """Test successfully updating a brand"""
        # Arrange
        existing_brand = self.create_mock_brand(1, "Canon", "Old description")
        
        brand_repository.find_by_id.side_effect = lambda bid: existing_brand if bid == 1 else None
        brand_repository.find_by_name.side_effect = lambda name: None
        brand_repository.save.return_value = existing_brand
        
        input_data = UpdateBrandInputData(
            brand_id=1,
            name="Canon Inc.",
            description="Updated camera manufacturer",
            logo_url="/images/brands/canon-new.png"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.brand_id == 1
        assert "successfully" in output.message.lower()
        
        existing_brand.update_details.assert_called_once_with(
            name="Canon Inc.",
            description="Updated camera manufacturer",
            logo_url="/images/brands/canon-new.png"
        )
        brand_repository.save.assert_called_once()
    
    def test_update_brand_name_only(self, use_case, brand_repository):
        """Test updating only brand name"""
        # Arrange
        existing_brand = self.create_mock_brand(1, "Sony", "Description")
        
        brand_repository.find_by_id.side_effect = lambda bid: existing_brand if bid == 1 else None
        brand_repository.find_by_name.side_effect = lambda name: None
        brand_repository.save.return_value = existing_brand
        
        input_data = UpdateBrandInputData(
            brand_id=1,
            name="Sony Corporation"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
    
    def test_update_brand_keep_same_name(self, use_case, brand_repository):
        """Test updating brand keeping the same name"""
        # Arrange
        existing_brand = self.create_mock_brand(1, "Canon", "Old description")
        
        brand_repository.find_by_id.side_effect = lambda bid: existing_brand if bid == 1 else None
        # find_by_name should not be called when name doesn't change
        brand_repository.save.return_value = existing_brand
        
        input_data = UpdateBrandInputData(
            brand_id=1,
            name="Canon",
            description="New description"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        brand_repository.find_by_name.assert_not_called()
    
    def test_update_brand_description_and_logo(self, use_case, brand_repository):
        """Test updating description and logo"""
        # Arrange
        existing_brand = self.create_mock_brand(2, "Nikon")
        
        brand_repository.find_by_id.side_effect = lambda bid: existing_brand if bid == 2 else None
        brand_repository.save.return_value = existing_brand
        
        input_data = UpdateBrandInputData(
            brand_id=2,
            name="Nikon",
            description="Optical excellence since 1917",
            logo_url="/images/nikon-logo.png"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
    
    # ============ VALIDATION CASES - BRAND_ID ============
    
    def test_update_brand_with_invalid_brand_id_zero_fails(self, use_case, brand_repository):
        """Test updating with invalid brand ID (zero)"""
        # Arrange
        input_data = UpdateBrandInputData(
            brand_id=0,
            name="Brand"
        )
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            use_case.execute(input_data)
        
        assert "brand id" in str(exc_info.value).lower()
        brand_repository.find_by_id.assert_not_called()
    
    def test_update_brand_with_negative_brand_id_fails(self, use_case, brand_repository):
        """Test updating with negative brand ID"""
        # Arrange
        input_data = UpdateBrandInputData(
            brand_id=-1,
            name="Brand"
        )
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            use_case.execute(input_data)
        
        assert "brand id" in str(exc_info.value).lower()
        brand_repository.find_by_id.assert_not_called()
    
    # ============ VALIDATION CASES - NAME ============
    
    def test_update_brand_with_empty_name_fails(self, use_case, brand_repository):
        """Test updating with empty name"""
        # Arrange
        input_data = UpdateBrandInputData(
            brand_id=1,
            name=""
        )
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            use_case.execute(input_data)
        
        assert "name" in str(exc_info.value).lower()
        assert "2 characters" in str(exc_info.value).lower()
    
    def test_update_brand_with_short_name_fails(self, use_case, brand_repository):
        """Test updating with name too short"""
        # Arrange
        input_data = UpdateBrandInputData(
            brand_id=1,
            name="A"
        )
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            use_case.execute(input_data)
        
        assert "name" in str(exc_info.value).lower()
        assert "2 characters" in str(exc_info.value).lower()
    
    def test_update_brand_with_name_too_long_fails(self, use_case, brand_repository):
        """Test updating with name exceeding max length"""
        # Arrange
        long_name = "A" * 101
        input_data = UpdateBrandInputData(
            brand_id=1,
            name=long_name
        )
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            use_case.execute(input_data)
        
        assert "100 characters" in str(exc_info.value).lower()
    
    # ============ NOT FOUND CASES ============
    
    def test_update_nonexistent_brand_fails(self, use_case, brand_repository):
        """Test updating non-existent brand"""
        # Arrange
        brand_repository.find_by_id.side_effect = lambda bid: None
        
        input_data = UpdateBrandInputData(
            brand_id=999,
            name="Brand Name"
        )
        
        # Act & Assert
        with pytest.raises(BrandNotFoundException) as exc_info:
            use_case.execute(input_data)
        
        assert "999" in str(exc_info.value)
        brand_repository.save.assert_not_called()
    
    # ============ DUPLICATE CASES ============
    
    def test_update_brand_with_duplicate_name_fails(self, use_case, brand_repository):
        """Test updating brand with name that exists for another brand"""
        # Arrange
        existing_brand = self.create_mock_brand(1, "Canon")
        other_brand = self.create_mock_brand(2, "Sony")
        
        brand_repository.find_by_id.side_effect = lambda bid: existing_brand if bid == 1 else None
        brand_repository.find_by_name.side_effect = lambda name: other_brand if name == "Sony" else None
        
        input_data = UpdateBrandInputData(
            brand_id=1,
            name="Sony"
        )
        
        # Act & Assert
        with pytest.raises(BrandAlreadyExistsException) as exc_info:
            use_case.execute(input_data)
        
        assert "Sony" in str(exc_info.value)
        assert "already exists" in str(exc_info.value).lower()
        brand_repository.save.assert_not_called()
    
    def test_update_brand_same_name_different_case(self, use_case, brand_repository):
        """Test updating to name with different case (if repository is case-sensitive)"""
        # Arrange
        existing_brand = self.create_mock_brand(1, "Canon")
        
        brand_repository.find_by_id.side_effect = lambda bid: existing_brand if bid == 1 else None
        brand_repository.find_by_name.side_effect = lambda name: None  # "CANON" not found
        brand_repository.save.return_value = existing_brand
        
        input_data = UpdateBrandInputData(
            brand_id=1,
            name="CANON"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
    
    # ============ REPOSITORY EXCEPTION CASES ============
    
    def test_repository_exception_find_by_id(self, use_case, brand_repository):
        """Test repository exception during find_by_id"""
        # Arrange
        brand_repository.find_by_id.side_effect = Exception("Database connection error")
        
        input_data = UpdateBrandInputData(
            brand_id=1,
            name="Brand"
        )
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            use_case.execute(input_data)
        
        assert "Database connection error" in str(exc_info.value)
    
    def test_repository_exception_find_by_name(self, use_case, brand_repository):
        """Test repository exception during find_by_name"""
        # Arrange
        existing_brand = self.create_mock_brand(1, "Canon")
        
        brand_repository.find_by_id.side_effect = lambda bid: existing_brand if bid == 1 else None
        brand_repository.find_by_name.side_effect = Exception("Database query error")
        
        input_data = UpdateBrandInputData(
            brand_id=1,
            name="New Name"
        )
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            use_case.execute(input_data)
        
        assert "Database query error" in str(exc_info.value)
    
    def test_repository_exception_save(self, use_case, brand_repository):
        """Test repository exception during save"""
        # Arrange
        existing_brand = self.create_mock_brand(1, "Canon")
        
        brand_repository.find_by_id.side_effect = lambda bid: existing_brand if bid == 1 else None
        brand_repository.find_by_name.side_effect = lambda name: None
        brand_repository.save.side_effect = Exception("Database save error")
        
        input_data = UpdateBrandInputData(
            brand_id=1,
            name="Canon Inc."
        )
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            use_case.execute(input_data)
        
        assert "Database save error" in str(exc_info.value)
    
    # ============ OUTPUT STRUCTURE VALIDATION ============
    
    def test_output_data_structure(self, use_case, brand_repository):
        """Test output data structure"""
        # Arrange
        existing_brand = self.create_mock_brand(1, "Canon")
        
        brand_repository.find_by_id.side_effect = lambda bid: existing_brand if bid == 1 else None
        brand_repository.find_by_name.side_effect = lambda name: None
        brand_repository.save.return_value = existing_brand
        
        input_data = UpdateBrandInputData(
            brand_id=1,
            name="Canon Inc."
        )
        
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
