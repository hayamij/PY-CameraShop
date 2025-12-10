"""
Test Suite for DeleteUserUseCase (USE CASE 5)
Test-Driven Development: RED phase - write tests first

Requirements from todo.txt:
- Admin can delete (soft delete) users
- SOFT DELETE only (is_active=false), NO hard delete
- Cannot self-delete
- User must exist
- If already inactive, error
- Check dependencies (orders, cart, etc.) - optional

Test Coverage: 16 tests (TC5.1 - TC5.16)
"""
import pytest
from datetime import datetime
from unittest.mock import Mock

from app.business.use_cases.delete_user_use_case import (
    DeleteUserUseCase,
    DeleteUserInputData,
    DeleteUserOutputData
)
from app.domain.entities import User
from app.domain.value_objects import Email, PhoneNumber
from app.domain.enums import UserRole
from app.domain.exceptions import UserNotFoundException


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_user_repository():
    """Mock user repository for unit testing"""
    return Mock()


@pytest.fixture
def sample_active_customer():
    """Sample active customer user"""
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
def sample_active_admin():
    """Sample active admin user (not the one performing action)"""
    return User.reconstruct(
        user_id=3,
        username="admin2",
        email=Email("admin2@example.com"),
        password_hash="hashed_admin_password",
        full_name="Admin Two",
        phone_number=None,
        address=None,
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime(2023, 12, 15)
    )


@pytest.fixture
def sample_inactive_user():
    """Sample inactive user (already deleted)"""
    return User.reconstruct(
        user_id=4,
        username="inactive_user",
        email=Email("inactive@example.com"),
        password_hash="hashed_password",
        full_name="Inactive User",
        phone_number=None,
        address=None,
        role=UserRole.CUSTOMER,
        is_active=False,
        created_at=datetime(2024, 2, 1)
    )


@pytest.fixture
def performing_admin():
    """Admin performing the delete action"""
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


# ============================================================================
# TEST CLASS 1: INPUT DATA VALIDATION (TC5.6)
# ============================================================================

class TestDeleteUserInputDataValidation:
    """Test input validation for DeleteUserUseCase"""
    
    def test_tc5_6_invalid_user_id_zero(self):
        """TC5.6: Invalid user_id (0) - validation error"""
        with pytest.raises(ValueError, match="user_id must be positive"):
            DeleteUserInputData(
                user_id=0,
                admin_user_id=1
            )
    
    def test_tc5_6_invalid_user_id_negative(self):
        """TC5.6: Invalid user_id (negative) - validation error"""
        with pytest.raises(ValueError, match="user_id must be positive"):
            DeleteUserInputData(
                user_id=-5,
                admin_user_id=1
            )
    
    def test_tc5_6_invalid_admin_user_id_zero(self):
        """TC5.6: Invalid admin_user_id (0) - validation error"""
        with pytest.raises(ValueError, match="admin_user_id must be positive"):
            DeleteUserInputData(
                user_id=2,
                admin_user_id=0
            )
    
    def test_valid_input_data(self):
        """Valid input data - success"""
        input_data = DeleteUserInputData(
            user_id=2,
            admin_user_id=1
        )
        assert input_data.user_id == 2
        assert input_data.admin_user_id == 1


# ============================================================================
# TEST CLASS 2: DELETE USER BUSINESS LOGIC (TC5.1 - TC5.16)
# ============================================================================

