"""
Tests for Category domain entity
"""
import pytest
from datetime import datetime
from app.domain.entities.category import Category


class TestCategoryCreation:
    """Test Category entity creation"""
    
    def test_create_valid_category(self):
        """Should create category with valid data"""
        category = Category(
            name="DSLR Cameras",
            description="Digital Single-Lens Reflex cameras"
        )
        
        assert category.name == "DSLR Cameras"
        assert category.description == "Digital Single-Lens Reflex cameras"
        assert category.id is None
    
    def test_create_category_without_description(self):
        """Should create category without description"""
        category = Category(name="DSLR Cameras")
        
        assert category.name == "DSLR Cameras"
        assert category.description is None
    
    def test_create_category_strips_whitespace(self):
        """Should strip whitespace from string fields"""
        category = Category(
            name="  DSLR Cameras  ",
            description="  Digital Single-Lens Reflex cameras  "
        )
        
        assert category.name == "DSLR Cameras"
        assert category.description == "Digital Single-Lens Reflex cameras"
    
    def test_create_category_empty_description_becomes_none(self):
        """Should convert empty description to None"""
        category = Category(name="DSLR Cameras", description="")
        
        assert category.description is None
    
    def test_create_category_invalid_name_too_short(self):
        """Should raise error for name less than 2 characters"""
        with pytest.raises(ValueError, match="Category name must be at least 2 characters"):
            Category(name="A")
    
    def test_create_category_invalid_name_empty(self):
        """Should raise error for empty name"""
        with pytest.raises(ValueError, match="Category name must be at least 2 characters"):
            Category(name="")


class TestCategoryReconstruction:
    """Test Category reconstruction from database"""
    
    def test_reconstruct_category(self):
        """Should reconstruct category from database without validation"""
        created_at = datetime(2023, 1, 1, 12, 0, 0)
        
        category = Category.reconstruct(
            category_id=1,
            name="DSLR Cameras",
            description="Digital Single-Lens Reflex cameras",
            created_at=created_at
        )
        
        assert category.id == 1
        assert category.name == "DSLR Cameras"
        assert category.created_at == created_at


class TestCategoryBehavior:
    """Test Category entity behavior"""
    
    def test_update_category_name(self):
        """Should update category name"""
        category = Category(name="DSLR Cameras")
        category.update_details(name="DSLR & Mirrorless Cameras")
        
        assert category.name == "DSLR & Mirrorless Cameras"
    
    def test_update_category_description(self):
        """Should update category description"""
        category = Category(name="DSLR Cameras", description="Old description")
        category.update_details(description="New description")
        
        assert category.description == "New description"
    
    def test_update_all_category_details(self):
        """Should update all category details at once"""
        category = Category(name="DSLR Cameras")
        category.update_details(
            name="DSLR & Mirrorless Cameras",
            description="Updated description"
        )
        
        assert category.name == "DSLR & Mirrorless Cameras"
        assert category.description == "Updated description"
    
    def test_update_category_invalid_name(self):
        """Should raise error for invalid name"""
        category = Category(name="DSLR Cameras")
        
        with pytest.raises(ValueError, match="Category name must be at least 2 characters"):
            category.update_details(name="A")
    
    def test_update_category_empty_description_becomes_none(self):
        """Should convert empty description to None"""
        category = Category(name="DSLR Cameras", description="Old description")
        category.update_details(description="")
        
        assert category.description is None


class TestCategoryEquality:
    """Test Category equality comparison"""
    
    def test_categories_with_same_id_are_equal(self):
        """Should consider categories with same ID as equal"""
        category1 = Category.reconstruct(
            category_id=1,
            name="DSLR Cameras",
            description="Desc 1",
            created_at=datetime.now()
        )
        
        category2 = Category.reconstruct(
            category_id=1,
            name="Mirrorless Cameras",
            description="Desc 2",
            created_at=datetime.now()
        )
        
        assert category1 == category2
    
    def test_categories_with_different_id_are_not_equal(self):
        """Should consider categories with different IDs as not equal"""
        category1 = Category.reconstruct(
            category_id=1,
            name="DSLR Cameras",
            description=None,
            created_at=datetime.now()
        )
        
        category2 = Category.reconstruct(
            category_id=2,
            name="DSLR Cameras",
            description=None,
            created_at=datetime.now()
        )
        
        assert category1 != category2
