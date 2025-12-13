"""
Integration tests for BrandRepositoryAdapter
"""
import pytest
from datetime import datetime
from app.adapters.repositories.brand_repository_adapter import BrandRepositoryAdapter
from app.domain.entities.brand import Brand
from app.infrastructure.database.models import BrandModel


class TestBrandRepositoryAdapter:
    """Test BrandRepositoryAdapter integration with database"""
    
    def test_save_new_brand(self, db_session):
        """Should save new brand to database"""
        repo = BrandRepositoryAdapter(db_session)
        
        brand = Brand(
            name="Canon",
            description="Leading camera manufacturer",
            logo_url="https://example.com/canon-logo.png"
        )
        
        saved_brand = repo.save(brand)
        
        assert saved_brand.id is not None
        assert saved_brand.name == "Canon"
        assert saved_brand.description == "Leading camera manufacturer"
        assert saved_brand.is_active is True
    
    def test_save_existing_brand(self, db_session):
        """Should update existing brand"""
        repo = BrandRepositoryAdapter(db_session)
        
        # Create brand
        brand = Brand(name="Canon", description="Original description")
        saved_brand = repo.save(brand)
        brand_id = saved_brand.id
        
        # Update brand
        saved_brand.update_details(name="Canon Inc.", description="Updated description")
        updated_brand = repo.save(saved_brand)
        
        assert updated_brand.id == brand_id
        assert updated_brand.name == "Canon Inc."
        assert updated_brand.description == "Updated description"
    
    def test_find_by_id_existing(self, db_session):
        """Should find brand by ID"""
        repo = BrandRepositoryAdapter(db_session)
        
        brand = Brand(name="Canon")
        saved_brand = repo.save(brand)
        
        found_brand = repo.find_by_id(saved_brand.id)
        
        assert found_brand is not None
        assert found_brand.id == saved_brand.id
        assert found_brand.name == "Canon"
    
    def test_find_by_id_nonexistent(self, db_session):
        """Should return None for nonexistent brand"""
        repo = BrandRepositoryAdapter(db_session)
        
        found_brand = repo.find_by_id(999)
        
        assert found_brand is None
    
    def test_find_by_name_existing(self, db_session):
        """Should find brand by name"""
        repo = BrandRepositoryAdapter(db_session)
        
        brand = Brand(name="Canon")
        repo.save(brand)
        
        found_brand = repo.find_by_name("Canon")
        
        assert found_brand is not None
        assert found_brand.name == "Canon"
    
    def test_find_by_name_nonexistent(self, db_session):
        """Should return None for nonexistent brand name"""
        repo = BrandRepositoryAdapter(db_session)
        
        found_brand = repo.find_by_name("NonexistentBrand")
        
        assert found_brand is None
    
    def test_find_all(self, db_session):
        """Should find all brands"""
        repo = BrandRepositoryAdapter(db_session)
        
        brand1 = Brand(name="Canon")
        brand2 = Brand(name="Nikon")
        brand3 = Brand(name="Sony")
        
        repo.save(brand1)
        repo.save(brand2)
        repo.save(brand3)
        
        all_brands = repo.find_all()
        
        assert len(all_brands) >= 3
        brand_names = [b.name for b in all_brands]
        assert "Canon" in brand_names
        assert "Nikon" in brand_names
        assert "Sony" in brand_names
    
    def test_find_all_active(self, db_session):
        """Should find only active brands"""
        repo = BrandRepositoryAdapter(db_session)
        
        brand1 = Brand(name="Canon")
        brand2 = Brand(name="Nikon")
        
        saved_brand1 = repo.save(brand1)
        saved_brand2 = repo.save(brand2)
        
        # Deactivate one brand
        saved_brand1.deactivate()
        repo.save(saved_brand1)
        
        active_brands = repo.find_all(active_only=True)
        
        active_names = [b.name for b in active_brands]
        assert "Nikon" in active_names
        assert "Canon" not in active_names
    
    def test_delete_brand(self, db_session):
        """Should delete brand from database"""
        repo = BrandRepositoryAdapter(db_session)
        
        brand = Brand(name="Canon")
        saved_brand = repo.save(brand)
        brand_id = saved_brand.id
        
        repo.delete(brand_id)
        
        found_brand = repo.find_by_id(brand_id)
        assert found_brand is None
    
    def test_exists_by_name(self, db_session):
        """Should check if brand name exists"""
        repo = BrandRepositoryAdapter(db_session)
        
        brand = Brand(name="Canon")
        repo.save(brand)
        
        assert repo.exists_by_name("Canon") is True
        assert repo.exists_by_name("Nikon") is False
    
    def test_brand_entity_domain_logic_preserved(self, db_session):
        """Should preserve domain entity behavior after persistence"""
        repo = BrandRepositoryAdapter(db_session)
        
        brand = Brand(name="Canon", description="Test")
        saved_brand = repo.save(brand)
        
        # Test domain behavior
        assert saved_brand.is_active is True
        
        saved_brand.deactivate()
        assert saved_brand.is_active is False
        
        # Persist changes
        updated_brand = repo.save(saved_brand)
        assert updated_brand.is_active is False
        
        # Retrieve and verify
        retrieved_brand = repo.find_by_id(updated_brand.id)
        assert retrieved_brand.is_active is False


class TestBrandRepositoryAdapterEdgeCases:
    """Test edge cases for BrandRepositoryAdapter"""
    
    def test_save_brand_with_none_description(self, db_session):
        """Should save brand with None description"""
        repo = BrandRepositoryAdapter(db_session)
        
        brand = Brand(name="Canon", description=None)
        saved_brand = repo.save(brand)
        
        assert saved_brand.description is None
    
    def test_save_brand_with_empty_description(self, db_session):
        """Should save brand with empty description as None"""
        repo = BrandRepositoryAdapter(db_session)
        
        brand = Brand(name="Canon", description="")
        saved_brand = repo.save(brand)
        
        assert saved_brand.description is None
    
    def test_save_multiple_brands_with_different_names(self, db_session):
        """Should save multiple brands with different names"""
        repo = BrandRepositoryAdapter(db_session)
        
        brands = [Brand(name=f"Brand{i}") for i in range(5)]
        saved_brands = [repo.save(b) for b in brands]
        
        assert len(saved_brands) == 5
        assert all(b.id is not None for b in saved_brands)
    
    def test_find_all_empty_database(self, db_session):
        """Should return empty list when no brands exist"""
        repo = BrandRepositoryAdapter(db_session)
        
        # Clear all brands
        db_session.query(BrandModel).delete()
        db_session.commit()
        
        all_brands = repo.find_all()
        
        assert all_brands == []
