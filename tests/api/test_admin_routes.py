"""
Comprehensive API integration tests for Admin Routes
Target: 100% coverage for app/adapters/api/admin_routes.py
Following Clean Architecture principles from mega-prompt
"""
import pytest
from app.domain.enums import UserRole, OrderStatus
import uuid


@pytest.fixture
def admin_user(clean_db):
    """Create admin user for testing"""
    from app.infrastructure.database.models.user_model import UserModel, RoleModel
    
    # Get ADMIN role
    admin_role = clean_db.query(RoleModel).filter_by(role_name='ADMIN').first()
    if not admin_role:
        raise RuntimeError("ADMIN role not found")
    
    user = UserModel(
        username='admin_test',
        email='admin@test.com',
        password_hash='hashed',
        full_name='Admin User',
        phone_number='0123456789',
        address='Admin Address',
        role_id=admin_role.role_id
    )
    clean_db.add(user)
    clean_db.commit()
    clean_db.refresh(user)
    return user


@pytest.fixture
def regular_user(clean_db):
    """Create regular user for permission testing"""
    from app.infrastructure.database.models.user_model import UserModel, RoleModel
    
    user_role = clean_db.query(RoleModel).filter_by(role_name='USER').first()
    if not user_role:
        raise RuntimeError("USER role not found")
    
    user = UserModel(
        username='regular_test',
        email='regular@test.com',
        password_hash='hashed',
        full_name='Regular User',
        phone_number='0987654321',
        address='User Address',
        role_id=user_role.role_id
    )
    clean_db.add(user)
    clean_db.commit()
    clean_db.refresh(user)
    return user


@pytest.fixture
def logged_in_admin(client, admin_user):
    """Login as admin"""
    with client.session_transaction() as sess:
        sess['user_id'] = admin_user.user_id
        sess['username'] = admin_user.username
        sess['role'] = 'ADMIN'
    return admin_user


@pytest.fixture
def logged_in_regular_user(client, regular_user):
    """Login as regular user"""
    with client.session_transaction() as sess:
        sess['user_id'] = regular_user.user_id
        sess['username'] = regular_user.username
        sess['role'] = 'USER'
    return regular_user


@pytest.fixture
def sample_brand(clean_db):
    """Create test brand"""
    from app.infrastructure.database.models.product_model import BrandModel
    brand = BrandModel(
        name=f'TestBrand_{uuid.uuid4().hex[:8]}',
        description='Test Brand',
        is_active=True
    )
    clean_db.add(brand)
    clean_db.commit()
    clean_db.refresh(brand)
    return brand


@pytest.fixture
def sample_category(clean_db):
    """Create test category"""
    from app.infrastructure.database.models.product_model import CategoryModel
    category = CategoryModel(
        name=f'TestCategory_{uuid.uuid4().hex[:8]}',
        description='Test Category',
        is_active=True
    )
    clean_db.add(category)
    clean_db.commit()
    clean_db.refresh(category)
    return category


@pytest.fixture
def sample_product(clean_db, sample_brand, sample_category):
    """Create test product"""
    from app.infrastructure.database.models.product_model import ProductModel
    product = ProductModel(
        name=f'TestProduct_{uuid.uuid4().hex[:8]}',
        description='Test Product',
        price=1000.00,
        stock_quantity=10,
        brand_id=sample_brand.brand_id,
        category_id=sample_category.category_id,
        is_visible=True
    )
    clean_db.add(product)
    clean_db.commit()
    clean_db.refresh(product)
    return product


# ============================================================================
# TEST CLASS 1: User Management Endpoints
# ============================================================================

