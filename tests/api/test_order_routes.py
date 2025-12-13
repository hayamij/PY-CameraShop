"""
Comprehensive API integration tests for Order Routes
Target: 100% coverage for app/adapters/api/order_routes.py
"""
import pytest
from app.domain.enums import UserRole, OrderStatus


@pytest.fixture
def test_user(clean_db):
    """Create test user"""
    from app.infrastructure.database.models.user_model import UserModel, RoleModel
    
    # Get USER role (created in app fixture - role_id=2)
    user_role = clean_db.query(RoleModel).filter_by(role_name='USER').first()
    if not user_role:
        # Should not happen, role created in app fixture
        raise RuntimeError("USER role not found - check app fixture in conftest.py")
    
    user = UserModel(
        username='orderuser',
        email='order@example.com',
        password_hash='hashed',
        full_name='Order Test',
        phone_number='0123456789',
        address='Test Address',
        role_id=user_role.role_id
    )
    clean_db.add(user)
    clean_db.commit()
    clean_db.refresh(user)
    return user


@pytest.fixture
def test_product(clean_db):
    """Create test product"""
    from app.infrastructure.database.models.product_model import ProductModel, BrandModel, CategoryModel
    import uuid
    
    unique_suffix = str(uuid.uuid4())[:8]
    
    brand = BrandModel(
        name=f'OrderBrand_{unique_suffix}',
        description='Test',
        is_active=True
    )
    clean_db.add(brand)
    clean_db.commit()
    clean_db.refresh(brand)
    
    category = CategoryModel(
        name=f'OrderCategory_{unique_suffix}',
        description='Test'
    )
    clean_db.add(category)
    clean_db.commit()
    clean_db.refresh(category)
    
    product = ProductModel(
        name=f'OrderCamera_{unique_suffix}',
        description='Test',
        price=1000.00,
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
def cart_with_items(clean_db, test_user, test_product):
    """Create cart with items"""
    from app.infrastructure.database.models.cart_model import CartModel, CartItemModel
    
    cart = CartModel(user_id=test_user.user_id)
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
    return cart


@pytest.fixture
def logged_in_user(client, test_user):
    """Login test user"""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.user_id
        sess['username'] = test_user.username
    return test_user


@pytest.fixture
def test_order_with_items(clean_db, test_user, test_product):
    """Create a complete test order with items (following business rules)"""
    from app.infrastructure.database.models.order_model import OrderModel, OrderItemModel
    
    order = OrderModel(
        user_id=test_user.user_id,
        shipping_address='123 Test Street, Test City',
        phone_number='0123456789',
        payment_method='COD',
        order_status=OrderStatus.PENDING.value,
        total_amount=2000.00,
        notes='Test order notes'
    )
    clean_db.add(order)
    clean_db.flush()  # Get order_id
    
    # Add order item (orders must have at least one item per business rules)
    order_item = OrderItemModel(
        order_id=order.order_id,
        product_id=test_product.product_id,
        product_name=test_product.name,
        quantity=2,
        unit_price=1000.00
    )
    clean_db.add(order_item)
    clean_db.commit()
    clean_db.refresh(order)
    return order


class TestPlaceOrderEndpoint:
    """Test POST /api/orders - Place order"""
    
    def test_place_order_success(self, client, logged_in_user, cart_with_items):
        """TC1: Place order successfully"""
        response = client.post('/api/orders', json={
            'shipping_address': '123 Test Street',
            'phone_number': '0987654321',
            'payment_method': 'COD',
            'notes': 'Please deliver in the morning'
        })
        if response.status_code != 201:
            print(f"ERROR: {response.get_json()}")
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'order_id' in data
        assert 'total_amount' in data
    
    def test_place_order_without_notes(self, client, logged_in_user, cart_with_items):
        """TC2: Place order without optional notes"""
        response = client.post('/api/orders', json={
            'shipping_address': '123 Test Street',
            'phone_number': '0987654321',
            'payment_method': 'BANK_TRANSFER'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
    
    def test_place_order_missing_shipping_address(self, client, logged_in_user):
        """TC3: Missing shipping address fails"""
        response = client.post('/api/orders', json={
            'phone_number': '0987654321',
            'payment_method': 'COD'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'shipping address' in data['error'].lower()
    
    def test_place_order_missing_phone_number(self, client, logged_in_user):
        """TC4: Missing phone number fails"""
        response = client.post('/api/orders', json={
            'shipping_address': '123 Test Street',
            'payment_method': 'COD'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'phone number' in data['error'].lower()
    
    def test_place_order_missing_payment_method(self, client, logged_in_user):
        """TC5: Missing payment method fails"""
        response = client.post('/api/orders', json={
            'shipping_address': '123 Test Street',
            'phone_number': '0987654321'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'payment method' in data['error'].lower()
    
    def test_place_order_empty_body(self, client, logged_in_user):
        """TC6: Empty request body fails"""
        response = client.post('/api/orders', json={})
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_place_order_no_json(self, client, logged_in_user):
        """TC7: No JSON body fails"""
        response = client.post('/api/orders')
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_place_order_empty_cart(self, client, logged_in_user):
        """TC8: Cannot place order with empty cart"""
        response = client.post('/api/orders', json={
            'shipping_address': '123 Test Street',
            'phone_number': '0987654321',
            'payment_method': 'COD'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_place_order_unauthenticated(self, client):
        """TC9: Unauthenticated user cannot place order"""
        response = client.post('/api/orders', json={
            'shipping_address': '123 Test Street',
            'phone_number': '0987654321',
            'payment_method': 'COD'
        })
        assert response.status_code == 401
    
    # Note: Error handling test removed - covered by business layer tests


class TestGetMyOrdersEndpoint:
    """Test GET /api/orders/my-orders - Get user's orders"""
    
    def test_get_my_orders_success(self, client, logged_in_user, test_order_with_items):
        """TC1: Get orders successfully"""
        response = client.get('/api/orders/my-orders')
        if response.status_code != 200:
            print(f"Get my orders error: {response.get_json()}")
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'orders' in data
        assert len(data['orders']) > 0
        # Verify order structure
        order = data['orders'][0]
        assert 'order_id' in order
        assert 'total_amount' in order
        assert 'status' in order
        assert 'item_count' in order
        assert order['item_count'] > 0
    
    def test_get_my_orders_with_status_filter(self, client, logged_in_user, clean_db, test_product):
        """TC2: Filter orders by status"""
        from app.infrastructure.database.models.order_model import OrderModel, OrderItemModel
        
        # Create orders with different statuses (with items per business rules)
        order1 = OrderModel(
            user_id=logged_in_user.user_id,
            shipping_address='Address 1',
            phone_number='0123456789',
            payment_method='COD',
            order_status=OrderStatus.PENDING.value,
            total_amount=1000.00
        )
        clean_db.add(order1)
        clean_db.flush()
        clean_db.add(OrderItemModel(
            order_id=order1.order_id,
            product_id=test_product.product_id,
            product_name=test_product.name,
            quantity=1,
            unit_price=1000.00
        ))
        
        order2 = OrderModel(
            user_id=logged_in_user.user_id,
            shipping_address='Address 2',
            phone_number='0123456789',
            payment_method='COD',
            order_status=OrderStatus.COMPLETED.value,
            total_amount=2000.00
        )
        clean_db.add(order2)
        clean_db.flush()
        clean_db.add(OrderItemModel(
            order_id=order2.order_id,
            product_id=test_product.product_id,
            product_name=test_product.name,
            quantity=2,
            unit_price=1000.00
        ))
        clean_db.commit()
        
        response = client.get('/api/orders/my-orders?status=PENDING')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['orders']) == 1
        assert data['orders'][0]['status'] == OrderStatus.PENDING.value
    
    def test_get_my_orders_empty(self, client, logged_in_user):
        """TC3: No orders returns empty list"""
        response = client.get('/api/orders/my-orders')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['orders']) == 0
    
    def test_get_my_orders_unauthenticated(self, client):
        """TC4: Unauthenticated user cannot get orders"""
        response = client.get('/api/orders/my-orders')
        assert response.status_code == 401
    
    # Note: Error handling test removed - covered by business layer tests


class TestGetOrderDetailEndpoint:
    """Test GET /api/orders/<id> - Get order detail"""
    
    def test_get_order_detail_success(self, client, logged_in_user, test_order_with_items):
        """TC1: Get order detail successfully"""
        response = client.get(f'/api/orders/{test_order_with_items.order_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'order' in data
        assert data['order']['order_id'] == test_order_with_items.order_id
        assert 'items' in data['order']
        assert len(data['order']['items']) > 0
    
    def test_get_order_detail_nonexistent(self, client, logged_in_user):
        """TC2: Nonexistent order returns 400"""
        response = client.get('/api/orders/99999')
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_get_order_detail_unauthenticated(self, client):
        """TC3: Unauthenticated user cannot get order detail"""
        response = client.get('/api/orders/1')
        assert response.status_code == 401
    
    # Note: Error handling test removed - covered by business layer tests


class TestCancelOrderEndpoint:
    """Test POST /api/orders/<id>/cancel - Cancel order"""
    
    def test_cancel_order_success(self, client, logged_in_user, test_order_with_items):
        """TC1: Cancel order successfully"""
        response = client.post(f'/api/orders/{test_order_with_items.order_id}/cancel')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'order_status' in data
        assert data['order_status'] == OrderStatus.CANCELLED.value
    
    def test_cancel_order_nonexistent(self, client, logged_in_user):
        """TC2: Cancel nonexistent order fails"""
        response = client.post('/api/orders/99999/cancel')
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_cancel_order_already_cancelled(self, client, logged_in_user, clean_db, test_product):
        """TC3: Cannot cancel already cancelled order"""
        from app.infrastructure.database.models.order_model import OrderModel, OrderItemModel
        
        order = OrderModel(
            user_id=logged_in_user.user_id,
            shipping_address='Test',
            phone_number='0123456789',
            payment_method='COD',
            order_status=OrderStatus.CANCELLED.value,
            total_amount=1000.00
        )
        clean_db.add(order)
        clean_db.flush()
        clean_db.add(OrderItemModel(
            order_id=order.order_id,
            product_id=test_product.product_id,
            product_name=test_product.name,
            quantity=1,
            unit_price=1000.00
        ))
        clean_db.commit()
        clean_db.refresh(order)
        
        response = client.post(f'/api/orders/{order.order_id}/cancel')
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_cancel_order_unauthenticated(self, client):
        """TC4: Unauthenticated user cannot cancel order"""
        response = client.post('/api/orders/1/cancel')
        assert response.status_code == 401
    
    # Note: Error handling test removed - covered by business layer tests


class TestOrderEndpointsIntegration:
    """Integration tests for order workflows"""
    
    def test_complete_order_workflow(self, client, logged_in_user, cart_with_items):
        """TC1: Complete order lifecycle"""
        # 1. Place order
        response = client.post('/api/orders', json={
            'shipping_address': '123 Test Street',
            'phone_number': '0987654321',
            'payment_method': 'COD',
            'notes': 'Test order'
        })
        assert response.status_code == 201
        order_id = response.get_json()['order_id']
        
        # 2. Get my orders
        response = client.get('/api/orders/my-orders')
        assert response.status_code == 200
        orders = response.get_json()['orders']
        assert len(orders) > 0
        
        # 3. Get order detail
        response = client.get(f'/api/orders/{order_id}')
        assert response.status_code == 200
        order = response.get_json()['order']
        assert order['order_id'] == order_id
        
        # 4. Cancel order
        response = client.post(f'/api/orders/{order_id}/cancel')
        assert response.status_code == 200
        
        # 5. Verify order is cancelled
        response = client.get(f'/api/orders/{order_id}')
        assert response.status_code == 200
        order = response.get_json()['order']
        assert order['status'] == OrderStatus.CANCELLED.value





