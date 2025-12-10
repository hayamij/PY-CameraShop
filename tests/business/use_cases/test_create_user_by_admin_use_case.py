"""
Unit Tests for CreateUserByAdminUseCase (Admin User Management - USE CASE 3)

Test Coverage: TC3.1 - TC3.24
Business Rules:
- Only admin can create users
- Username unique (3-50 chars, alphanumeric + underscore)
- Email unique and valid format
- Password minimum 8 chars, hashed before save
- Full name minimum 2 chars
- Phone number optional, validate if provided
- Address optional
- Role: ADMIN or CUSTOMER
- Default: is_active=true
- Never expose password_hash in output
"""
import pytest
from unittest.mock import Mock, patch
from app.business.use_cases.create_user_by_admin_use_case import (
    CreateUserByAdminUseCase,
    CreateUserInputData,
    CreateUserOutputData
)
from app.domain.entities import User
from app.domain.enums import UserRole
from app.domain.value_objects import Email, PhoneNumber
from app.domain.exceptions import UserAlreadyExistsException


class TestCreateUserInputDataValidation:
    """Test Input DTO validation"""
    
    def test_input_with_all_valid_data_customer(self):
        """TC3.1: Create user with all valid data (CUSTOMER)"""
        input_data = CreateUserInputData(
            username="newcustomer",
            email="customer@test.com",
            password="password123",
            full_name="New Customer",
            phone_number="0912345678",
            address="123 Test Street",
            role="CUSTOMER"
        )
        
        assert input_data.username == "newcustomer"
        assert input_data.email == "customer@test.com"
        assert input_data.password == "password123"
        assert input_data.full_name == "New Customer"
        assert input_data.phone_number == "0912345678"
        assert input_data.address == "123 Test Street"
        assert input_data.role == "CUSTOMER"
    
    def test_input_with_all_valid_data_admin(self):
        """TC3.2: Create user with all valid data (ADMIN)"""
        input_data = CreateUserInputData(
            username="newadmin",
            email="admin@test.com",
            password="admin12345",
            full_name="New Admin",
            phone_number="0923456789",
            address="456 Admin Street",
            role="ADMIN"
        )
        
        assert input_data.role == "ADMIN"
    
    def test_input_with_only_required_fields(self):
        """TC3.3: Create user with only required fields"""
        input_data = CreateUserInputData(
            username="minimal",
            email="minimal@test.com",
            password="password123",
            full_name="Min User",
            phone_number=None,
            address=None,
            role="CUSTOMER"
        )
        
        assert input_data.phone_number is None
        assert input_data.address is None
    
    def test_input_username_empty_raises_error(self):
        """TC3.4: Username empty - validation error"""
        with pytest.raises(ValueError, match="Username cannot be empty"):
            CreateUserInputData(
                username="",
                email="test@test.com",
                password="password123",
                full_name="Test User",
                role="CUSTOMER"
            )
    
    def test_input_username_too_short_raises_error(self):
        """TC3.5: Username < 3 chars - validation error"""
        with pytest.raises(ValueError, match="Username must be between 3 and 50 characters"):
            CreateUserInputData(
                username="ab",
                email="test@test.com",
                password="password123",
                full_name="Test User",
                role="CUSTOMER"
            )
    
    def test_input_username_too_long_raises_error(self):
        """TC3.6: Username > 50 chars - validation error"""
        long_username = "a" * 51
        with pytest.raises(ValueError, match="Username must be between 3 and 50 characters"):
            CreateUserInputData(
                username=long_username,
                email="test@test.com",
                password="password123",
                full_name="Test User",
                role="CUSTOMER"
            )
    
    def test_input_username_invalid_chars_raises_error(self):
        """TC3.7: Username with invalid chars - validation error"""
        with pytest.raises(ValueError, match="Username can only contain letters, numbers, and underscores"):
            CreateUserInputData(
                username="user name",  # Space is invalid
                email="test@test.com",
                password="password123",
                full_name="Test User",
                role="CUSTOMER"
            )
    
    def test_input_email_empty_raises_error(self):
        """TC3.9: Email empty - validation error"""
        with pytest.raises(ValueError, match="Email cannot be empty"):
            CreateUserInputData(
                username="testuser",
                email="",
                password="password123",
                full_name="Test User",
                role="CUSTOMER"
            )
    
    def test_input_password_empty_raises_error(self):
        """TC3.12: Password empty - validation error"""
        with pytest.raises(ValueError, match="Password cannot be empty"):
            CreateUserInputData(
                username="testuser",
                email="test@test.com",
                password="",
                full_name="Test User",
                role="CUSTOMER"
            )
    
    def test_input_password_too_short_raises_error(self):
        """TC3.13: Password < 8 chars - validation error"""
        with pytest.raises(ValueError, match="Password must be at least 8 characters"):
            CreateUserInputData(
                username="testuser",
                email="test@test.com",
                password="pass123",  # Only 7 chars
                full_name="Test User",
                role="CUSTOMER"
            )
    
    def test_input_full_name_empty_raises_error(self):
        """TC3.15: Full name empty - validation error"""
        with pytest.raises(ValueError, match="Full name cannot be empty"):
            CreateUserInputData(
                username="testuser",
                email="test@test.com",
                password="password123",
                full_name="",
                role="CUSTOMER"
            )
    
    def test_input_full_name_too_short_raises_error(self):
        """TC3.16: Full name < 2 chars - validation error"""
        with pytest.raises(ValueError, match="Full name must be at least 2 characters"):
            CreateUserInputData(
                username="testuser",
                email="test@test.com",
                password="password123",
                full_name="A",
                role="CUSTOMER"
            )
    
    def test_input_invalid_role_raises_error(self):
        """TC3.19: Invalid role - validation error"""
        with pytest.raises(ValueError, match="Role must be either ADMIN or CUSTOMER"):
            CreateUserInputData(
                username="testuser",
                email="test@test.com",
                password="password123",
                full_name="Test User",
                role="INVALID_ROLE"
            )
    
    def test_input_role_case_insensitive(self):
        """TC3.20: Role case-insensitive"""
        input_data = CreateUserInputData(
            username="testuser",
            email="test@test.com",
            password="password123",
            full_name="Test User",
            role="admin"  # lowercase
        )
        
        assert input_data.role == "ADMIN"  # normalized to uppercase
    
    def test_input_empty_role_raises_error(self):
        """TC3.23: Empty role - validation error"""
        with pytest.raises(ValueError, match="Role cannot be empty"):
            CreateUserInputData(
                username="testuser",
                email="test@test.com",
                password="password123",
                full_name="Test User",
                role=""
            )


