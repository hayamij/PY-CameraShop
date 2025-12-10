"""
Integration Tests for Product API Routes
Tests theo Clean Architecture principles - adapter layer
"""

import pytest
from flask import Flask


@pytest.fixture
def app():
    """Create test Flask app"""
    from app.infrastructure.factory import create_app
    app = create_app('testing')
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestListProductsEndpoint:
    """Test suite for GET /api/products"""
    
    def test_list_products_default_pagination(self, client):
        """TC1: List products with default pagination"""
        response = client.get('/api/products')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'products' in data
        assert 'total_products' in data
        assert 'current_page' in data
        assert 'has_next' in data
        assert 'has_prev' in data
        assert data['products'] == []
        
    def test_list_products_with_page_parameter(self, client):
        """TC2: List products with specific page"""
        response = client.get('/api/products?page=2&per_page=5')
        assert response.status_code == 200
        data = response.get_json()
        assert data['current_page'] == 2
        assert 'products' in data
        
    def test_list_products_with_category_filter(self, client):
        """TC3: Filter products by category"""
        response = client.get('/api/products?category_id=1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
    def test_list_products_with_brand_filter(self, client):
        """TC4: Filter products by brand"""
        response = client.get('/api/products?brand_id=1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
    def test_list_products_with_search_query(self, client):
        """TC5: Search products by keyword"""
        response = client.get('/api/products?search_query=camera')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
    def test_list_products_with_price_range(self, client):
        """TC6: Filter products by price range"""
        response = client.get('/api/products?min_price=1000&max_price=5000')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
    def test_list_products_with_sort_by_newest(self, client):
        """TC7: Sort products by newest"""
        response = client.get('/api/products?sort_by=newest')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
    def test_list_products_with_sort_by_price_asc(self, client):
        """TC8: Sort products by price ascending"""
        response = client.get('/api/products?sort_by=price_asc')
        assert response.status_code == 200
        
    def test_list_products_with_sort_by_price_desc(self, client):
        """TC9: Sort products by price descending"""
        response = client.get('/api/products?sort_by=price_desc')
        assert response.status_code == 200
        
    def test_list_products_with_combined_filters(self, client):
        """TC10: Filter with multiple parameters"""
        response = client.get(
            '/api/products?category_id=1&brand_id=2&min_price=1000&sort_by=price_asc&page=1'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
    def test_list_products_with_invalid_page(self, client):
        """TC11: Invalid page number"""
        response = client.get('/api/products?page=-1')
        # Should handle gracefully - either return error or default to page 1
        assert response.status_code in [200, 400]
        
    def test_list_products_with_zero_per_page(self, client):
        """TC12: Zero items per page"""
        response = client.get('/api/products?per_page=0')
        # Should handle gracefully
        assert response.status_code in [200, 400]


class TestGetProductDetailEndpoint:
    """Test suite for GET /api/products/<id>"""
    
    def test_get_product_detail_success(self, client):
        """TC1: Get existing product detail"""
        # First, get a product ID from list
        list_response = client.get('/api/products?per_page=1')
        products = list_response.get_json().get('products', [])
        
        if products:
            product_id = products[0]['id']
            response = client.get(f'/api/products/{product_id}')
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'product' in data
            assert data['product']['id'] == product_id
        else:
            pytest.skip("No products available for testing")
            
    def test_get_product_detail_nonexistent(self, client):
        """TC2: Get nonexistent product"""
        response = client.get('/api/products/999999')
        assert response.status_code in [400, 404]
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
        
    def test_get_product_detail_invalid_id(self, client):
        """TC3: Get product with invalid ID format"""
        response = client.get('/api/products/abc')
        assert response.status_code in [400, 404]
        
    def test_get_product_detail_negative_id(self, client):
        """TC4: Get product with negative ID"""
        response = client.get('/api/products/-1')
        assert response.status_code in [400, 404]
        
    def test_get_product_detail_zero_id(self, client):
        """TC5: Get product with ID 0"""
        response = client.get('/api/products/0')
        assert response.status_code in [400, 404]


class TestProductRoutesIntegration:
    """Integration tests for product routes workflow"""
    
    def test_list_then_detail_workflow(self, client):
        """TC1: Complete flow - list products then view detail"""
        # Step 1: List products
        list_response = client.get('/api/products?per_page=3')
        assert list_response.status_code == 200
        products = list_response.get_json().get('products', [])
        
        # Step 2: Get detail of first product
        if products:
            product_id = products[0]['id']
            detail_response = client.get(f'/api/products/{product_id}')
            assert detail_response.status_code == 200
            detail_data = detail_response.get_json()
            assert detail_data['product']['id'] == product_id
        else:
            pytest.skip("No products for workflow test")
            
    def test_search_then_filter_workflow(self, client):
        """TC2: Search then apply additional filters"""
        # Step 1: Search for products
        search_response = client.get('/api/products?search_query=camera')
        assert search_response.status_code == 200
        
        # Step 2: Add price filter to search
        filtered_response = client.get(
            '/api/products?search_query=camera&min_price=1000'
        )
        assert filtered_response.status_code == 200
        
    def test_pagination_navigation(self, client):
        """TC3: Navigate through pages"""
        # Page 1
        page1 = client.get('/api/products?page=1&per_page=5')
        assert page1.status_code == 200
        
        # Page 2
        page2 = client.get('/api/products?page=2&per_page=5')
        assert page2.status_code == 200
        
        # Results should be different (if enough products exist)
        data1 = page1.get_json()
        data2 = page2.get_json()
        
        if len(data1['products']) > 0 and len(data2['products']) > 0:
            # Check that pages have different products
            ids1 = {p['id'] for p in data1['products']}
            ids2 = {p['id'] for p in data2['products']}
            assert ids1 != ids2, "Pages should contain different products"


class TestProductRoutesErrorHandling:
    """Test error handling and edge cases"""
    
    def test_list_products_with_very_large_page(self, client):
        """TC1: Request page far beyond available"""
        response = client.get('/api/products?page=10000')
        assert response.status_code == 200
        data = response.get_json()
        # Should return empty list or redirect to last valid page
        assert 'products' in data
        
    def test_list_products_with_very_large_per_page(self, client):
        """TC2: Request excessive items per page"""
        response = client.get('/api/products?per_page=10000')
        # Should cap at reasonable limit
        assert response.status_code == 200
        
    def test_list_products_with_negative_prices(self, client):
        """TC3: Invalid negative price filters"""
        response = client.get('/api/products?min_price=-100&max_price=-50')
        # Should handle gracefully
        assert response.status_code in [200, 400]
        
    def test_list_products_with_min_greater_than_max(self, client):
        """TC4: Min price > max price"""
        response = client.get('/api/products?min_price=5000&max_price=1000')
        # Should handle gracefully - return empty or error
        assert response.status_code in [200, 400]
        
    def test_list_products_with_invalid_sort_by(self, client):
        """TC5: Invalid sort_by value"""
        response = client.get('/api/products?sort_by=invalid_sort')
        # Should use default sort or return error
        assert response.status_code in [200, 400]