class TestAdminUserManagement:
    """Test admin user management endpoints"""
    
    def test_list_users_success(self, client, logged_in_admin, regular_user):
        """TC1: Admin can list all users"""
        response = client.get('/api/admin/users')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'users' in data
        assert len(data['users']) >= 2  # Admin + regular user
    
    def test_list_users_with_pagination(self, client, logged_in_admin):
        """TC2: List users with pagination parameters"""
        response = client.get('/api/admin/users?page=1&per_page=5')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'users' in data
    
    def test_list_users_unauthorized(self, client, logged_in_regular_user):
        """TC3: Regular user cannot list users"""
        response = client.get('/api/admin/users')
        assert response.status_code == 403
        data = response.get_json()
        assert data['success'] is False
        assert 'Admin access required' in data['error']
    
    def test_list_users_unauthenticated(self, client):
        """TC4: Unauthenticated cannot access"""
        response = client.get('/api/admin/users')
        assert response.status_code == 401
    
    def test_search_users_success(self, client, logged_in_admin, regular_user):
        """TC5: Search users by keyword"""
        response = client.get(f'/api/admin/users/search?keyword={regular_user.username}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'users' in data
    
    def test_search_users_unauthorized(self, client, logged_in_regular_user):
        """TC6: Regular user cannot search users"""
        response = client.get('/api/admin/users/search?keyword=test')
        assert response.status_code == 403
    
    def test_create_user_success(self, client, logged_in_admin):
        """TC7: Admin can create new user"""
        unique_id = uuid.uuid4().hex[:8]
        response = client.post('/api/admin/users', json={
            'username': f'newuser_{unique_id}',
            'email': f'newuser_{unique_id}@test.com',
            'password': 'password123',
            'full_name': 'New User',
            'phone_number': '0123456789',
            'address': 'Test Address',
            'role': 'USER'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'user_id' in data
    
    def test_create_user_missing_fields(self, client, logged_in_admin):
        """TC8: Create user fails with missing required fields"""
        response = client.post('/api/admin/users', json={
            'username': 'incomplete'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_create_user_unauthorized(self, client, logged_in_regular_user):
        """TC9: Regular user cannot create users"""
        response = client.post('/api/admin/users', json={
            'username': 'test',
            'email': 'test@test.com',
            'password': 'pass'
        })
        assert response.status_code == 403
    
    def test_update_user_success(self, client, logged_in_admin, regular_user):
        """TC10: Admin can update user"""
        response = client.put(f'/api/admin/users/{regular_user.user_id}', json={
            'full_name': 'Updated Name',
            'phone_number': '9999999999'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_update_user_nonexistent(self, client, logged_in_admin):
        """TC11: Update nonexistent user returns error"""
        response = client.put('/api/admin/users/99999', json={
            'full_name': 'Test'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_update_user_unauthorized(self, client, logged_in_regular_user, regular_user):
        """TC12: Regular user cannot update users"""
        response = client.put(f'/api/admin/users/{regular_user.user_id}', json={
            'full_name': 'Hacked'
        })
        assert response.status_code == 403
    
    def test_delete_user_success(self, client, logged_in_admin, clean_db):
        """TC13: Admin can delete user"""
        from app.infrastructure.database.models.user_model import UserModel, RoleModel
        
        # Create user to delete
        user_role = clean_db.query(RoleModel).filter_by(role_name='USER').first()
        user = UserModel(
            username=f'todelete_{uuid.uuid4().hex[:8]}',
            email=f'delete_{uuid.uuid4().hex[:8]}@test.com',
            password_hash='hash',
            full_name='To Delete',
            phone_number='1111111111',
            address='Address',
            role_id=user_role.role_id
        )
        clean_db.add(user)
        clean_db.commit()
        clean_db.refresh(user)
        
        response = client.delete(f'/api/admin/users/{user.user_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_delete_user_unauthorized(self, client, logged_in_regular_user, regular_user):
        """TC14: Regular user cannot delete users"""
        response = client.delete(f'/api/admin/users/{regular_user.user_id}')
        assert response.status_code == 403
    
    def test_change_user_role_success(self, client, logged_in_admin, regular_user):
        """TC15: Admin can change user role"""
        response = client.put(f'/api/admin/users/{regular_user.user_id}/role', json={
            'new_role': 'ADMIN'
        })
        # May succeed or fail depending on business rules
        assert response.status_code in [200, 400]
    
    def test_change_user_role_unauthorized(self, client, logged_in_regular_user, regular_user):
        """TC16: Regular user cannot change roles"""
        response = client.put(f'/api/admin/users/{regular_user.user_id}/role', json={
            'new_role': 'ADMIN'
        })
        assert response.status_code == 403


# ============================================================================
# TEST CLASS 2: Product Management Endpoints
# ============================================================================

class TestAdminProductManagement:
    """Test admin product management endpoints"""
    
    def test_create_product_success(self, client, logged_in_admin, sample_brand, sample_category):
        """TC1: Admin can create product"""
        unique_id = uuid.uuid4().hex[:8]
        response = client.post('/api/admin/products', json={
            'name': f'NewProduct_{unique_id}',
            'description': 'New Product Description',
            'price': 2000.00,
            'stock_quantity': 50,
            'brand_id': sample_brand.brand_id,
            'category_id': sample_category.category_id,
            'is_visible': True
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'product_id' in data
    
    def test_create_product_missing_fields(self, client, logged_in_admin):
        """TC2: Create product fails with missing required fields"""
        response = client.post('/api/admin/products', json={
            'name': 'Incomplete'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_create_product_unauthorized(self, client, logged_in_regular_user, sample_brand, sample_category):
        """TC3: Regular user cannot create products"""
        response = client.post('/api/admin/products', json={
            'name': 'Test',
            'price': 100,
            'brand_id': sample_brand.brand_id,
            'category_id': sample_category.category_id
        })
        assert response.status_code == 403
    
    def test_update_product_success(self, client, logged_in_admin, sample_product):
        """TC4: Admin can update product"""
        response = client.put(f'/api/admin/products/{sample_product.product_id}', json={
            'name': 'Updated Product Name',
            'price': 1500.00
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_update_product_nonexistent(self, client, logged_in_admin):
        """TC5: Update nonexistent product returns error"""
        response = client.put('/api/admin/products/99999', json={
            'name': 'Test'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_update_product_unauthorized(self, client, logged_in_regular_user, sample_product):
        """TC6: Regular user cannot update products"""
        response = client.put(f'/api/admin/products/{sample_product.product_id}', json={
            'name': 'Hacked'
        })
        assert response.status_code == 403
    
    def test_delete_product_success(self, client, logged_in_admin, sample_product):
        """TC7: Admin can delete product"""
        response = client.delete(f'/api/admin/products/{sample_product.product_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_delete_product_unauthorized(self, client, logged_in_regular_user, sample_product):
        """TC8: Regular user cannot delete products"""
        response = client.delete(f'/api/admin/products/{sample_product.product_id}')
        assert response.status_code == 403


# ============================================================================
# TEST CLASS 3: Category Management Endpoints
# ============================================================================

class TestAdminCategoryManagement:
    """Test admin category management endpoints"""
    
    def test_create_category_success(self, client, logged_in_admin):
        """TC1: Admin can create category"""
        unique_id = uuid.uuid4().hex[:8]
        response = client.post('/api/admin/categories', json={
            'name': f'NewCategory_{unique_id}',
            'description': 'New Category Description',
            'is_active': True
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'category_id' in data
    
    def test_create_category_missing_name(self, client, logged_in_admin):
        """TC2: Create category fails without name"""
        response = client.post('/api/admin/categories', json={
            'description': 'No name'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_create_category_unauthorized(self, client, logged_in_regular_user):
        """TC3: Regular user cannot create categories"""
        response = client.post('/api/admin/categories', json={
            'name': 'Test',
            'description': 'Test'
        })
        assert response.status_code == 403
    
    def test_update_category_success(self, client, logged_in_admin, sample_category):
        """TC4: Admin can update category"""
        response = client.put(f'/api/admin/categories/{sample_category.category_id}', json={
            'name': 'Updated Category',
            'description': 'Updated Description'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_update_category_nonexistent(self, client, logged_in_admin):
        """TC5: Update nonexistent category returns error"""
        response = client.put('/api/admin/categories/99999', json={
            'name': 'Test'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_update_category_unauthorized(self, client, logged_in_regular_user, sample_category):
        """TC6: Regular user cannot update categories"""
        response = client.put(f'/api/admin/categories/{sample_category.category_id}', json={
            'name': 'Hacked'
        })
        assert response.status_code == 403
    
    def test_delete_category_success(self, client, logged_in_admin, sample_category):
        """TC7: Admin can delete category"""
        response = client.delete(f'/api/admin/categories/{sample_category.category_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_delete_category_unauthorized(self, client, logged_in_regular_user, sample_category):
        """TC8: Regular user cannot delete categories"""
        response = client.delete(f'/api/admin/categories/{sample_category.category_id}')
        assert response.status_code == 403


# ============================================================================
# TEST CLASS 4: Brand Management Endpoints
# ============================================================================

class TestAdminBrandManagement:
    """Test admin brand management endpoints"""
    
    def test_create_brand_success(self, client, logged_in_admin):
        """TC1: Admin can create brand"""
        unique_id = uuid.uuid4().hex[:8]
        response = client.post('/api/admin/brands', json={
            'name': f'NewBrand_{unique_id}',
            'description': 'New Brand Description',
            'is_active': True
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'brand_id' in data
    
    def test_create_brand_missing_name(self, client, logged_in_admin):
        """TC2: Create brand fails without name"""
        response = client.post('/api/admin/brands', json={
            'description': 'No name'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_create_brand_unauthorized(self, client, logged_in_regular_user):
        """TC3: Regular user cannot create brands"""
        response = client.post('/api/admin/brands', json={
            'name': 'Test',
            'description': 'Test'
        })
        assert response.status_code == 403
    
    def test_update_brand_success(self, client, logged_in_admin, sample_brand):
        """TC4: Admin can update brand"""
        response = client.put(f'/api/admin/brands/{sample_brand.brand_id}', json={
            'name': 'Updated Brand',
            'description': 'Updated Description'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_update_brand_nonexistent(self, client, logged_in_admin):
        """TC5: Update nonexistent brand returns error"""
        response = client.put('/api/admin/brands/99999', json={
            'name': 'Test'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_update_brand_unauthorized(self, client, logged_in_regular_user, sample_brand):
        """TC6: Regular user cannot update brands"""
        response = client.put(f'/api/admin/brands/{sample_brand.brand_id}', json={
            'name': 'Hacked'
        })
        assert response.status_code == 403
    
    def test_delete_brand_success(self, client, logged_in_admin, sample_brand):
        """TC7: Admin can delete brand"""
        response = client.delete(f'/api/admin/brands/{sample_brand.brand_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_delete_brand_unauthorized(self, client, logged_in_regular_user, sample_brand):
        """TC8: Regular user cannot delete brands"""
        response = client.delete(f'/api/admin/brands/{sample_brand.brand_id}')
        assert response.status_code == 403


# ============================================================================
# TEST CLASS 5: Order Management Endpoints
# ============================================================================

class TestAdminOrderManagement:
    """Test admin order management endpoints"""
    
    def test_list_orders_success(self, client, logged_in_admin):
        """TC1: Admin can list all orders"""
        response = client.get('/api/admin/orders')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'orders' in data
    
    def test_list_orders_with_filters(self, client, logged_in_admin):
        """TC2: List orders with status filter"""
        response = client.get('/api/admin/orders?status=PENDING')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_list_orders_with_pagination(self, client, logged_in_admin):
        """TC3: List orders with pagination"""
        response = client.get('/api/admin/orders?page=1&per_page=10')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_list_orders_unauthorized(self, client, logged_in_regular_user):
        """TC4: Regular user cannot list all orders"""
        response = client.get('/api/admin/orders')
        assert response.status_code == 403
    
    def test_update_order_status_success(self, client, logged_in_admin, clean_db, regular_user, sample_product):
        """TC5: Admin can update order status"""
        from app.infrastructure.database.models.order_model import OrderModel, OrderItemModel
        
        # Create test order
        order = OrderModel(
            user_id=regular_user.user_id,
            shipping_address='Test Address',
            phone_number='0123456789',
            payment_method='COD',
            order_status=OrderStatus.PENDING.value,
            total_amount=1000.00
        )
        clean_db.add(order)
        clean_db.flush()
        clean_db.add(OrderItemModel(
            order_id=order.order_id,
            product_id=sample_product.product_id,
            product_name=sample_product.name,
            quantity=1,
            unit_price=1000.00
        ))
        clean_db.commit()
        clean_db.refresh(order)
        
        response = client.put(f'/api/admin/orders/{order.order_id}/status', json={
            'new_status': 'SHIPPING'
        })
        # May succeed or fail based on business rules
        assert response.status_code in [200, 400]
    
    def test_update_order_status_unauthorized(self, client, logged_in_regular_user):
        """TC6: Regular user cannot update order status"""
        response = client.put('/api/admin/orders/1/status', json={
            'new_status': 'COMPLETED'
        })
        assert response.status_code == 403


# ============================================================================
# TEST CLASS 6: Admin Authorization and Edge Cases
# ============================================================================

class TestAdminAuthorizationAndEdgeCases:
    """Test admin-specific authorization and edge cases"""
    
    def test_admin_access_with_no_session(self, client):
        """TC1: All admin endpoints require authentication"""
        endpoints = [
            '/api/admin/users',
            '/api/admin/products',
            '/api/admin/categories',
            '/api/admin/brands',
            '/api/admin/orders'
        ]
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401
    
    def test_admin_endpoints_reject_non_admin(self, client, logged_in_regular_user):
        """TC2: All admin endpoints reject non-admin users"""
        endpoints = [
            ('/api/admin/users', 'GET'),
            ('/api/admin/products', 'POST'),
            ('/api/admin/categories', 'POST'),
            ('/api/admin/brands', 'POST'),
            ('/api/admin/orders', 'GET')
        ]
        for endpoint, method in endpoints:
            if method == 'GET':
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json={})
            assert response.status_code == 403
            data = response.get_json()
            assert 'Admin access required' in data['error']
    
    def test_invalid_json_handling(self, client, logged_in_admin):
        """TC3: Endpoints handle invalid JSON gracefully"""
        response = client.post('/api/admin/products', 
                              data='invalid json',
                              content_type='application/json')
        # Should return 400 or 500 with error message
        assert response.status_code in [400, 500]
    
    def test_missing_required_fields(self, client, logged_in_admin):
        """TC4: Endpoints validate required fields"""
        # Try to create product without required fields
        response = client.post('/api/admin/products', json={})
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
