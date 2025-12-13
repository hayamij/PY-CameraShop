"""
Integration tests for CategoryRepositoryAdapter
"""
import pytest
from datetime import datetime
from app.adapters.repositories.category_repository_adapter import CategoryRepositoryAdapter
from app.domain.entities.category import Category
from app.infrastructure.database.models import CategoryModel


class TestCategoryRepositoryAdapter:
    """Test CategoryRepositoryAdapter integration with database"""
    
    def test_save_new_category(self, db_session):
        """Should save new category to database"""
        repo = CategoryRepositoryAdapter(db_session)
        
        category = Category(
            name="DSLR Cameras",
            description="Digital Single-Lens Reflex cameras"
        )
        
        saved_category = repo.save(category)
        
        assert saved_category.id is not None
        assert saved_category.name == "DSLR Cameras"
        assert saved_category.description == "Digital Single-Lens Reflex cameras"
    
    def test_save_existing_category(self, db_session):
        """Should update existing category"""
        repo = CategoryRepositoryAdapter(db_session)
        
        # Create category
        category = Category(name="DSLR Cameras", description="Original description")
        saved_category = repo.save(category)
        category_id = saved_category.id
        
        # Update category
        saved_category.update_details(name="DSLR & Mirrorless", description="Updated description")
        updated_category = repo.save(saved_category)
        
        assert updated_category.id == category_id
        assert updated_category.name == "DSLR & Mirrorless"
        assert updated_category.description == "Updated description"
    
    def test_find_by_id_existing(self, db_session):
        """Should find category by ID"""
        repo = CategoryRepositoryAdapter(db_session)
        
        category = Category(name="DSLR Cameras")
        saved_category = repo.save(category)
        
        found_category = repo.find_by_id(saved_category.id)
        
        assert found_category is not None
        assert found_category.id == saved_category.id
        assert found_category.name == "DSLR Cameras"
    
    def test_find_by_id_nonexistent(self, db_session):
        """Should return None for nonexistent category"""
        repo = CategoryRepositoryAdapter(db_session)
        
        found_category = repo.find_by_id(999)
        
        assert found_category is None
    
    def test_find_by_name_existing(self, db_session):
        """Should find category by name"""
        repo = CategoryRepositoryAdapter(db_session)
        
        category = Category(name="DSLR Cameras")
        repo.save(category)
        
        found_category = repo.find_by_name("DSLR Cameras")
        
        assert found_category is not None
        assert found_category.name == "DSLR Cameras"
    
    def test_find_by_name_nonexistent(self, db_session):
        """Should return None for nonexistent category name"""
        repo = CategoryRepositoryAdapter(db_session)
        
        found_category = repo.find_by_name("NonexistentCategory")
        
        assert found_category is None
    
    def test_find_all(self, db_session):
        """Should find all categories"""
        repo = CategoryRepositoryAdapter(db_session)
        
        category1 = Category(name="DSLR Cameras")
        category2 = Category(name="Mirrorless Cameras")
        category3 = Category(name="Lenses")
        
        repo.save(category1)
        repo.save(category2)
        repo.save(category3)
        
        all_categories = repo.find_all()
        
        assert len(all_categories) >= 3
        category_names = [c.name for c in all_categories]
        assert "DSLR Cameras" in category_names
        assert "Mirrorless Cameras" in category_names
        assert "Lenses" in category_names
    
    def test_delete_category(self, db_session):
        """Should delete category from database"""
        repo = CategoryRepositoryAdapter(db_session)
        
        category = Category(name="DSLR Cameras")
        saved_category = repo.save(category)
        category_id = saved_category.id
        
        repo.delete(category_id)
        
        found_category = repo.find_by_id(category_id)
        assert found_category is None
    
    def test_exists_by_name(self, db_session):
        """Should check if category name exists"""
        repo = CategoryRepositoryAdapter(db_session)
        
        category = Category(name="DSLR Cameras")
        repo.save(category)
        
        assert repo.exists_by_name("DSLR Cameras") is True
        assert repo.exists_by_name("Mirrorless Cameras") is False
    
    def test_category_entity_domain_logic_preserved(self, db_session):
        """Should preserve domain entity behavior after persistence"""
        repo = CategoryRepositoryAdapter(db_session)
        
        category = Category(name="DSLR Cameras", description="Test")
        saved_category = repo.save(category)
        
        # Test domain behavior - update details
        saved_category.update_details(name="Updated Name", description="Updated Desc")
        assert saved_category.name == "Updated Name"
        assert saved_category.description == "Updated Desc"
        
        # Persist changes
        updated_category = repo.save(saved_category)
        assert updated_category.name == "Updated Name"
        
        # Retrieve and verify
        retrieved_category = repo.find_by_id(updated_category.id)
        assert retrieved_category.name == "Updated Name"
        assert retrieved_category.description == "Updated Desc"


class TestCategoryRepositoryAdapterEdgeCases:
    """Test edge cases for CategoryRepositoryAdapter"""
    
    def test_save_category_with_none_description(self, db_session):
        """Should save category with None description"""
        repo = CategoryRepositoryAdapter(db_session)
        
        category = Category(name="DSLR Cameras", description=None)
        saved_category = repo.save(category)
        
        assert saved_category.description is None
    
    def test_save_category_with_empty_description(self, db_session):
        """Should save category with empty description as None"""
        repo = CategoryRepositoryAdapter(db_session)
        
        category = Category(name="DSLR Cameras", description="")
        saved_category = repo.save(category)
        
        assert saved_category.description is None
    
    def test_save_multiple_categories_with_different_names(self, db_session):
        """Should save multiple categories with different names"""
        repo = CategoryRepositoryAdapter(db_session)
        
        categories = [Category(name=f"Category{i}") for i in range(5)]
        saved_categories = [repo.save(c) for c in categories]
        
        assert len(saved_categories) == 5
        assert all(c.id is not None for c in saved_categories)
    
    def test_find_all_empty_database(self, db_session):
        """Should return empty list when no categories exist"""
        repo = CategoryRepositoryAdapter(db_session)
        
        # Clear all categories
        db_session.query(CategoryModel).delete()
        db_session.commit()
        
        all_categories = repo.find_all()
        
        assert all_categories == []
    
    def test_category_name_case_sensitivity(self, db_session):
        """Should handle category names with different cases"""
        repo = CategoryRepositoryAdapter(db_session)
        
        category1 = Category(name="DSLR Cameras")
        category2 = Category(name="dslr cameras")
        
        saved_category1 = repo.save(category1)
        saved_category2 = repo.save(category2)
        
        # Both should be saved as different categories (case-sensitive)
        assert saved_category1.id != saved_category2.id
    
    def test_save_category_with_long_name(self, db_session):
        """Should save category with long name"""
        repo = CategoryRepositoryAdapter(db_session)
        
        long_name = "A" * 200  # Very long category name
        category = Category(name=long_name)
        saved_category = repo.save(category)
        
        assert saved_category.name == long_name
    
    def test_save_category_with_special_characters(self, db_session):
        """Should save category with special characters in name"""
        repo = CategoryRepositoryAdapter(db_session)
        
        category = Category(name="DSLR & Mirrorless (Pro)")
        saved_category = repo.save(category)
        
        assert saved_category.name == "DSLR & Mirrorless (Pro)"
        
        found_category = repo.find_by_name("DSLR & Mirrorless (Pro)")
        assert found_category is not None
