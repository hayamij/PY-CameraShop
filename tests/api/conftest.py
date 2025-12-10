"""
Shared test fixtures for API integration tests
"""
import pytest
from app.infrastructure.factory import create_app
from app.infrastructure.config.database import init_database, get_session, create_all_tables


@pytest.fixture(scope='session')
def app():
    """Create Flask app for entire test session"""
    # Create app with 'testing' config to use in-memory database from start
    test_app = create_app('testing')
    
    # Override config to ensure in-memory database
    test_app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key-for-testing',
        'WTF_CSRF_ENABLED': False,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })
    
    with test_app.app_context():
        # Database already initialized in create_app('testing')
        # Tables already created (see factory.py line 52-53)
        
        # Seed default roles (required for user registration)
        from app.infrastructure.database.models import RoleModel
        from app.infrastructure.config import get_session
        session = get_session()
        
        # Check if roles exist, if not create them
        existing_roles = session.query(RoleModel).count()
        if existing_roles == 0:
            admin_role = RoleModel(role_id=1, role_name='ADMIN', description='Administrator')
            user_role = RoleModel(role_id=2, role_name='USER', description='Regular user')
            session.add_all([admin_role, user_role])
            session.commit()
        
        yield test_app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def db(app):
    """Get database instance"""
    with app.app_context():
        database = get_session()
        yield database
        # Cleanup after each test
        database.rollback()


@pytest.fixture
def clean_db(db):
    """Clean database before test"""
    # Import all models
    from app.infrastructure.database.models.user_model import UserModel
    from app.infrastructure.database.models.product_model import (
        ProductModel, CategoryModel, BrandModel
    )
    from app.infrastructure.database.models.cart_model import CartModel, CartItemModel
    from app.infrastructure.database.models.order_model import OrderModel, OrderItemModel
    
    # Delete all data (respecting foreign keys)
    db.query(OrderItemModel).delete()
    db.query(OrderModel).delete()
    db.query(CartItemModel).delete()
    db.query(CartModel).delete()
    db.query(ProductModel).delete()
    db.query(CategoryModel).delete()
    db.query(BrandModel).delete()
    db.query(UserModel).delete()
    db.commit()
    
    yield db
    
    # Cleanup after test
    db.rollback()


@pytest.fixture
def sample_user_data():
    """Sample user registration data"""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'SecurePassword123',
        'full_name': 'Test User',
        'phone_number': '0123456789',
        'address': '123 Test Street'
    }
