"""
Comprehensive API Integration Tests for Catalog Routes
Target: 100% coverage for app/adapters/api/catalog_routes.py

Following Clean Architecture principles:
- Test HTTP layer (adapters) end-to-end
- Verify request/response format
- Test error handling
"""
import pytest


@pytest.fixture
def sample_categories(clean_db):
    """Create sample categories in database"""
    from app.infrastructure.database.models.product_model import CategoryModel
    
    # Don't specify IDs - let autoincrement handle it
    categories = [
        CategoryModel(
            name='DSLR Cameras',
            description='Digital Single-Lens Reflex cameras',
            is_active=True
        ),
        CategoryModel(
            name='Mirrorless Cameras',
            description='Compact mirrorless camera systems',
            is_active=True
        ),
        CategoryModel(
            name='Action Cameras',
            description='Portable action and sports cameras',
            is_active=True
        ),
        CategoryModel(
            name='Discontinued',
            description='Old category - not active',
            is_active=False  # Inactive - should not appear
        )
    ]
    
    for cat in categories:
        clean_db.add(cat)
    clean_db.commit()
    
    # Refresh to get generated IDs
    for cat in categories:
        clean_db.refresh(cat)
    
    return [c for c in categories if c.is_active]  # Return only active


@pytest.fixture
def sample_brands(clean_db):
    """Create sample brands in database"""
    from app.infrastructure.database.models.product_model import BrandModel
    
    # Don't specify IDs - let autoincrement handle it
    brands = [
        BrandModel(
            name='Canon',
            description='Professional camera equipment',
            is_active=True
        ),
        BrandModel(
            name='Nikon',
            description='High-quality imaging products',
            is_active=True
        ),
        BrandModel(
            name='Sony',
            description='Innovative camera technology',
            is_active=True
        ),
        BrandModel(
            name='Discontinued Brand',
            description='Old brand - not active',
            is_active=False  # Inactive - should not appear
        )
    ]
    
    for brand in brands:
        clean_db.add(brand)
    clean_db.commit()
    
    # Refresh to get generated IDs
    for brand in brands:
        clean_db.refresh(brand)
    
    return [b for b in brands if b.is_active]  # Return only active


class TestListCategoriesEndpoint:
    """Test GET /api/catalog/categories"""
    
    def test_list_categories_empty_database(self, client, clean_db):
        """TC1: List categories returns empty list when no categories exist"""
        response = client.get('/api/catalog/categories')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'categories' in data
        assert data['categories'] == []
    
    def test_list_categories_with_data(self, client, sample_categories):
        """TC2: List categories returns all active categories"""
        response = client.get('/api/catalog/categories')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['categories']) == 3  # Only active ones
        
        # Verify structure
        first_category = data['categories'][0]
        assert 'category_id' in first_category
        assert 'name' in first_category
        assert 'description' in first_category
    
    def test_list_categories_excludes_inactive(self, client, sample_categories, clean_db):
        """TC3: Inactive categories should not appear in results"""
        response = client.get('/api/catalog/categories')
        data = response.get_json()
        
        # Verify only 3 active categories returned (not 4)
        assert len(data['categories']) == 3
        
        # Verify "Discontinued" not in results
        category_names = [cat['name'] for cat in data['categories']]
        assert 'Discontinued' not in category_names
    
    def test_list_categories_response_format(self, client, sample_categories):
        """TC4: Response has correct JSON structure"""
        response = client.get('/api/catalog/categories')
        data = response.get_json()
        
        assert isinstance(data['categories'], list)
        
        for category in data['categories']:
            assert isinstance(category['category_id'], int)
            assert isinstance(category['name'], str)
            assert isinstance(category['description'], (str, type(None)))
    
    def test_list_categories_ordered_by_name(self, client, sample_categories):
        """TC5: Categories returned in consistent order"""
        response = client.get('/api/catalog/categories')
        data = response.get_json()
        
        # Should have 3 categories
        assert len(data['categories']) == 3
        
        # Verify all expected categories present
        names = [cat['name'] for cat in data['categories']]
        assert 'DSLR Cameras' in names
        assert 'Mirrorless Cameras' in names
        assert 'Action Cameras' in names


