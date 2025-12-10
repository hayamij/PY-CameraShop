"""
Test Suite for UpdateUserByAdminUseCase (USE CASE 4)
Test-Driven Development: RED phase - write tests first

Requirements from todo.txt:
- Admin can update user information
- Cannot self-deactivate
- Cannot self-demote from ADMIN
- Username/email uniqueness validated on change
- All fields validated like Create
- Role can be changed (ADMIN ↔ CUSTOMER)
- Can activate/deactivate users
- Cannot update password (separate use case)

Test Coverage: 28 tests (TC4.1 - TC4.28)
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock

from app.business.use_cases.update_user_by_admin_use_case import (
    UpdateUserByAdminUseCase,
    UpdateUserInputData,
    UpdateUserOutputData
)
from app.domain.entities import User
from app.domain.value_objects import Email, PhoneNumber
from app.domain.enums import UserRole
from app.domain.exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_user_repository():
    """Mock user repository for unit testing"""
    return Mock()


@pytest.fixture
def sample_target_user():
    """Sample target user to be updated (CUSTOMER)"""
    return User.reconstruct(
        user_id=2,
        username="customer1",
        email=Email("customer1@example.com"),
        password_hash="hashed_password",
        full_name="John Doe",
        phone_number=PhoneNumber("0123456789"),
        address="123 Main St",
        role=UserRole.CUSTOMER,
        is_active=True,
        created_at=datetime(2024, 1, 1)
    )


@pytest.fixture
def sample_admin_user():
    """Sample admin user performing the update"""
    return User.reconstruct(
        user_id=1,
        username="admin",
        email=Email("admin@example.com"),
        password_hash="hashed_admin_password",
        full_name="Admin User",
        phone_number=None,
        address=None,
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime(2023, 12, 1)
    )


@pytest.fixture
def another_admin_user():
    """Another admin user to be updated"""
    return User.reconstruct(
        user_id=3,
        username="admin2",
        email=Email("admin2@example.com"),
        password_hash="hashed_admin2_password",
        full_name="Admin Two",
        phone_number=None,
        address=None,
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime(2023, 12, 15)
    )


# ============================================================================
# TEST CLASS 1: INPUT DATA VALIDATION (TC4.11 - TC4.19)
# ============================================================================

class TestUpdateUserInputDataValidation:
    """Test input validation for UpdateUserByAdminUseCase"""
    
    def test_tc4_12_invalid_user_id_zero(self):
        """TC4.12: Invalid user_id (0) - validation error"""
        with pytest.raises(ValueError, match="user_id must be positive"):
            UpdateUserInputData(
                user_id=0,
                admin_user_id=1,
                username="newusername"
            )
    
    def test_tc4_12_invalid_user_id_negative(self):
        """TC4.12: Invalid user_id (negative) - validation error"""
        with pytest.raises(ValueError, match="user_id must be positive"):
            UpdateUserInputData(
                user_id=-5,
                admin_user_id=1,
                username="newusername"
            )
    
    def test_tc4_17_invalid_username_too_short(self):
        """TC4.17: Invalid username format (< 3 chars) - validation error"""
        with pytest.raises(ValueError, match="Username must be 3-50 characters"):
            UpdateUserInputData(
                user_id=2,
                admin_user_id=1,
                username="ab"
            )
    
    def test_tc4_17_invalid_username_too_long(self):
        """TC4.17: Invalid username format (> 50 chars) - validation error"""
        with pytest.raises(ValueError, match="Username must be 3-50 characters"):
            UpdateUserInputData(
                user_id=2,
                admin_user_id=1,
                username="a" * 51
            )
    
    def test_tc4_17_invalid_username_special_chars(self):
        """TC4.17: Invalid username format (special chars) - validation error"""
        with pytest.raises(ValueError, match="Username must contain only alphanumeric"):
            UpdateUserInputData(
                user_id=2,
                admin_user_id=1,
                username="user@name!"
            )
    
    def test_tc4_18_invalid_email_format(self):
        """TC4.18: Invalid email format - validation error"""
        with pytest.raises(ValueError, match="Invalid email format"):
            UpdateUserInputData(
                user_id=2,
                admin_user_id=1,
                email="invalid-email"
            )
    
    def test_tc4_19_invalid_phone_format(self):
        """TC4.19: Invalid phone format - validation error"""
        with pytest.raises(ValueError, match="Invalid Vietnamese phone number"):
            UpdateUserInputData(
                user_id=2,
                admin_user_id=1,
                phone_number="123"  # Invalid Vietnamese format
            )
    
    def test_valid_input_all_fields(self):
        """Valid input with all fields provided"""
        input_data = UpdateUserInputData(
            user_id=2,
            admin_user_id=1,
            username="newusername",
            email="newemail@example.com",
            full_name="New Name",
            phone_number="0987654321",
            address="New Address",
            role="CUSTOMER",
            is_active=True
        )
        assert input_data.user_id == 2
        assert input_data.admin_user_id == 1
        assert input_data.username == "newusername"
        assert input_data.email.address == "newemail@example.com"


# ============================================================================
# TEST CLASS 2: UPDATE USER BUSINESS LOGIC (TC4.1 - TC4.28)
# ============================================================================

class TestUpdateUserByAdminUseCase:
    """Test UpdateUserByAdminUseCase business logic"""
    
    # ========== SUCCESS CASES (TC4.1 - TC4.10) ==========
    
    def test_tc4_1_update_all_fields_success(
        self,
        mock_user_repository,
        sample_target_user,
        sample_admin_user
    ):
        """TC4.1: Update user with all fields - success"""
        # Arrange
        mock_user_repository.find_by_id.return_value = sample_target_user
        mock_user_repository.exists_by_username.return_value = False
        mock_user_repository.exists_by_email.return_value = False
        # Mock save to return the user passed to it (which may be reconstructed)
        mock_user_repository.save.side_effect = lambda user: user
        
        use_case = UpdateUserByAdminUseCase(mock_user_repository)
        
        input_data = UpdateUserInputData(
            user_id=2,
            admin_user_id=1,
            username="newusername",
            email="newemail@example.com",
            full_name="Jane Smith",
            phone_number="0987654321",
            address="456 New St",
            role="ADMIN",
            is_active=False
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.user_id == 2
        assert output.username == "newusername"
        assert "successfully" in output.message.lower()
        assert "password_hash" not in output.__dict__
        mock_user_repository.save.assert_called_once()
    
    def test_tc4_2_update_only_username_success(
        self,
        mock_user_repository,
        sample_target_user
    ):
        """TC4.2: Update only username - success"""
        # Arrange
        mock_user_repository.find_by_id.return_value = sample_target_user
        mock_user_repository.exists_by_username.return_value = False
        # Mock save to return the user passed to it
        mock_user_repository.save.side_effect = lambda user: user
        
        use_case = UpdateUserByAdminUseCase(mock_user_repository)
        
        input_data = UpdateUserInputData(
            user_id=2,
            admin_user_id=1,
            username="newusername"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        # Check returned username (user object may be replaced)
        assert output.username == "newusername"
    
    def test_tc4_3_update_only_email_success(
        self,
        mock_user_repository,
        sample_target_user
    ):
        """TC4.3: Update only email - success"""
        # Arrange
        mock_user_repository.find_by_id.return_value = sample_target_user
        mock_user_repository.exists_by_email.return_value = False
        mock_user_repository.save.return_value = sample_target_user
        
        use_case = UpdateUserByAdminUseCase(mock_user_repository)
        
        input_data = UpdateUserInputData(
            user_id=2,
            admin_user_id=1,
            email="newemail@example.com"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
    
    def test_tc4_4_update_only_full_name_success(
        self,
        mock_user_repository,
        sample_target_user
    ):
        """TC4.4: Update only full_name - success"""
        # Arrange
        mock_user_repository.find_by_id.return_value = sample_target_user
        mock_user_repository.save.return_value = sample_target_user
        
        use_case = UpdateUserByAdminUseCase(mock_user_repository)
        
        input_data = UpdateUserInputData(
            user_id=2,
            admin_user_id=1,
            full_name="Updated Full Name"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert sample_target_user.full_name == "Updated Full Name"
    
    def test_tc4_5_update_only_phone_number_success(
        self,
        mock_user_repository,
        sample_target_user
    ):
        """TC4.5: Update only phone_number - success"""
        # Arrange
        mock_user_repository.find_by_id.return_value = sample_target_user
        mock_user_repository.save.return_value = sample_target_user
        
        use_case = UpdateUserByAdminUseCase(mock_user_repository)
        
        input_data = UpdateUserInputData(
            user_id=2,
            admin_user_id=1,
            phone_number="0999888777"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert sample_target_user.phone_number.number == "0999888777"
    
    def test_tc4_6_update_only_address_success(
        self,
        mock_user_repository,
        sample_target_user
    ):
        """TC4.6: Update only address - success"""
        # Arrange
        mock_user_repository.find_by_id.return_value = sample_target_user
        mock_user_repository.save.return_value = sample_target_user
        
        use_case = UpdateUserByAdminUseCase(mock_user_repository)
        
        input_data = UpdateUserInputData(
            user_id=2,
            admin_user_id=1,
            address="789 Updated Street"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert sample_target_user.address == "789 Updated Street"
    
    def test_tc4_7_update_role_customer_to_admin_success(
        self,
        mock_user_repository,
        sample_target_user
    ):
        """TC4.7: Update role (CUSTOMER → ADMIN) - success"""
        # Arrange
        mock_user_repository.find_by_id.return_value = sample_target_user
        mock_user_repository.save.return_value = sample_target_user
        
        use_case = UpdateUserByAdminUseCase(mock_user_repository)
        
        input_data = UpdateUserInputData(
            user_id=2,
            admin_user_id=1,
            role="ADMIN"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert sample_target_user.role == UserRole.ADMIN
    
    def test_tc4_8_update_role_admin_to_customer_success(
        self,
        mock_user_repository,
        another_admin_user
    ):
        """TC4.8: Update role (ADMIN → CUSTOMER) - success"""
        # Arrange
        mock_user_repository.find_by_id.return_value = another_admin_user
        mock_user_repository.save.return_value = another_admin_user
        
        use_case = UpdateUserByAdminUseCase(mock_user_repository)
        
        input_data = UpdateUserInputData(
            user_id=3,
            admin_user_id=1,  # Different admin performing action
            role="CUSTOMER"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert another_admin_user.role == UserRole.CUSTOMER
    
    def test_tc4_9_update_is_active_true_to_false_success(
        self,
        mock_user_repository,
        sample_target_user
    ):
        """TC4.9: Update is_active (true → false) - success"""
        # Arrange
        mock_user_repository.find_by_id.return_value = sample_target_user
        mock_user_repository.save.return_value = sample_target_user
        
        use_case = UpdateUserByAdminUseCase(mock_user_repository)
        
        input_data = UpdateUserInputData(
            user_id=2,
            admin_user_id=1,
            is_active=False
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert sample_target_user.is_active is False
    
    def test_tc4_10_update_is_active_false_to_true_success(
        self,
        mock_user_repository,
        sample_target_user
    ):
        """TC4.10: Update is_active (false → true) - success"""
        # Arrange
        sample_target_user.deactivate()  # Start with inactive user
        mock_user_repository.find_by_id.return_value = sample_target_user
        mock_user_repository.save.return_value = sample_target_user
        
        use_case = UpdateUserByAdminUseCase(mock_user_repository)
        
        input_data = UpdateUserInputData(
            user_id=2,
            admin_user_id=1,
            is_active=True
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert sample_target_user.is_active is True
    
    # ========== ERROR CASES (TC4.11 - TC4.28) ==========
    
    def test_tc4_11_user_not_found_error(self, mock_user_repository):
        """TC4.11: User ID not found - error"""
        # Arrange
        mock_user_repository.find_by_id.return_value = None
        
        use_case = UpdateUserByAdminUseCase(mock_user_repository)
        
        input_data = UpdateUserInputData(
            user_id=999,
            admin_user_id=1,
            full_name="New Name"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "not found" in output.message.lower()
    
    def test_tc4_13_username_already_taken_error(
        self,
        mock_user_repository,
        sample_target_user
    ):
        """TC4.13: Username already taken by another user - error"""
        # Arrange
        mock_user_repository.find_by_id.return_value = sample_target_user
        mock_user_repository.exists_by_username.return_value = True
        
        use_case = UpdateUserByAdminUseCase(mock_user_repository)
        
        input_data = UpdateUserInputData(
            user_id=2,
            admin_user_id=1,
            username="taken_username"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "already exists" in output.message.lower() or "taken" in output.message.lower()
    
    def test_tc4_14_email_already_taken_error(
        self,
        mock_user_repository,
        sample_target_user
    ):
        """TC4.14: Email already taken by another user - error"""
        # Arrange
        mock_user_repository.find_by_id.return_value = sample_target_user
        mock_user_repository.exists_by_email.return_value = True
        
        use_case = UpdateUserByAdminUseCase(mock_user_repository)
        
        input_data = UpdateUserInputData(
            user_id=2,
            admin_user_id=1,
            email="taken@example.com"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "already exists" in output.message.lower() or "taken" in output.message.lower()
    
    def test_tc4_15_username_same_as_current_success(
        self,
        mock_user_repository,
        sample_target_user
    ):
        """TC4.15: Username same as current (no uniqueness check needed) - success"""
        # Arrange
        mock_user_repository.find_by_id.return_value = sample_target_user
        mock_user_repository.save.return_value = sample_target_user
        
        use_case = UpdateUserByAdminUseCase(mock_user_repository)
        
        input_data = UpdateUserInputData(
            user_id=2,
            admin_user_id=1,
            username="customer1"  # Same as current
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        # exists_by_username should NOT be called if username unchanged
    
    def test_tc4_16_email_same_as_current_success(
        self,
        mock_user_repository,
        sample_target_user
    ):
        """TC4.16: Email same as current (no uniqueness check needed) - success"""
        # Arrange
        mock_user_repository.find_by_id.return_value = sample_target_user
        mock_user_repository.save.return_value = sample_target_user
        
        use_case = UpdateUserByAdminUseCase(mock_user_repository)
        
        input_data = UpdateUserInputData(
            user_id=2,
            admin_user_id=1,
            email="customer1@example.com"  # Same as current
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
    
    def test_tc4_20_admin_tries_to_deactivate_self_error(
        self,
        mock_user_repository,
        sample_admin_user
    ):
        """TC4.20: Admin tries to deactivate self - error"""
        # Arrange
        mock_user_repository.find_by_id.return_value = sample_admin_user
        
        use_case = UpdateUserByAdminUseCase(mock_user_repository)
        
        input_data = UpdateUserInputData(
            user_id=1,
            admin_user_id=1,  # Same user
            is_active=False
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "cannot deactivate yourself" in output.message.lower()
    
    def test_tc4_21_admin_tries_to_demote_self_error(
        self,
        mock_user_repository,
        sample_admin_user
    ):
        """TC4.21: Admin tries to demote self - error"""
        # Arrange
        mock_user_repository.find_by_id.return_value = sample_admin_user
        
        use_case = UpdateUserByAdminUseCase(mock_user_repository)
        
        input_data = UpdateUserInputData(
            user_id=1,
            admin_user_id=1,  # Same user
            role="CUSTOMER"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "cannot change your own role" in output.message.lower()
    
    def test_tc4_22_admin_updates_another_admin_success(
        self,
        mock_user_repository,
        another_admin_user
    ):
        """TC4.22: Admin updates another admin - success"""
        # Arrange
        mock_user_repository.find_by_id.return_value = another_admin_user
        mock_user_repository.save.return_value = another_admin_user
        
        use_case = UpdateUserByAdminUseCase(mock_user_repository)
        
        input_data = UpdateUserInputData(
            user_id=3,
            admin_user_id=1,  # Different admin
            full_name="Updated Admin Name"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
    
    def test_tc4_23_admin_updates_customer_success(
        self,
        mock_user_repository,
        sample_target_user
    ):
        """TC4.23: Admin updates customer - success"""
        # Arrange
        mock_user_repository.find_by_id.return_value = sample_target_user
        mock_user_repository.save.return_value = sample_target_user
        
        use_case = UpdateUserByAdminUseCase(mock_user_repository)
        
        input_data = UpdateUserInputData(
            user_id=2,
            admin_user_id=1,
            full_name="Updated Customer Name"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
    
    def test_tc4_24_clear_phone_number_success(
        self,
        mock_user_repository,
        sample_target_user
    ):
        """TC4.24: Set phone_number to null (clear) - success"""
        # Arrange
        # Create a fresh copy to avoid side effects
        user_copy = User.reconstruct(
            user_id=sample_target_user.id,
            username=sample_target_user.username,
            email=sample_target_user.email,
            password_hash=sample_target_user.password_hash,
            full_name=sample_target_user.full_name,
            phone_number=sample_target_user.phone_number,
            address=sample_target_user.address,
            role=sample_target_user.role,
            is_active=sample_target_user.is_active,
            created_at=sample_target_user.created_at
        )
        mock_user_repository.find_by_id.return_value = user_copy
        # Mock save to return the user passed to it (reconstructed with None phone)
        mock_user_repository.save.side_effect = lambda user: user
        
        use_case = UpdateUserByAdminUseCase(mock_user_repository)
        
        input_data = UpdateUserInputData(
            user_id=2,
            admin_user_id=1,
            phone_number=""  # Empty string to clear
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert - check the saved user from mock
        assert output.success is True
        saved_user = mock_user_repository.save.call_args[0][0]
        assert saved_user.phone_number is None
    
    def test_tc4_25_clear_address_success(
        self,
        mock_user_repository,
        sample_target_user
    ):
        """TC4.25: Set address to null (clear) - success"""
        # Arrange
        # Create a fresh copy to avoid side effects
        user_copy = User.reconstruct(
            user_id=sample_target_user.id,
            username=sample_target_user.username,
            email=sample_target_user.email,
            password_hash=sample_target_user.password_hash,
            full_name=sample_target_user.full_name,
            phone_number=sample_target_user.phone_number,
            address=sample_target_user.address,
            role=sample_target_user.role,
            is_active=sample_target_user.is_active,
            created_at=sample_target_user.created_at
        )
        mock_user_repository.find_by_id.return_value = user_copy
        # Mock save to return the user passed to it
        mock_user_repository.save.side_effect = lambda user: user
        
        use_case = UpdateUserByAdminUseCase(mock_user_repository)
        
        input_data = UpdateUserInputData(
            user_id=2,
            admin_user_id=1,
            address=""  # Empty string to clear
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert - check the saved user from mock
        assert output.success is True
        saved_user = mock_user_repository.save.call_args[0][0]
        assert saved_user.address is None
    
    def test_tc4_28_password_hash_never_updated(
        self,
        mock_user_repository,
        sample_target_user
    ):
        """TC4.28: Verify password_hash never updated via this use case"""
        # Arrange
        original_password_hash = sample_target_user.password_hash
        mock_user_repository.find_by_id.return_value = sample_target_user
        mock_user_repository.save.return_value = sample_target_user
        
        use_case = UpdateUserByAdminUseCase(mock_user_repository)
        
        input_data = UpdateUserInputData(
            user_id=2,
            admin_user_id=1,
            full_name="New Name"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert sample_target_user.password_hash == original_password_hash
        assert "password_hash" not in output.__dict__
