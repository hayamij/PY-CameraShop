"""
Tests for Brand domain entity
"""
import pytest
from datetime import datetime
from app.domain.entities.brand import Brand


class TestBrandCreation:
    """Test Brand entity creation"""
    
    def test_create_valid_brand(self):
        """Should create brand with valid data"""
        brand = Brand(
            name="Canon",
            description="Leading camera manufacturer",
            logo_url="https://example.com/canon-logo.png"
        )
        
        assert brand.name == "Canon"
        assert brand.description == "Leading camera manufacturer"
        assert brand.logo_url == "https://example.com/canon-logo.png"
        assert brand.is_active is True
        assert brand.id is None
    
    def test_create_brand_without_description(self):
        """Should create brand without description"""
        brand = Brand(name="Canon")
        
        assert brand.name == "Canon"
        assert brand.description is None
        assert brand.logo_url is None
    
    def test_create_brand_strips_whitespace(self):
        """Should strip whitespace from string fields"""
        brand = Brand(
            name="  Canon  ",
            description="  Leading camera manufacturer  "
        )
        
        assert brand.name == "Canon"
        assert brand.description == "Leading camera manufacturer"
    
    def test_create_brand_empty_description_becomes_none(self):
        """Should convert empty description to None"""
        brand = Brand(name="Canon", description="")
        
        assert brand.description is None
    
    def test_create_brand_invalid_name_too_short(self):
        """Should raise error for name less than 2 characters"""
        with pytest.raises(ValueError, match="Brand name must be at least 2 characters"):
            Brand(name="A")
    
    def test_create_brand_invalid_name_empty(self):
        """Should raise error for empty name"""
        with pytest.raises(ValueError, match="Brand name must be at least 2 characters"):
            Brand(name="")


class TestBrandReconstruction:
    """Test Brand reconstruction from database"""
    
    def test_reconstruct_brand(self):
        """Should reconstruct brand from database without validation"""
        created_at = datetime(2023, 1, 1, 12, 0, 0)
        
        brand = Brand.reconstruct(
            brand_id=1,
            name="Canon",
            description="Leading camera manufacturer",
            logo_url="https://example.com/canon-logo.png",
            is_active=False,
            created_at=created_at
        )
        
        assert brand.id == 1
        assert brand.name == "Canon"
        assert brand.is_active is False
        assert brand.created_at == created_at


class TestBrandBehavior:
    """Test Brand entity behavior"""
    
    def test_update_brand_name(self):
        """Should update brand name"""
        brand = Brand(name="Canon")
        brand.update_details(name="Canon Inc.")
        
        assert brand.name == "Canon Inc."
    
    def test_update_brand_description(self):
        """Should update brand description"""
        brand = Brand(name="Canon", description="Old description")
        brand.update_details(description="New description")
        
        assert brand.description == "New description"
    
    def test_update_brand_logo_url(self):
        """Should update brand logo URL"""
        brand = Brand(name="Canon", logo_url="old-logo.png")
        brand.update_details(logo_url="new-logo.png")
        
        assert brand.logo_url == "new-logo.png"
    
    def test_update_all_brand_details(self):
        """Should update all brand details at once"""
        brand = Brand(name="Canon")
        brand.update_details(
            name="Canon Inc.",
            description="Updated description",
            logo_url="new-logo.png"
        )
        
        assert brand.name == "Canon Inc."
        assert brand.description == "Updated description"
        assert brand.logo_url == "new-logo.png"
    
    def test_update_brand_invalid_name(self):
        """Should raise error for invalid name"""
        brand = Brand(name="Canon")
        
        with pytest.raises(ValueError, match="Brand name must be at least 2 characters"):
            brand.update_details(name="A")
    
    def test_update_brand_empty_description_becomes_none(self):
        """Should convert empty description to None"""
        brand = Brand(name="Canon", description="Old description")
        brand.update_details(description="")
        
        assert brand.description is None
    
    def test_deactivate_brand(self):
        """Should deactivate brand"""
        brand = Brand(name="Canon")
        
        assert brand.is_active is True
        brand.deactivate()
        assert brand.is_active is False
    
    def test_activate_brand(self):
        """Should activate brand"""
        brand = Brand.reconstruct(
            brand_id=1,
            name="Canon",
            description=None,
            logo_url=None,
            is_active=False,
            created_at=datetime.now()
        )
        
        assert brand.is_active is False
        brand.activate()
        assert brand.is_active is True


class TestBrandEquality:
    """Test Brand equality comparison"""
    
    def test_brands_with_same_id_are_equal(self):
        """Should consider brands with same ID as equal"""
        brand1 = Brand.reconstruct(
            brand_id=1,
            name="Canon",
            description="Desc 1",
            logo_url=None,
            is_active=True,
            created_at=datetime.now()
        )
        
        brand2 = Brand.reconstruct(
            brand_id=1,
            name="Nikon",
            description="Desc 2",
            logo_url=None,
            is_active=False,
            created_at=datetime.now()
        )
        
        assert brand1 == brand2
    
    def test_brands_with_different_id_are_not_equal(self):
        """Should consider brands with different IDs as not equal"""
        brand1 = Brand.reconstruct(
            brand_id=1,
            name="Canon",
            description=None,
            logo_url=None,
            is_active=True,
            created_at=datetime.now()
        )
        
        brand2 = Brand.reconstruct(
            brand_id=2,
            name="Canon",
            description=None,
            logo_url=None,
            is_active=True,
            created_at=datetime.now()
        )
        
        assert brand1 != brand2
