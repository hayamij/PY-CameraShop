"""
Tests for User domain entity
"""
import pytest
from datetime import datetime
from app.domain.entities.user import User
from app.domain.value_objects import Email, PhoneNumber
from app.domain.enums import UserRole
from app.domain.exceptions import InvalidCredentialsException, InsufficientPermissionsException


class TestUserCreation:
    """Test User entity creation"""
    
    def test_create_valid_user(self):
        """Should create user with valid data"""
        email = Email("user@example.com")
        phone = PhoneNumber("0123456789")
        
        user = User(
            username="testuser",
            email=email,
            password_hash="hashed_password",
            full_name="Test User",
            phone_number=phone,
            address="123 Test St",
            role=UserRole.CUSTOMER
        )
        
        assert user.username == "testuser"
        assert user.email == email
        assert user.full_name == "Test User"
        assert user.phone_number == phone
        assert user.address == "123 Test St"
        assert user.role == UserRole.CUSTOMER
        assert user.is_active is True
        assert user.id is None  # Not persisted yet
    
    def test_create_user_with_minimal_data(self):
        """Should create user with only required fields"""
        email = Email("user@example.com")
        
        user = User(
            username="testuser",
            email=email,
            password_hash="hashed_password",
            full_name="Test User"
        )
        
        assert user.username == "testuser"
        assert user.phone_number is None
        assert user.address is None
        assert user.role == UserRole.CUSTOMER  # Default role
    
    def test_create_user_strips_whitespace(self):
        """Should strip whitespace from string fields"""
        email = Email("user@example.com")
        
        user = User(
            username="  testuser  ",
            email=email,
            password_hash="hashed_password",
            full_name="  Test User  ",
            address="  123 Test St  "
        )
        
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.address == "123 Test St"
    
    def test_create_user_invalid_username_too_short(self):
        """Should raise error for username less than 3 characters"""
        email = Email("user@example.com")
        
        with pytest.raises(ValueError, match="Username must be at least 3 characters"):
            User(
                username="ab",
                email=email,
                password_hash="hashed_password",
                full_name="Test User"
            )
    
    def test_create_user_invalid_username_empty(self):
        """Should raise error for empty username"""
        email = Email("user@example.com")
        
        with pytest.raises(ValueError, match="Username must be at least 3 characters"):
            User(
                username="",
                email=email,
                password_hash="hashed_password",
                full_name="Test User"
            )
    
    def test_create_user_invalid_password_hash_empty(self):
        """Should raise error for empty password hash"""
        email = Email("user@example.com")
        
        with pytest.raises(ValueError, match="Password hash cannot be empty"):
            User(
                username="testuser",
                email=email,
                password_hash="",
                full_name="Test User"
            )
    
    def test_create_user_invalid_full_name_too_short(self):
        """Should raise error for full name less than 2 characters"""
        email = Email("user@example.com")
        
        with pytest.raises(ValueError, match="Full name must be at least 2 characters"):
            User(
                username="testuser",
                email=email,
                password_hash="hashed_password",
                full_name="A"
            )


class TestUserReconstruction:
    """Test User reconstruction from database"""
    
    def test_reconstruct_user(self):
        """Should reconstruct user from database without validation"""
        email = Email("user@example.com")
        phone = PhoneNumber("0123456789")
        created_at = datetime(2023, 1, 1, 12, 0, 0)
        
        user = User.reconstruct(
            user_id=1,
            username="testuser",
            email=email,
            password_hash="hashed_password",
            full_name="Test User",
            phone_number=phone,
            address="123 Test St",
            role=UserRole.ADMIN,
            is_active=False,
            created_at=created_at
        )
        
        assert user.id == 1
        assert user.username == "testuser"
        assert user.is_active is False
        assert user.created_at == created_at


