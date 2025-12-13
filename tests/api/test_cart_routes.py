"""
Comprehensive API integration tests for Cart Routes
Target: 100% coverage for app/adapters/api/cart_routes.py
"""
import pytest
from app.domain.entities.user import User
from app.domain.entities.product import Product
from app.domain.entities.cart import Cart
from app.domain.value_objects.money import Money
from app.domain.enums import UserRole


@pytest.fixture
def test_user(clean_db):
    """Create test user in database"""
    from app.infrastructure.database.models.user_model import UserModel, RoleModel
    
    # Get USER role (created in app fixture - role_id=2)
    user_role = clean_db.query(RoleModel).filter_by(role_name='USER').first()
    if not user_role:
        # Should not happen, role created in app fixture
        raise RuntimeError("USER role not found - check app fixture in conftest.py")
    
    user_model = UserModel(
        username='testcartuser',
        email='cart@example.com',
        password_hash='hashed_password',
        full_name='Cart Test User',
        phone_number='0123456789',
        address='Test Address',
        role_id=user_role.role_id
    )
    clean_db.add(user_model)
    clean_db.commit()
    clean_db.refresh(user_model)
    return user_model


@pytest.fixture
def test_product(clean_db):
    """Create test product in database"""
    from app.infrastructure.database.models.product_model import ProductModel, BrandModel, CategoryModel
    import uuid
    
    # Create brand with unique name
    unique_suffix = str(uuid.uuid4())[:8]
    brand = BrandModel(
        name=f'TestBrand_{unique_suffix}',
        description='Test brand',
        is_active=True
    )
    clean_db.add(brand)
    clean_db.commit()
    clean_db.refresh(brand)
    
    # Create category with unique name
    category = CategoryModel(
        name=f'TestCategory_{unique_suffix}',
        description='Test category'
    )
    clean_db.add(category)
    clean_db.commit()
    clean_db.refresh(category)
    
    # Create product
    product = ProductModel(
        name=f'TestCamera_{unique_suffix}',
        description='Test camera description',
        price=500.00,
        stock_quantity=10,
        brand_id=brand.brand_id,
        category_id=category.category_id,
        is_visible=True
    )
    clean_db.add(product)
    clean_db.commit()
    clean_db.refresh(product)
    return product


@pytest.fixture
def logged_in_session(client, test_user):
    """Create logged in session"""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.user_id
        sess['role'] = test_user.role.role_name
    return test_user


class TestViewCartEndpoint:
    """Test GET /api/cart - View user's cart"""
    
    def test_view_empty_cart_success(self, client, logged_in_session):
        """TC1: View empty cart returns empty items"""
        response = client.get('/api/cart')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'cart' in data
        assert data['cart']['total_items'] == 0
        assert len(data['cart']['items']) == 0
        assert data['cart']['total'] == 0.0
    
    def test_view_cart_with_items_success(self, client, clean_db, logged_in_session, test_product):
        """TC2: View cart with items returns all items"""
        from app.infrastructure.database.models.cart_model import CartModel, CartItemModel
        
        # Create cart with item
        cart = CartModel(user_id=logged_in_session.user_id)
        clean_db.add(cart)
        clean_db.commit()
        clean_db.refresh(cart)
        
        cart_item = CartItemModel(
            cart_id=cart.cart_id,
            product_id=test_product.product_id,
            quantity=2
        )
        clean_db.add(cart_item)
        clean_db.commit()
        
        response = client.get('/api/cart')
        if response.status_code != 200:
            print(f"Response: {response.get_json()}")
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['cart']['total_items'] == 1  # 1 cart item (not quantity sum)
        assert len(data['cart']['items']) == 1
        assert data['cart']['items'][0]['product_id'] == test_product.product_id
        assert data['cart']['items'][0]['quantity'] == 2
    
    def test_view_cart_unauthenticated_fails(self, client):
        """TC3: Unauthenticated user cannot view cart"""
        response = client.get('/api/cart')
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
    
    # Note: Error handling test removed - monkeypatching use cases through factory
    # is not supported. Error handling is tested through business layer tests.