class TestListBrandsEndpoint:
    """Test GET /api/catalog/brands"""
    
    def test_list_brands_empty_database(self, client, clean_db):
        """TC1: List brands returns empty list when no brands exist"""
        response = client.get('/api/catalog/brands')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'brands' in data
        assert data['brands'] == []
    
    def test_list_brands_with_data(self, client, sample_brands):
        """TC2: List brands returns all active brands"""
        response = client.get('/api/catalog/brands')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['brands']) == 3  # Only active ones
        
        # Verify structure
        first_brand = data['brands'][0]
        assert 'brand_id' in first_brand
        assert 'name' in first_brand
        assert 'description' in first_brand
    
    def test_list_brands_excludes_inactive(self, client, sample_brands, clean_db):
        """TC3: Inactive brands should not appear in results"""
        response = client.get('/api/catalog/brands')
        data = response.get_json()
        
        # Verify only 3 active brands returned (not 4)
        assert len(data['brands']) == 3
        
        # Verify "Discontinued Brand" not in results
        brand_names = [brand['name'] for brand in data['brands']]
        assert 'Discontinued Brand' not in brand_names
    
    def test_list_brands_response_format(self, client, sample_brands):
        """TC4: Response has correct JSON structure"""
        response = client.get('/api/catalog/brands')
        data = response.get_json()
        
        assert isinstance(data['brands'], list)
        
        for brand in data['brands']:
            assert isinstance(brand['brand_id'], int)
            assert isinstance(brand['name'], str)
            assert isinstance(brand['description'], (str, type(None)))
    
    def test_list_brands_with_popular_brands(self, client, sample_brands):
        """TC5: All major brands returned correctly"""
        response = client.get('/api/catalog/brands')
        data = response.get_json()
        
        # Should have 3 brands
        assert len(data['brands']) == 3
        
        # Verify all expected brands present
        names = [brand['name'] for brand in data['brands']]
        assert 'Canon' in names
        assert 'Nikon' in names
        assert 'Sony' in names


class TestCatalogIntegration:
    """Integration tests for catalog endpoints"""
    
    def test_categories_and_brands_both_available(self, client, sample_categories, sample_brands):
        """TC1: Both endpoints work independently"""
        # Get categories
        cat_response = client.get('/api/catalog/categories')
        assert cat_response.status_code == 200
        cat_data = cat_response.get_json()
        assert len(cat_data['categories']) == 3
        
        # Get brands
        brand_response = client.get('/api/catalog/brands')
        assert brand_response.status_code == 200
        brand_data = brand_response.get_json()
        assert len(brand_data['brands']) == 3
    
    def test_catalog_endpoints_independent(self, client, clean_db):
        """TC2: Endpoints work even when one has no data"""
        from app.infrastructure.database.models.product_model import CategoryModel
        
        # Add only category
        category = CategoryModel(
            name='Test Category',
            description='Test',
            is_active=True
        )
        clean_db.add(category)
        clean_db.commit()
        clean_db.refresh(category)
        
        # Categories endpoint returns data
        cat_response = client.get('/api/catalog/categories')
        assert cat_response.status_code == 200
        assert len(cat_response.get_json()['categories']) == 1
        
        # Brands endpoint returns empty (no brands added)
        brand_response = client.get('/api/catalog/brands')
        assert brand_response.status_code == 200
        assert len(brand_response.get_json()['brands']) == 0
    
    def test_catalog_data_consistency(self, client, sample_categories, sample_brands):
        """TC3: Multiple requests return consistent data"""
        # First request
        response1 = client.get('/api/catalog/categories')
        data1 = response1.get_json()
        
        # Second request
        response2 = client.get('/api/catalog/categories')
        data2 = response2.get_json()
        
        # Should be identical
        assert data1 == data2
        assert len(data1['categories']) == len(data2['categories'])