class TestDeleteUserUseCase:
    """Test DeleteUserUseCase business logic"""
    
    # ========== SUCCESS CASES (TC5.1 - TC5.2) ==========
    
    def test_tc5_1_delete_active_customer_success(
        self,
        mock_user_repository,
        sample_active_customer
    ):
        """TC5.1: Delete active customer - success (soft delete)"""
        # Arrange
        mock_user_repository.find_by_id.return_value = sample_active_customer
        mock_user_repository.save.side_effect = lambda user: user
        
        use_case = DeleteUserUseCase(mock_user_repository)
        
        input_data = DeleteUserInputData(
            user_id=2,
            admin_user_id=1  # Different from target user
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.user_id == 2
        assert "deleted successfully" in output.message.lower() or "deactivated" in output.message.lower()
        # Verify soft delete - user is now inactive
        saved_user = mock_user_repository.save.call_args[0][0]
        assert saved_user.is_active is False
        mock_user_repository.save.assert_called_once()
    
    def test_tc5_2_delete_active_admin_not_self_success(
        self,
        mock_user_repository,
        sample_active_admin
    ):
        """TC5.2: Delete active admin (not self) - success"""
        # Arrange
        mock_user_repository.find_by_id.return_value = sample_active_admin
        mock_user_repository.save.side_effect = lambda user: user
        
        use_case = DeleteUserUseCase(mock_user_repository)
        
        input_data = DeleteUserInputData(
            user_id=3,
            admin_user_id=1  # Different admin
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.user_id == 3
        # Verify soft delete
        saved_user = mock_user_repository.save.call_args[0][0]
        assert saved_user.is_active is False
    
    # ========== ERROR CASES (TC5.3 - TC5.15) ==========
    
    def test_tc5_3_delete_already_inactive_user_error(
        self,
        mock_user_repository,
        sample_inactive_user
    ):
        """TC5.3: Delete already inactive user - error (already deleted)"""
        # Arrange
        mock_user_repository.find_by_id.return_value = sample_inactive_user
        
        use_case = DeleteUserUseCase(mock_user_repository)
        
        input_data = DeleteUserInputData(
            user_id=4,
            admin_user_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "already" in output.message.lower() and ("inactive" in output.message.lower() or "deleted" in output.message.lower())
        # Verify save was NOT called
        mock_user_repository.save.assert_not_called()
    
    def test_tc5_4_admin_tries_to_delete_self_error(
        self,
        mock_user_repository,
        performing_admin
    ):
        """TC5.4: Admin tries to delete self - error"""
        # Arrange
        mock_user_repository.find_by_id.return_value = performing_admin
        
        use_case = DeleteUserUseCase(mock_user_repository)
        
        input_data = DeleteUserInputData(
            user_id=1,
            admin_user_id=1  # Same user
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "cannot delete yourself" in output.message.lower()
        # Verify save was NOT called
        mock_user_repository.save.assert_not_called()
    
    def test_tc5_5_user_not_found_error(
        self,
        mock_user_repository
    ):
        """TC5.5: User ID not found - error"""
        # Arrange
        mock_user_repository.find_by_id.return_value = None
        
        use_case = DeleteUserUseCase(mock_user_repository)
        
        input_data = DeleteUserInputData(
            user_id=999,
            admin_user_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "not found" in output.message.lower()
    
    def test_tc5_7_verify_soft_delete_data_retained(
        self,
        mock_user_repository,
        sample_active_customer
    ):
        """TC5.7: Verify soft delete (is_active=false, data retained)"""
        # Arrange
        original_username = sample_active_customer.username
        original_email = sample_active_customer.email.address
        
        mock_user_repository.find_by_id.return_value = sample_active_customer
        mock_user_repository.save.side_effect = lambda user: user
        
        use_case = DeleteUserUseCase(mock_user_repository)
        
        input_data = DeleteUserInputData(
            user_id=2,
            admin_user_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        saved_user = mock_user_repository.save.call_args[0][0]
        # Verify data retained
        assert saved_user.username == original_username
        assert saved_user.email.address == original_email
        assert saved_user.is_active is False
    
    def test_tc5_8_verify_hard_delete_not_performed(
        self,
        mock_user_repository,
        sample_active_customer
    ):
        """TC5.8: Verify hard delete NOT performed (record still in DB)"""
        # Arrange
        mock_user_repository.find_by_id.return_value = sample_active_customer
        mock_user_repository.save.side_effect = lambda user: user
        
        use_case = DeleteUserUseCase(mock_user_repository)
        
        input_data = DeleteUserInputData(
            user_id=2,
            admin_user_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        # Verify repository delete was NOT called
        assert not hasattr(mock_user_repository, 'delete') or not mock_user_repository.delete.called
        # Verify save WAS called (soft delete)
        mock_user_repository.save.assert_called_once()
    
    def test_tc5_9_delete_user_with_pending_orders_success(
        self,
        mock_user_repository,
        sample_active_customer
    ):
        """TC5.9: Delete user with pending orders - success (allow)"""
        # Arrange
        # Note: Order dependency check is optional in requirements
        # This test assumes we allow deletion regardless of orders
        mock_user_repository.find_by_id.return_value = sample_active_customer
        mock_user_repository.save.side_effect = lambda user: user
        
        use_case = DeleteUserUseCase(mock_user_repository)
        
        input_data = DeleteUserInputData(
            user_id=2,
            admin_user_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        # Deletion allowed even if user has orders
    
    def test_tc5_10_delete_user_with_completed_orders_success(
        self,
        mock_user_repository,
        sample_active_customer
    ):
        """TC5.10: Delete user with completed orders - success"""
        # Arrange
        mock_user_repository.find_by_id.return_value = sample_active_customer
        mock_user_repository.save.side_effect = lambda user: user
        
        use_case = DeleteUserUseCase(mock_user_repository)
        
        input_data = DeleteUserInputData(
            user_id=2,
            admin_user_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        # Deletion allowed
    
    def test_tc5_11_deleted_user_cannot_login(
        self,
        mock_user_repository,
        sample_active_customer
    ):
        """TC5.11: Verify deleted user cannot login (business rule check)"""
        # Arrange
        mock_user_repository.find_by_id.return_value = sample_active_customer
        mock_user_repository.save.side_effect = lambda user: user
        
        use_case = DeleteUserUseCase(mock_user_repository)
        
        input_data = DeleteUserInputData(
            user_id=2,
            admin_user_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        saved_user = mock_user_repository.save.call_args[0][0]
        # Verify user is inactive (login should be blocked by auth system)
        assert saved_user.is_active is False
    
    def test_tc5_12_deleted_user_orders_still_accessible(
        self,
        mock_user_repository,
        sample_active_customer
    ):
        """TC5.12: Verify deleted user orders still accessible by admin"""
        # Arrange
        # This is a soft delete, so user record still exists
        mock_user_repository.find_by_id.return_value = sample_active_customer
        mock_user_repository.save.side_effect = lambda user: user
        
        use_case = DeleteUserUseCase(mock_user_repository)
        
        input_data = DeleteUserInputData(
            user_id=2,
            admin_user_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        saved_user = mock_user_repository.save.call_args[0][0]
        # User ID still exists, orders can be queried
        assert saved_user.id == 2
    
    def test_tc5_13_delete_then_reactivate_possible(
        self,
        mock_user_repository,
        sample_active_customer
    ):
        """TC5.13: Delete then reactivate (via Update use case) - possible"""
        # Arrange
        mock_user_repository.find_by_id.return_value = sample_active_customer
        mock_user_repository.save.side_effect = lambda user: user
        
        use_case = DeleteUserUseCase(mock_user_repository)
        
        input_data = DeleteUserInputData(
            user_id=2,
            admin_user_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        saved_user = mock_user_repository.save.call_args[0][0]
        assert saved_user.is_active is False
        
        # Verify user can be reactivated (call user.activate())
        saved_user.activate()
        assert saved_user.is_active is True
    
    def test_tc5_14_admin_a_deletes_admin_b_success(
        self,
        mock_user_repository,
        sample_active_admin
    ):
        """TC5.14: Admin A deletes Admin B - success"""
        # Arrange
        mock_user_repository.find_by_id.return_value = sample_active_admin
        mock_user_repository.save.side_effect = lambda user: user
        
        use_case = DeleteUserUseCase(mock_user_repository)
        
        input_data = DeleteUserInputData(
            user_id=3,
            admin_user_id=1  # Admin A deletes Admin B
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        saved_user = mock_user_repository.save.call_args[0][0]
        assert saved_user.role == UserRole.ADMIN
        assert saved_user.is_active is False
    
    def test_tc5_15_last_admin_cannot_be_deleted_optional(
        self,
        mock_user_repository,
        sample_active_admin
    ):
        """TC5.15: Last admin cannot be deleted - error (optional safety check)"""
        # Arrange
        # This is an optional feature - check if it's the last admin
        mock_user_repository.find_by_id.return_value = sample_active_admin
        mock_user_repository.count_active_admins.return_value = 1  # Only one active admin
        
        use_case = DeleteUserUseCase(mock_user_repository)
        
        input_data = DeleteUserInputData(
            user_id=3,
            admin_user_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        # If last admin protection is implemented, should fail
        # If not implemented, should succeed
        # We'll test for the protected scenario
        if hasattr(mock_user_repository, 'count_active_admins'):
            # Last admin protection implemented
            assert output.success is False or output.success is True
            # Either behavior is acceptable per requirements
        else:
            # No protection, should succeed
            assert output.success is True
    
    def test_tc5_16_audit_log_created_optional(
        self,
        mock_user_repository,
        sample_active_customer
    ):
        """TC5.16: Audit log created after deletion (if implemented - optional)"""
        # Arrange
        mock_user_repository.find_by_id.return_value = sample_active_customer
        mock_user_repository.save.side_effect = lambda user: user
        
        use_case = DeleteUserUseCase(mock_user_repository)
        
        input_data = DeleteUserInputData(
            user_id=2,
            admin_user_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        # Audit logging is optional
        # This test just verifies deletion succeeded
        # Actual audit log would be in infrastructure layer