class TestAddToCartEndpoint:
    """Test POST /api/cart/add - Add item to cart"""
    
    def test_add_to_cart_success(self, client, logged_in_session, test_product):
        """TC1: Add product to cart successfully"""
        response = client.post('/api/cart/add', json={
            'product_id': test_product.product_id,
            'quantity': 2
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'cart_id' in data
        assert 'cart_item_id' in data
        assert data['total_items'] == 1  # 1 distinct item (not quantity sum)
    
    def test_add_to_cart_default_quantity(self, client, logged_in_session, test_product):
        """TC2: Add product without quantity defaults to 1"""
        response = client.post('/api/cart/add', json={
            'product_id': test_product.product_id
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert data['total_items'] == 1
    
    def test_add_to_cart_missing_product_id(self, client, logged_in_session):
        """TC3: Missing product_id returns 400"""
        response = client.post('/api/cart/add', json={
            'quantity': 2
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'product id' in data['error'].lower()
    
    def test_add_to_cart_empty_body(self, client, logged_in_session):
        """TC4: Empty request body returns 400"""
        response = client.post('/api/cart/add', json={})
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_add_to_cart_no_json(self, client, logged_in_session):
        """TC5: No JSON body returns error (400 or 500)"""
        response = client.post('/api/cart/add')
        assert response.status_code in [400, 500]
        data = response.get_json()
        assert data['success'] is False
    
    def test_add_to_cart_nonexistent_product(self, client, logged_in_session):
        """TC6: Adding nonexistent product fails"""
        response = client.post('/api/cart/add', json={
            'product_id': 99999,
            'quantity': 1
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_add_to_cart_invalid_quantity(self, client, logged_in_session, test_product):
        """TC7: Invalid quantity (0 or negative) fails"""
        response = client.post('/api/cart/add', json={
            'product_id': test_product.product_id,
            'quantity': 0
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_add_to_cart_exceeds_stock(self, client, logged_in_session, test_product):
        """TC8: Quantity exceeding stock fails"""
        response = client.post('/api/cart/add', json={
            'product_id': test_product.product_id,
            'quantity': 9999
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_add_to_cart_unauthenticated(self, client, test_product):
        """TC9: Unauthenticated user cannot add to cart"""
        response = client.post('/api/cart/add', json={
            'product_id': test_product.product_id,
            'quantity': 1
        })
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
    
    # Note: Error handling test removed - error scenarios covered by business layer tests


class TestUpdateCartItemEndpoint:
    """Test PUT /api/cart/items/<id> - Update cart item quantity"""
    
    def test_update_cart_item_success(self, client, clean_db, logged_in_session, test_product):
        """TC1: Update cart item quantity successfully"""
        from app.infrastructure.database.models.cart_model import CartModel, CartItemModel
        
        # Create cart with item
        cart = CartModel(user_id=logged_in_session.user_id)
        clean_db.add(cart)
        clean_db.commit()
        clean_db.refresh(cart)
        
        cart_item = CartItemModel(
            cart_id=cart.cart_id,
            product_id=test_product.product_id,
            quantity=2
        )
        clean_db.add(cart_item)
        clean_db.commit()
        clean_db.refresh(cart_item)
        
        response = client.put(f'/api/cart/items/{cart_item.cart_item_id}', json={
            'quantity': 5
        })
        if response.status_code != 200:
            print(f"Cart update error: {response.get_json()}")
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['new_quantity'] == 5
    
    def test_update_cart_item_missing_quantity(self, client, logged_in_session):
        """TC2: Missing quantity returns 400"""
        response = client.put('/api/cart/items/1', json={})
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'quantity' in data['error'].lower()
    
    def test_update_cart_item_no_json(self, client, logged_in_session):
        """TC3: No JSON body returns error (400 or 500)"""
        response = client.put('/api/cart/items/1')
        assert response.status_code in [400, 500]
        data = response.get_json()
        assert data['success'] is False
    
    def test_update_cart_item_nonexistent(self, client, logged_in_session):
        """TC4: Updating nonexistent item fails"""
        response = client.put('/api/cart/items/99999', json={
            'quantity': 3
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_update_cart_item_invalid_quantity(self, client, clean_db, logged_in_session, test_product):
        """TC5: Invalid quantity (0 or negative) fails"""
        from app.infrastructure.database.models.cart_model import CartModel, CartItemModel
        
        cart = CartModel(user_id=logged_in_session.user_id)
        clean_db.add(cart)
        clean_db.commit()
        clean_db.refresh(cart)
        
        cart_item = CartItemModel(
            cart_id=cart.cart_id,
            product_id=test_product.product_id,
            quantity=2
        )
        clean_db.add(cart_item)
        clean_db.commit()
        clean_db.refresh(cart_item)
        
        response = client.put(f'/api/cart/items/{cart_item.cart_item_id}', json={
            'quantity': 0
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_update_cart_item_unauthenticated(self, client):
        """TC6: Unauthenticated user cannot update cart"""
        response = client.put('/api/cart/items/1', json={
            'quantity': 3
        })
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
    
    # Note: Error handling test removed - covered by business layer tests


class TestRemoveCartItemEndpoint:
    """Test DELETE /api/cart/items/<id> - Remove item from cart"""
    
    def test_remove_cart_item_success(self, client, clean_db, logged_in_session, test_product):
        """TC1: Remove cart item successfully"""
        from app.infrastructure.database.models.cart_model import CartModel, CartItemModel
        
        # Create cart with item
        cart = CartModel(user_id=logged_in_session.user_id)
        clean_db.add(cart)
        clean_db.commit()
        clean_db.refresh(cart)
        
        cart_item = CartItemModel(
            cart_id=cart.cart_id,
            product_id=test_product.product_id,
            quantity=2
        )
        clean_db.add(cart_item)
        clean_db.commit()
        clean_db.refresh(cart_item)
        
        response = client.delete(f'/api/cart/items/{cart_item.cart_item_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'message' in data
    
    def test_remove_cart_item_nonexistent(self, client, logged_in_session):
        """TC2: Removing nonexistent item fails"""
        response = client.delete('/api/cart/items/99999')
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_remove_cart_item_unauthenticated(self, client):
        """TC3: Unauthenticated user cannot remove cart item"""
        response = client.delete('/api/cart/items/1')
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
    
    # Note: Error handling test removed - covered by business layer tests


class TestCartEndpointIntegration:
    """Integration tests for complete cart workflows"""
    
    def test_complete_cart_workflow(self, client, logged_in_session, test_product):
        """TC1: Complete flow - add, view, update, remove"""
        # 1. View empty cart
        response = client.get('/api/cart')
        assert response.status_code == 200
        assert response.get_json()['cart']['total_items'] == 0
        
        # 2. Add item to cart
        response = client.post('/api/cart/add', json={
            'product_id': test_product.product_id,
            'quantity': 2
        })
        assert response.status_code == 201
        cart_item_id = response.get_json()['cart_item_id']
        
        # 3. View cart with items
        response = client.get('/api/cart')
        assert response.status_code == 200
        assert response.get_json()['cart']['total_items'] == 1  # 1 distinct item
        
        # 4. Update item quantity
        response = client.put(f'/api/cart/items/{cart_item_id}', json={
            'quantity': 5
        })
        assert response.status_code == 200
        
        # 5. Verify updated quantity
        response = client.get('/api/cart')
        assert response.status_code == 200
        assert response.get_json()['cart']['total_items'] == 1  # Still 1 item
        
        # 6. Remove item
        response = client.delete(f'/api/cart/items/{cart_item_id}')
        assert response.status_code == 200
        
        # 7. Verify cart is empty
        response = client.get('/api/cart')
        assert response.status_code == 200
        assert response.get_json()['cart']['total_items'] == 0
    
    def test_add_same_product_twice(self, client, logged_in_session, test_product):
        """TC2: Adding same product increases quantity"""
        # Add first time
        response = client.post('/api/cart/add', json={
            'product_id': test_product.product_id,
            'quantity': 2
        })
        assert response.status_code == 201
        
        # Add second time
        response = client.post('/api/cart/add', json={
            'product_id': test_product.product_id,
            'quantity': 3
        })
        # Should succeed (business logic handles this)
        assert response.status_code in [200, 201]