class TestUserBehavior:
    """Test User entity behavior"""
    
    def test_verify_password_correct(self):
        """Should verify correct password"""
        from werkzeug.security import generate_password_hash
        
        email = Email("user@example.com")
        password = "SecurePassword123"
        password_hash = generate_password_hash(password)
        
        user = User(
            username="testuser",
            email=email,
            password_hash=password_hash,
            full_name="Test User"
        )
        
        assert user.verify_password(password) is True
    
    def test_verify_password_incorrect(self):
        """Should reject incorrect password"""
        from werkzeug.security import generate_password_hash
        
        email = Email("user@example.com")
        password = "SecurePassword123"
        password_hash = generate_password_hash(password)
        
        user = User(
            username="testuser",
            email=email,
            password_hash=password_hash,
            full_name="Test User"
        )
        
        with pytest.raises(InvalidCredentialsException):
            user.verify_password("WrongPassword")
    
    def test_update_password(self):
        """Should update password hash"""
        from werkzeug.security import generate_password_hash
        
        email = Email("user@example.com")
        old_password = "OldPassword123"
        old_hash = generate_password_hash(old_password)
        
        user = User(
            username="testuser",
            email=email,
            password_hash=old_hash,
            full_name="Test User"
        )
        
        new_password = "NewPassword456"
        new_hash = generate_password_hash(new_password)
        user.update_password(new_hash)
        
        assert user.verify_password(new_password) is True
    
    def test_update_password_empty_raises_error(self):
        """Should raise error for empty password hash"""
        email = Email("user@example.com")
        
        user = User(
            username="testuser",
            email=email,
            password_hash="hashed_password",
            full_name="Test User"
        )
        
        with pytest.raises(ValueError, match="Password hash cannot be empty"):
            user.update_password("")
    
    def test_change_role(self):
        """Should change user role"""
        email = Email("user@example.com")
        
        user = User(
            username="testuser",
            email=email,
            password_hash="hashed_password",
            full_name="Test User",
            role=UserRole.CUSTOMER
        )
        
        user.change_role(UserRole.ADMIN)
        assert user.role == UserRole.ADMIN
    
    def test_deactivate_user(self):
        """Should deactivate user"""
        email = Email("user@example.com")
        
        user = User(
            username="testuser",
            email=email,
            password_hash="hashed_password",
            full_name="Test User"
        )
        
        assert user.is_active is True
        user.deactivate()
        assert user.is_active is False
    
    def test_activate_user(self):
        """Should activate user"""
        email = Email("user@example.com")
        
        user = User.reconstruct(
            user_id=1,
            username="testuser",
            email=email,
            password_hash="hashed_password",
            full_name="Test User",
            phone_number=None,
            address=None,
            role=UserRole.CUSTOMER,
            is_active=False,
            created_at=datetime.now()
        )
        
        assert user.is_active is False
        user.activate()
        assert user.is_active is True
    
    def test_is_admin(self):
        """Should correctly identify admin users"""
        email = Email("user@example.com")
        
        admin = User(
            username="admin",
            email=email,
            password_hash="hashed_password",
            full_name="Admin User",
            role=UserRole.ADMIN
        )
        
        customer = User(
            username="customer",
            email=Email("customer@example.com"),
            password_hash="hashed_password",
            full_name="Customer User",
            role=UserRole.CUSTOMER
        )
        
        assert admin.is_admin() is True
        assert customer.is_admin() is False
    
    def test_is_customer(self):
        """Should correctly identify customer users"""
        email = Email("user@example.com")
        
        admin = User(
            username="admin",
            email=email,
            password_hash="hashed_password",
            full_name="Admin User",
            role=UserRole.ADMIN
        )
        
        customer = User(
            username="customer",
            email=Email("customer@example.com"),
            password_hash="hashed_password",
            full_name="Customer User",
            role=UserRole.CUSTOMER
        )
        
        assert admin.is_customer() is False
        assert customer.is_customer() is True
    
    def test_require_admin_permission(self):
        """Should allow admin operations for admin users"""
        email = Email("admin@example.com")
        
        admin = User(
            username="admin",
            email=email,
            password_hash="hashed_password",
            full_name="Admin User",
            role=UserRole.ADMIN
        )
        
        # Should not raise
        admin.require_admin_permission()
    
    def test_require_admin_permission_raises_for_customer(self):
        """Should raise error for non-admin users"""
        email = Email("customer@example.com")
        
        customer = User(
            username="customer",
            email=email,
            password_hash="hashed_password",
            full_name="Customer User",
            role=UserRole.CUSTOMER
        )
        
        with pytest.raises(InsufficientPermissionsException):
            customer.require_admin_permission()
    
    def test_update_profile(self):
        """Should update user profile"""
        email = Email("user@example.com")
        phone = PhoneNumber("0123456789")
        
        user = User(
            username="testuser",
            email=email,
            password_hash="hashed_password",
            full_name="Test User"
        )
        
        new_phone = PhoneNumber("0987654321")
        user.update_profile(
            full_name="Updated User",
            phone_number=new_phone,
            address="New Address"
        )
        
        assert user.full_name == "Updated User"
        assert user.phone_number == new_phone
        assert user.address == "New Address"
    
    def test_update_profile_invalid_full_name(self):
        """Should raise error for invalid full name"""
        email = Email("user@example.com")
        
        user = User(
            username="testuser",
            email=email,
            password_hash="hashed_password",
            full_name="Test User"
        )
        
        with pytest.raises(ValueError, match="Full name must be at least 2 characters"):
            user.update_profile(full_name="A")


class TestUserEquality:
    """Test User equality comparison"""
    
    def test_users_with_same_id_are_equal(self):
        """Should consider users with same ID as equal"""
        email1 = Email("user1@example.com")
        email2 = Email("user2@example.com")
        
        user1 = User.reconstruct(
            user_id=1,
            username="user1",
            email=email1,
            password_hash="hash1",
            full_name="User One",
            phone_number=None,
            address=None,
            role=UserRole.CUSTOMER,
            is_active=True,
            created_at=datetime.now()
        )
        
        user2 = User.reconstruct(
            user_id=1,
            username="user2",
            email=email2,
            password_hash="hash2",
            full_name="User Two",
            phone_number=None,
            address=None,
            role=UserRole.ADMIN,
            is_active=True,
            created_at=datetime.now()
        )
        
        assert user1 == user2
    
    def test_users_with_different_id_are_not_equal(self):
        """Should consider users with different IDs as not equal"""
        email = Email("user@example.com")
        
        user1 = User.reconstruct(
            user_id=1,
            username="testuser",
            email=email,
            password_hash="hash",
            full_name="Test User",
            phone_number=None,
            address=None,
            role=UserRole.CUSTOMER,
            is_active=True,
            created_at=datetime.now()
        )
        
        user2 = User.reconstruct(
            user_id=2,
            username="testuser",
            email=email,
            password_hash="hash",
            full_name="Test User",
            phone_number=None,
            address=None,
            role=UserRole.CUSTOMER,
            is_active=True,
            created_at=datetime.now()
        )
        
        assert user1 != user2
