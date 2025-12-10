"""
Pytest configuration and fixtures

Provides common test fixtures and configuration
"""

import pytest
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# Flask app fixtures for API testing
@pytest.fixture(scope='function')
def app():
    """
    Create Flask app for API testing
    Note: Uses production database (camerashop.db) - data will be cleaned up after tests
    For full isolation, run tests separately from production
    """
    from app.infrastructure.factory import create_app
    from app.infrastructure.config.database import Base, init_database
    
    # Create app with test configuration
    test_app = create_app()
    test_app.config['TESTING'] = True
    test_app.config['SECRET_KEY'] = 'test-secret-key'
    
    # Ensure database tables exist
    engine = init_database(test_app)
    Base.metadata.create_all(engine)
    
    yield test_app


@pytest.fixture(scope='function')
def client(app):
    """Create Flask test client"""
    return app.test_client()


@pytest.fixture
def mock_db_session():
    """Mock database session"""
    from unittest.mock import Mock
    session = Mock()
    session.commit = Mock()
    session.rollback = Mock()
    session.close = Mock()
    return session


# Integration test fixtures
@pytest.fixture(scope='session')
def test_engine():
    """Create a test database engine"""
    from app.infrastructure.config.database import Base
    from app.infrastructure.database import models  # Import models to register them
    
    # Use in-memory SQLite for tests
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(engine)
    
    yield engine
    
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope='function')
def db_session(test_engine):
    """Create a new database session for a test"""
    connection = test_engine.connect()
    transaction = connection.begin()
    
    Session = scoped_session(sessionmaker(bind=connection))
    session = Session()
    
    yield session
    
    session.close()
    Session.remove()
    transaction.rollback()
    connection.close()


@pytest.fixture
def user_repository(db_session):
    """Create UserRepository with test database session"""
    from app.adapters.repositories.user_repository_adapter import UserRepositoryAdapter
    return UserRepositoryAdapter(db_session)


@pytest.fixture
def product_repository(db_session):
    """Create ProductRepository with test database session"""
    from app.adapters.repositories.product_repository_adapter import ProductRepositoryAdapter
    return ProductRepositoryAdapter(db_session)


@pytest.fixture
def category_repository(db_session):
    """Create CategoryRepository with test database session"""
    from app.adapters.repositories.category_repository_adapter import CategoryRepositoryAdapter
    return CategoryRepositoryAdapter(db_session)


@pytest.fixture
def brand_repository(db_session):
    """Create BrandRepository with test database session"""
    from app.adapters.repositories.brand_repository_adapter import BrandRepositoryAdapter
    return BrandRepositoryAdapter(db_session)


@pytest.fixture
def cart_repository(db_session):
    """Create CartRepository with test database session"""
    from app.adapters.repositories.cart_repository_adapter import CartRepositoryAdapter
    return CartRepositoryAdapter(db_session)


@pytest.fixture
def order_repository(db_session):
    """Create OrderRepository with test database session"""
    from app.adapters.repositories.order_repository_adapter import OrderRepositoryAdapter
    return OrderRepositoryAdapter(db_session)


@pytest.fixture
def sample_user(user_repository):
    """Create a sample user for testing"""
    from app.domain.entities.user import User
    from app.domain.value_objects.email import Email
    from app.domain.enums import UserRole
    
    user = User(
        username="testuser",
        email=Email("testuser@example.com"),
        password_hash="hashed_password",
        full_name="Test User",
        role=UserRole.CUSTOMER
    )
    
    return user_repository.save(user)


@pytest.fixture
def sample_category(category_repository):
    """Create a sample category for testing"""
    from app.domain.entities.category import Category
    
    category = Category(
        name="Test Category",
        description="Test category description"
    )
    
    return category_repository.save(category)


@pytest.fixture
def sample_brand(brand_repository):
    """Create a sample brand for testing"""
    from app.domain.entities.brand import Brand
    
    brand = Brand(
        name="Test Brand",
        description="Test brand description",
        logo_url="http://example.com/logo.jpg"
    )
    
    return brand_repository.save(brand)


@pytest.fixture
def sample_product(product_repository, sample_category, sample_brand):
    """Create a sample product for testing"""
    from app.domain.entities.product import Product
    from app.domain.value_objects.money import Money
    
    product = Product(
        name="Test Product",
        description="Test product description",
        price=Money(1000.00),
        stock_quantity=50,
        category_id=sample_category.id,
        brand_id=sample_brand.id,
        image_url="http://example.com/product.jpg"
    )
    
    return product_repository.save(product)


@pytest.fixture
def sample_cart(cart_repository, sample_user, sample_product):
    """Create a sample cart for testing"""
    from app.domain.entities.cart import Cart
    
    cart = Cart(customer_id=sample_user.id)
    cart.add_item(product_id=sample_product.id, quantity=2)
    
    return cart_repository.save(cart)


@pytest.fixture
def sample_order(order_repository, sample_user, sample_product):
    """Create a sample order for testing"""
    from app.domain.entities.order import Order, OrderItem
    from app.domain.value_objects.money import Money
    from app.domain.enums import PaymentMethod
    
    items = [
        OrderItem(
            product_id=sample_product.id,
            product_name=sample_product.name,
            quantity=2,
            unit_price=sample_product.price
        )
    ]
    
    order = Order(
        customer_id=sample_user.id,
        items=items,
        payment_method=PaymentMethod.CREDIT_CARD,
        shipping_address="123 Test Street, Test City"
    )
    
    return order_repository.save(order)