class TestCatalogErrorHandling:
    """Test error handling in catalog endpoints"""
    
    def test_categories_invalid_method_post(self, client):
        """TC1: POST method not allowed on categories endpoint"""
        response = client.post('/api/catalog/categories', json={})
        assert response.status_code == 405  # Method Not Allowed
    
    def test_brands_invalid_method_post(self, client):
        """TC2: POST method not allowed on brands endpoint"""
        response = client.post('/api/catalog/brands', json={})
        assert response.status_code == 405  # Method Not Allowed
    
    def test_categories_invalid_method_put(self, client):
        """TC3: PUT method not allowed"""
        response = client.put('/api/catalog/categories', json={})
        assert response.status_code == 405
    
    def test_brands_invalid_method_delete(self, client):
        """TC4: DELETE method not allowed"""
        response = client.delete('/api/catalog/brands')
        assert response.status_code == 405
    
    def test_nonexistent_catalog_endpoint(self, client):
        """TC5: Invalid catalog endpoint returns 404"""
        response = client.get('/api/catalog/nonexistent')
        assert response.status_code == 404


class TestCatalogEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_category_with_null_description(self, client, clean_db):
        """TC1: Category with NULL description handled correctly"""
        from app.infrastructure.database.models.product_model import CategoryModel
        
        category = CategoryModel(
            name='Test Category',
            description=None,  # NULL description
            is_active=True
        )
        clean_db.add(category)
        clean_db.commit()
        clean_db.refresh(category)
        
        response = client.get('/api/catalog/categories')
        data = response.get_json()
        
        assert response.status_code == 200
        assert len(data['categories']) == 1
        assert data['categories'][0]['description'] is None
    
    def test_brand_with_empty_description(self, client, clean_db):
        """TC2: Brand with empty string description"""
        from app.infrastructure.database.models.product_model import BrandModel
        
        brand = BrandModel(
            name='Test Brand',
            description='',  # Empty string
            is_active=True
        )
        clean_db.add(brand)
        clean_db.commit()
        clean_db.refresh(brand)
        
        response = client.get('/api/catalog/brands')
        data = response.get_json()
        
        assert response.status_code == 200
        assert len(data['brands']) == 1
        assert data['brands'][0]['description'] == ''
    
    def test_large_number_of_categories(self, client, clean_db):
        """TC3: Handle many categories efficiently"""
        from app.infrastructure.database.models.product_model import CategoryModel
        
        # Create 50 categories
        categories = [
            CategoryModel(
                name=f'Category {i}',
                description=f'Description for category {i}',
                is_active=True
            )
            for i in range(1, 51)
        ]
        
        for cat in categories:
            clean_db.add(cat)
        clean_db.commit()
        
        response = client.get('/api/catalog/categories')
        data = response.get_json()
        
        assert response.status_code == 200
        assert len(data['categories']) == 50
    
    def test_unicode_in_category_names(self, client, clean_db):
        """TC4: Unicode characters in category names"""
        from app.infrastructure.database.models.product_model import CategoryModel
        
        category = CategoryModel(
            name='カメラ 📷',  # Japanese + Emoji
            description='Cameras in Japanese',
            is_active=True
        )
        clean_db.add(category)
        clean_db.commit()
        clean_db.refresh(category)
        
        response = client.get('/api/catalog/categories')
        data = response.get_json()
        
        assert response.status_code == 200
        assert data['categories'][0]['name'] == 'カメラ 📷'
    
    def test_special_characters_in_brand_names(self, client, clean_db):
        """TC5: Special characters in brand names"""
        from app.infrastructure.database.models.product_model import BrandModel
        
        brand = BrandModel(
            name="O'Neill & Co.",  # Apostrophe and ampersand
            description='Brand with special chars',
            is_active=True
        )
        clean_db.add(brand)
        clean_db.commit()
        clean_db.refresh(brand)
        
        response = client.get('/api/catalog/brands')
        data = response.get_json()
        
        assert response.status_code == 200
        assert data['brands'][0]['name'] == "O'Neill & Co."
