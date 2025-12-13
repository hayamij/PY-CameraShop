"""
Tests for CreateOrderByAdminUseCase
"""
import pytest
from decimal import Decimal
from app.business.use_cases.create_order_by_admin_use_case import (
    CreateOrderByAdminUseCase,
    CreateOrderByAdminInputData,
    OrderItemInput
)
from app.domain.entities.user import User
from app.domain.entities.product import Product
from app.domain.value_objects import Email, Money


class MockOrderRepository:
    """Mock order repository for testing"""
    def __init__(self):
        self.orders = {}
        self.next_id = 1
    
    def save(self, order):
        order._id = self.next_id
        self.orders[self.next_id] = order
        self.next_id += 1
        return order
    
    def find_by_id(self, order_id):
        return self.orders.get(order_id)


class MockProductRepository:
    """Mock product repository for testing"""
    def __init__(self):
        self.products = {}
    
    def find_by_id(self, product_id):
        return self.products.get(product_id)
    
    def add_product(self, product):
        self.products[product.id] = product


class MockUserRepository:
    """Mock user repository for testing"""
    def __init__(self):
        self.users = {}
    
    def get_by_id(self, user_id):
        return self.users.get(user_id)
    
    def add_user(self, user):
        self.users[user.id] = user


class TestCreateOrderByAdminUseCase:
    """Test CreateOrderByAdminUseCase"""
    
    @pytest.fixture
    def repositories(self):
        """Setup mock repositories"""
        order_repo = MockOrderRepository()
        product_repo = MockProductRepository()
        user_repo = MockUserRepository()
        
        # Add test products
        product1 = Product.reconstruct(
            product_id=1,
            name="Canon EOS 90D",
            description="Professional DSLR",
            price=Money(Decimal("1000000")),
            stock_quantity=10,
            category_id=1,
            brand_id=1,
            image_url=None,
            is_visible=True,
            created_at=None
        )
        product2 = Product.reconstruct(
            product_id=2,
            name="Nikon D850",
            description="Professional DSLR",
            price=Money(Decimal("1500000")),
            stock_quantity=5,
            category_id=1,
            brand_id=2,
            image_url=None,
            is_visible=True,
            created_at=None
        )
        product_repo.add_product(product1)
        product_repo.add_product(product2)
        
        # Add test user
        user = User.reconstruct(
            user_id=1,
            username="customer1",
            email=Email("customer@example.com"),
            password_hash="hashed",
            full_name="Test Customer",
            phone_number=None,
            address=None,
            role=None,
            is_active=True,
            created_at=None
        )
        user_repo.add_user(user)
        
        return order_repo, product_repo, user_repo
    
    @pytest.fixture
    def use_case(self, repositories):
        """Create use case with mock repositories"""
        order_repo, product_repo, user_repo = repositories
        return CreateOrderByAdminUseCase(order_repo, product_repo, user_repo)
    
    def test_create_order_by_admin_success(self, use_case):
        """Should successfully create order by admin"""
        input_data = CreateOrderByAdminInputData(
            customer_email="customer@example.com",
            customer_phone="0123456789",
            shipping_address="123 Test Street, City",
            payment_method="COD",
            items=[
                OrderItemInput(product_id=1, quantity=2, unit_price=1000000.0),
                OrderItemInput(product_id=2, quantity=1, unit_price=1500000.0)
            ],
            notes="Test order",
            user_id=1
        )
        
        result = use_case.execute(input_data)
        
        assert result.success is True
        assert result.order_id is not None
        assert "successfully" in result.message.lower()
    
    def test_create_order_by_admin_without_user_id(self, use_case):
        """Should create order without user_id (guest order)"""
        input_data = CreateOrderByAdminInputData(
            customer_email="guest@example.com",
            customer_phone="0987654321",
            shipping_address="456 Guest Street, City",
            payment_method="COD",
            items=[
                OrderItemInput(product_id=1, quantity=1, unit_price=1000000.0)
            ],
            user_id=None
        )
        
        result = use_case.execute(input_data)
        
        assert result.success is True
        assert result.order_id is not None
    
    def test_create_order_by_admin_user_not_found(self, use_case):
        """Should fail when user not found"""
        input_data = CreateOrderByAdminInputData(
            customer_email="customer@example.com",
            customer_phone="0123456789",
            shipping_address="123 Test Street, City",
            payment_method="COD",
            items=[
                OrderItemInput(product_id=1, quantity=1, unit_price=1000000.0)
            ],
            user_id=999  # Non-existent user
        )
        
        result = use_case.execute(input_data)
        
        assert result.success is False
        assert "not found" in result.message.lower()
    
    def test_create_order_by_admin_empty_items(self, use_case):
        """Should fail when items list is empty"""
        input_data = CreateOrderByAdminInputData(
            customer_email="customer@example.com",
            customer_phone="0123456789",
            shipping_address="123 Test Street, City",
            payment_method="COD",
            items=[],
            user_id=1
        )
        
        result = use_case.execute(input_data)
        
        assert result.success is False
        assert "at least one item" in result.message.lower()
    
    def test_create_order_by_admin_product_not_found(self, use_case):
        """Should fail when product not found"""
        input_data = CreateOrderByAdminInputData(
            customer_email="customer@example.com",
            customer_phone="0123456789",
            shipping_address="123 Test Street, City",
            payment_method="COD",
            items=[
                OrderItemInput(product_id=999, quantity=1, unit_price=1000000.0)  # Non-existent product
            ],
            user_id=1
        )
        
        result = use_case.execute(input_data)
        
        assert result.success is False
        assert "not found" in result.message.lower()
    
    def test_create_order_by_admin_multiple_items(self, use_case):
        """Should create order with multiple items"""
        input_data = CreateOrderByAdminInputData(
            customer_email="customer@example.com",
            customer_phone="0123456789",
            shipping_address="123 Test Street, City",
            payment_method="BANK_TRANSFER",
            items=[
                OrderItemInput(product_id=1, quantity=2, unit_price=1000000.0),
                OrderItemInput(product_id=2, quantity=3, unit_price=1500000.0)
            ],
            notes="Bulk order",
            user_id=1
        )
        
        result = use_case.execute(input_data)
        
        assert result.success is True
        assert result.order_id is not None