@pytest.fixture
def mock_user_repository():
    """Mock IUserRepository"""
    return Mock()


@pytest.fixture
def mock_password_service():
    """Mock PasswordHashingService"""
    return Mock()


@pytest.fixture
def use_case(mock_user_repository, mock_password_service):
    """CreateUserByAdminUseCase instance"""
    return CreateUserByAdminUseCase(
        user_repository=mock_user_repository,
        password_service=mock_password_service
    )


class TestCreateUserByAdminUseCase:
    """Test CreateUserByAdminUseCase business logic"""
    
    def test_create_customer_with_all_fields_success(self, use_case, mock_user_repository, mock_password_service):
        """TC3.1: Create CUSTOMER with all valid data - success"""
        # Arrange
        mock_password_service.hash_password.return_value = "$2b$12$hashedpassword"
        mock_user_repository.exists_by_username.return_value = False
        mock_user_repository.exists_by_email.return_value = False
        
        created_user = User.reconstruct(
            user_id=10,
            username="newcustomer",
            email=Email("customer@test.com"),
            password_hash="$2b$12$hashedpassword",
            full_name="New Customer",
            phone_number=PhoneNumber("0912345678"),
            address="123 Test Street",
            role=UserRole.CUSTOMER,
            is_active=True,
            created_at=None
        )
        mock_user_repository.save.return_value = created_user
        
        input_data = CreateUserInputData(
            username="newcustomer",
            email="customer@test.com",
            password="password123",
            full_name="New Customer",
            phone_number="0912345678",
            address="123 Test Street",
            role="CUSTOMER"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.user_id == 10
        assert output.username == "newcustomer"
        assert "successfully created" in output.message.lower()
        # Verify password was hashed
        mock_password_service.hash_password.assert_called_once_with("password123")
    
    def test_create_admin_with_all_fields_success(self, use_case, mock_user_repository, mock_password_service):
        """TC3.2: Create ADMIN with all valid data - success"""
        # Arrange
        mock_password_service.hash_password.return_value = "$2b$12$hashedadminpass"
        mock_user_repository.exists_by_username.return_value = False
        mock_user_repository.exists_by_email.return_value = False
        
        created_user = User.reconstruct(
            user_id=11,
            username="newadmin",
            email=Email("admin@test.com"),
            password_hash="$2b$12$hashedadminpass",
            full_name="New Admin",
            phone_number=PhoneNumber("0923456789"),
            address="456 Admin Street",
            role=UserRole.ADMIN,
            is_active=True,
            created_at=None
        )
        mock_user_repository.save.return_value = created_user
        
        input_data = CreateUserInputData(
            username="newadmin",
            email="admin@test.com",
            password="admin12345",
            full_name="New Admin",
            phone_number="0923456789",
            address="456 Admin Street",
            role="ADMIN"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.user_id == 11
        assert output.username == "newadmin"
    
    def test_create_user_with_only_required_fields_success(self, use_case, mock_user_repository, mock_password_service):
        """TC3.3: Create user with only required fields - success"""
        # Arrange
        mock_password_service.hash_password.return_value = "$2b$12$hashedpass"
        mock_user_repository.exists_by_username.return_value = False
        mock_user_repository.exists_by_email.return_value = False
        
        created_user = User.reconstruct(
            user_id=12,
            username="minimal",
            email=Email("minimal@test.com"),
            password_hash="$2b$12$hashedpass",
            full_name="Min User",
            phone_number=None,
            address=None,
            role=UserRole.CUSTOMER,
            is_active=True,
            created_at=None
        )
        mock_user_repository.save.return_value = created_user
        
        input_data = CreateUserInputData(
            username="minimal",
            email="minimal@test.com",
            password="password123",
            full_name="Min User",
            phone_number=None,
            address=None,
            role="CUSTOMER"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.user_id == 12
    
    def test_username_already_exists_error(self, use_case, mock_user_repository, mock_password_service):
        """TC3.8: Username already exists - error"""
        # Arrange
        mock_user_repository.exists_by_username.return_value = True
        
        input_data = CreateUserInputData(
            username="existinguser",
            email="new@test.com",
            password="password123",
            full_name="Test User",
            role="CUSTOMER"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "username" in output.error_message.lower()
        assert "already exists" in output.error_message.lower()
    
    def test_email_already_exists_error(self, use_case, mock_user_repository, mock_password_service):
        """TC3.11: Email already exists - error"""
        # Arrange
        mock_user_repository.exists_by_username.return_value = False
        mock_user_repository.exists_by_email.return_value = True
        
        input_data = CreateUserInputData(
            username="newuser",
            email="existing@test.com",
            password="password123",
            full_name="Test User",
            role="CUSTOMER"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "email" in output.error_message.lower()
        assert "already exists" in output.error_message.lower()
    
    def test_password_properly_hashed(self, use_case, mock_user_repository, mock_password_service):
        """TC3.14: Password properly hashed with bcrypt"""
        # Arrange
        mock_password_service.hash_password.return_value = "$2b$12$realhashvalue"
        mock_user_repository.exists_by_username.return_value = False
        mock_user_repository.exists_by_email.return_value = False
        
        created_user = User.reconstruct(
            user_id=13,
            username="testuser",
            email=Email("test@test.com"),
            password_hash="$2b$12$realhashvalue",
            full_name="Test User",
            phone_number=None,
            address=None,
            role=UserRole.CUSTOMER,
            is_active=True,
            created_at=None
        )
        mock_user_repository.save.return_value = created_user
        
        input_data = CreateUserInputData(
            username="testuser",
            email="test@test.com",
            password="plainpassword",
            full_name="Test User",
            role="CUSTOMER"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        mock_password_service.hash_password.assert_called_once_with("plainpassword")
        # Verify hashed password used in User entity
        saved_user_call = mock_user_repository.save.call_args[0][0]
        assert saved_user_call.password_hash == "$2b$12$realhashvalue"
    
    def test_phone_number_valid_format_success(self, use_case, mock_user_repository, mock_password_service):
        """TC3.18: Phone number valid format - success"""
        # Arrange
        mock_password_service.hash_password.return_value = "$2b$12$hash"
        mock_user_repository.exists_by_username.return_value = False
        mock_user_repository.exists_by_email.return_value = False
        
        created_user = User.reconstruct(
            user_id=14,
            username="phoneuser",
            email=Email("phone@test.com"),
            password_hash="$2b$12$hash",
            full_name="Phone User",
            phone_number=PhoneNumber("0987654321"),
            address=None,
            role=UserRole.CUSTOMER,
            is_active=True,
            created_at=None
        )
        mock_user_repository.save.return_value = created_user
        
        input_data = CreateUserInputData(
            username="phoneuser",
            email="phone@test.com",
            password="password123",
            full_name="Phone User",
            phone_number="0987654321",
            role="CUSTOMER"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
    
    def test_created_user_is_active_by_default(self, use_case, mock_user_repository, mock_password_service):
        """TC3.21: Created user is_active=true by default"""
        # Arrange
        mock_password_service.hash_password.return_value = "$2b$12$hash"
        mock_user_repository.exists_by_username.return_value = False
        mock_user_repository.exists_by_email.return_value = False
        
        created_user = User.reconstruct(
            user_id=15,
            username="activeuser",
            email=Email("active@test.com"),
            password_hash="$2b$12$hash",
            full_name="Active User",
            phone_number=None,
            address=None,
            role=UserRole.CUSTOMER,
            is_active=True,
            created_at=None
        )
        mock_user_repository.save.return_value = created_user
        
        input_data = CreateUserInputData(
            username="activeuser",
            email="active@test.com",
            password="password123",
            full_name="Active User",
            role="CUSTOMER"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        # Verify saved user has is_active=True
        saved_user = mock_user_repository.save.call_args[0][0]
        assert saved_user.is_active is True
    
    def test_password_hash_never_exposed_in_output(self, use_case, mock_user_repository, mock_password_service):
        """TC3.22: Verify password_hash never returned in output"""
        # Arrange
        mock_password_service.hash_password.return_value = "$2b$12$hash"
        mock_user_repository.exists_by_username.return_value = False
        mock_user_repository.exists_by_email.return_value = False
        
        created_user = User.reconstruct(
            user_id=16,
            username="secureuser",
            email=Email("secure@test.com"),
            password_hash="$2b$12$hash",
            full_name="Secure User",
            phone_number=None,
            address=None,
            role=UserRole.CUSTOMER,
            is_active=True,
            created_at=None
        )
        mock_user_repository.save.return_value = created_user
        
        input_data = CreateUserInputData(
            username="secureuser",
            email="secure@test.com",
            password="password123",
            full_name="Secure User",
            role="CUSTOMER"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        # Verify NO password_hash attribute in output
        assert not hasattr(output, 'password_hash')
        # Check output dict
        output_dict = {
            'success': output.success,
            'user_id': output.user_id,
            'username': output.username,
            'message': output.message
        }
        assert 'password_hash' not in output_dict
    
    def test_special_characters_in_full_name_handled(self, use_case, mock_user_repository, mock_password_service):
        """TC3.24: Special characters in full_name - handled properly"""
        # Arrange
        mock_password_service.hash_password.return_value = "$2b$12$hash"
        mock_user_repository.exists_by_username.return_value = False
        mock_user_repository.exists_by_email.return_value = False
        
        created_user = User.reconstruct(
            user_id=17,
            username="specialuser",
            email=Email("special@test.com"),
            password_hash="$2b$12$hash",
            full_name="Nguyễn Văn Á",  # Vietnamese characters
            phone_number=None,
            address=None,
            role=UserRole.CUSTOMER,
            is_active=True,
            created_at=None
        )
        mock_user_repository.save.return_value = created_user
        
        input_data = CreateUserInputData(
            username="specialuser",
            email="special@test.com",
            password="password123",
            full_name="Nguyễn Văn Á",
            role="CUSTOMER"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
    
    def test_email_invalid_format_caught_by_value_object(self, use_case, mock_user_repository, mock_password_service):
        """TC3.10: Email invalid format - validation error"""
        # Arrange
        mock_user_repository.exists_by_username.return_value = False
        
        input_data = CreateUserInputData(
            username="testuser",
            email="invalid-email",  # Invalid format
            password="password123",
            full_name="Test User",
            role="CUSTOMER"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "email" in output.error_message.lower()
    
    def test_phone_invalid_format_caught_by_value_object(self, use_case, mock_user_repository, mock_password_service):
        """TC3.17: Phone number invalid format - validation error"""
        # Arrange
        mock_user_repository.exists_by_username.return_value = False
        mock_user_repository.exists_by_email.return_value = False
        
        input_data = CreateUserInputData(
            username="testuser",
            email="test@test.com",
            password="password123",
            full_name="Test User",
            phone_number="123",  # Invalid Vietnamese phone format
            role="CUSTOMER"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "phone" in output.error_message.lower()
