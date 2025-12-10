"""
Test Cases for ChangeUserRoleUseCase

USE CASE 6: CHANGE USER ROLE (Admin promote/demote user)
Business Rules:
- Only admin can change roles
- Cannot self-change role
- User must exist and be active
- new_role must be ADMIN or CUSTOMER
- If new_role == old_role, error (no change)
- Promote: CUSTOMER → ADMIN
- Demote: ADMIN → CUSTOMER
- Optional: Last admin protection (cannot demote last admin)
"""
import pytest
from unittest.mock import Mock, MagicMock
from dataclasses import dataclass
from typing import Optional

from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.phone_number import PhoneNumber
from app.domain.enums import UserRole
from app.business.use_cases.change_user_role_use_case import (
    ChangeUserRoleUseCase,
    ChangeUserRoleInputData,
    ChangeUserRoleOutputData
)


# ==================== FIXTURES ====================

@pytest.fixture
def mock_user_repository():
    """Mock user repository"""
    return Mock()


@pytest.fixture
def sample_customer_user():
    """Active customer user"""
    from datetime import datetime
    user = User.reconstruct(
        user_id=10,
        username="customer1",
        email=Email("customer1@example.com"),
        password_hash="hashed_password",
        full_name="John Customer",
        phone_number=PhoneNumber("0901234567"),
        address="123 Customer St",
        role=UserRole.CUSTOMER,
        is_active=True,
        created_at=datetime(2024, 1, 1)
    )
    return user


@pytest.fixture
def sample_admin_user():
    """Active admin user"""
    from datetime import datetime
    user = User.reconstruct(
        user_id=20,
        username="admin1",
        email=Email("admin1@example.com"),
        password_hash="hashed_password",
        full_name="Admin One",
        phone_number=PhoneNumber("0912345678"),
        address="456 Admin Ave",
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime(2024, 1, 1)
    )
    return user


@pytest.fixture
def sample_inactive_user():
    """Inactive customer user"""
    from datetime import datetime
    user = User.reconstruct(
        user_id=30,
        username="inactive1",
        email=Email("inactive@example.com"),
        password_hash="hashed_password",
        full_name="Inactive User",
        phone_number=None,
        address=None,
        role=UserRole.CUSTOMER,
        is_active=False,
        created_at=datetime(2024, 1, 1)
    )
    return user


@pytest.fixture
def performing_admin():
    """Admin performing the role change"""
    from datetime import datetime
    user = User.reconstruct(
        user_id=1,
        username="super_admin",
        email=Email("super@example.com"),
        password_hash="hashed_password",
        full_name="Super Admin",
        phone_number=PhoneNumber("0900000000"),
        address="1 Admin Tower",
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime(2024, 1, 1)
    )
    return user


# ==================== INPUT VALIDATION TESTS ====================

class TestChangeUserRoleInputDataValidation:
    """Test input data validation"""
    
    def test_tc6_5_invalid_user_id_zero(self):
        """TC6.5: Invalid user_id (zero) - validation error"""
        with pytest.raises(ValueError, match="user_id must be a positive integer"):
            ChangeUserRoleInputData(
                user_id=0,
                new_role="ADMIN",
                admin_user_id=1
            )
    
    def test_tc6_5_invalid_user_id_negative(self):
        """TC6.5: Invalid user_id (negative) - validation error"""
        with pytest.raises(ValueError, match="user_id must be a positive integer"):
            ChangeUserRoleInputData(
                user_id=-5,
                new_role="CUSTOMER",
                admin_user_id=1
            )
    
    def test_tc6_5_invalid_admin_user_id_zero(self):
        """TC6.5: Invalid admin_user_id (zero) - validation error"""
        with pytest.raises(ValueError, match="admin_user_id must be a positive integer"):
            ChangeUserRoleInputData(
                user_id=10,
                new_role="ADMIN",
                admin_user_id=0
            )
    
    def test_tc6_6_invalid_new_role(self):
        """TC6.6: Invalid new_role (not ADMIN/CUSTOMER) - validation error"""
        with pytest.raises(ValueError, match="new_role must be 'ADMIN' or 'CUSTOMER'"):
            ChangeUserRoleInputData(
                user_id=10,
                new_role="SUPERUSER",
                admin_user_id=1
            )
    
    def test_tc6_11_case_insensitive_role_admin(self):
        """TC6.11: Case-insensitive role ('admin' → ADMIN) - success"""
        input_data = ChangeUserRoleInputData(
            user_id=10,
            new_role="admin",  # lowercase
            admin_user_id=1
        )
        assert input_data.new_role == "ADMIN"
    
    def test_tc6_11_case_insensitive_role_customer(self):
        """TC6.11: Case-insensitive role ('customer' → CUSTOMER) - success"""
        input_data = ChangeUserRoleInputData(
            user_id=10,
            new_role="CuStOmEr",  # mixed case
            admin_user_id=1
        )
        assert input_data.new_role == "CUSTOMER"
    
    def test_valid_input_data(self):
        """Valid input data should be created successfully"""
        input_data = ChangeUserRoleInputData(
            user_id=10,
            new_role="ADMIN",
            admin_user_id=1
        )
        assert input_data.user_id == 10
        assert input_data.new_role == "ADMIN"
        assert input_data.admin_user_id == 1


# ==================== USE CASE BUSINESS LOGIC TESTS ====================

class TestChangeUserRoleUseCase:
    """Test ChangeUserRoleUseCase business logic"""
    
    def test_tc6_1_promote_customer_to_admin_success(
        self, mock_user_repository, sample_customer_user, performing_admin
    ):
        """TC6.1: Promote CUSTOMER to ADMIN - success"""
        # Setup
        mock_user_repository.find_by_id.return_value = sample_customer_user
        mock_user_repository.save.side_effect = lambda user: user
        
        use_case = ChangeUserRoleUseCase(mock_user_repository)
        input_data = ChangeUserRoleInputData(
            user_id=10,
            new_role="ADMIN",
            admin_user_id=1
        )
        
        # Execute
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.user_id == 10
        assert output.old_role == "CUSTOMER"
        assert output.new_role == "ADMIN"
        assert "promoted to admin" in output.message.lower()
        mock_user_repository.save.assert_called_once()
        
        # Verify domain method called (user role changed)
        assert sample_customer_user.role == UserRole.ADMIN
    
    def test_tc6_2_demote_admin_to_customer_success(
        self, mock_user_repository, sample_admin_user, performing_admin
    ):
        """TC6.2: Demote ADMIN to CUSTOMER - success"""
        # Setup
        mock_user_repository.find_by_id.return_value = sample_admin_user
        mock_user_repository.count_by_role.return_value = 2  # Multiple admins exist
        mock_user_repository.save.side_effect = lambda user: user
        
        use_case = ChangeUserRoleUseCase(mock_user_repository)
        input_data = ChangeUserRoleInputData(
            user_id=20,
            new_role="CUSTOMER",
            admin_user_id=1
        )
        
        # Execute
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.user_id == 20
        assert output.old_role == "ADMIN"
        assert output.new_role == "CUSTOMER"
        assert "demoted to customer" in output.message.lower()
        mock_user_repository.save.assert_called_once()
        
        # Verify domain method called
        assert sample_admin_user.role == UserRole.CUSTOMER
    
    def test_tc6_3_admin_tries_to_change_own_role_error(
        self, mock_user_repository, performing_admin
    ):
        """TC6.3: Admin tries to change own role - error"""
        # Setup
        mock_user_repository.find_by_id.return_value = performing_admin
        
        use_case = ChangeUserRoleUseCase(mock_user_repository)
        input_data = ChangeUserRoleInputData(
            user_id=1,  # Same as admin_user_id
            new_role="CUSTOMER",
            admin_user_id=1
        )
        
        # Execute
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.user_id is None
        assert "cannot change your own role" in output.message.lower()
        mock_user_repository.save.assert_not_called()
    
    def test_tc6_4_user_id_not_found_error(
        self, mock_user_repository
    ):
        """TC6.4: User ID not found - error"""
        # Setup
        mock_user_repository.find_by_id.return_value = None
        
        use_case = ChangeUserRoleUseCase(mock_user_repository)
        input_data = ChangeUserRoleInputData(
            user_id=999,
            new_role="ADMIN",
            admin_user_id=1
        )
        
        # Execute
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.user_id is None
        assert "user not found" in output.message.lower()
        mock_user_repository.save.assert_not_called()
    
    def test_tc6_7_new_role_same_as_current_role_error(
        self, mock_user_repository, sample_admin_user
    ):
        """TC6.7: new_role same as current role - error (no change)"""
        # Setup
        mock_user_repository.find_by_id.return_value = sample_admin_user
        
        use_case = ChangeUserRoleUseCase(mock_user_repository)
        input_data = ChangeUserRoleInputData(
            user_id=20,
            new_role="ADMIN",  # Already ADMIN
            admin_user_id=1
        )
        
        # Execute
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.user_id is None
        assert "already has role ADMIN" in output.message
        mock_user_repository.save.assert_not_called()
    
    def test_tc6_8_promote_inactive_user_error(
        self, mock_user_repository, sample_inactive_user
    ):
        """TC6.8: Promote inactive user - error (must be active)"""
        # Setup
        mock_user_repository.find_by_id.return_value = sample_inactive_user
        
        use_case = ChangeUserRoleUseCase(mock_user_repository)
        input_data = ChangeUserRoleInputData(
            user_id=30,
            new_role="ADMIN",
            admin_user_id=1
        )
        
        # Execute
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.user_id is None
        assert "inactive user" in output.message.lower() or "must be active" in output.message.lower()
        mock_user_repository.save.assert_not_called()
    
    def test_tc6_9_promote_already_admin_user_error(
        self, mock_user_repository, sample_admin_user
    ):
        """TC6.9: Promote already ADMIN user - error"""
        # Setup (user is already ADMIN)
        mock_user_repository.find_by_id.return_value = sample_admin_user
        
        use_case = ChangeUserRoleUseCase(mock_user_repository)
        input_data = ChangeUserRoleInputData(
            user_id=20,
            new_role="ADMIN",
            admin_user_id=1
        )
        
        # Execute
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "already has role ADMIN" in output.message
        mock_user_repository.save.assert_not_called()
    
    def test_tc6_10_demote_already_customer_user_error(
        self, mock_user_repository, sample_customer_user
    ):
        """TC6.10: Demote already CUSTOMER user - error"""
        # Setup (user is already CUSTOMER)
        mock_user_repository.find_by_id.return_value = sample_customer_user
        
        use_case = ChangeUserRoleUseCase(mock_user_repository)
        input_data = ChangeUserRoleInputData(
            user_id=10,
            new_role="CUSTOMER",
            admin_user_id=1
        )
        
        # Execute
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "already has role CUSTOMER" in output.message
        mock_user_repository.save.assert_not_called()
    
    def test_tc6_12_demote_last_admin_in_system_error_optional(
        self, mock_user_repository, sample_admin_user
    ):
        """TC6.12: Demote last admin in system - error (safety check)"""
        # Setup
        mock_user_repository.find_by_id.return_value = sample_admin_user
        mock_user_repository.count_by_role.return_value = 1  # Only 1 admin
        
        use_case = ChangeUserRoleUseCase(mock_user_repository)
        input_data = ChangeUserRoleInputData(
            user_id=20,
            new_role="CUSTOMER",
            admin_user_id=1
        )
        
        # Execute
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.user_id is None
        assert "last admin" in output.message.lower() or "at least one admin" in output.message.lower()
        mock_user_repository.save.assert_not_called()
    
    def test_tc6_13_multiple_admins_exist_demote_one_success(
        self, mock_user_repository, sample_admin_user
    ):
        """TC6.13: Multiple admins exist, demote one - success"""
        # Setup
        mock_user_repository.find_by_id.return_value = sample_admin_user
        mock_user_repository.count_by_role.return_value = 3  # 3 admins exist
        mock_user_repository.save.side_effect = lambda user: user
        
        use_case = ChangeUserRoleUseCase(mock_user_repository)
        input_data = ChangeUserRoleInputData(
            user_id=20,
            new_role="CUSTOMER",
            admin_user_id=1
        )
        
        # Execute
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.user_id == 20
        assert output.old_role == "ADMIN"
        assert output.new_role == "CUSTOMER"
        mock_user_repository.save.assert_called_once()
    
    def test_tc6_14_verify_promote_to_admin_method_called(
        self, mock_user_repository, sample_customer_user
    ):
        """TC6.14: Verify User.promote_to_admin() called"""
        # Setup
        mock_user_repository.find_by_id.return_value = sample_customer_user
        mock_user_repository.save.side_effect = lambda user: user
        
        use_case = ChangeUserRoleUseCase(mock_user_repository)
        input_data = ChangeUserRoleInputData(
            user_id=10,
            new_role="ADMIN",
            admin_user_id=1
        )
        
        # Execute
        output = use_case.execute(input_data)
        
        # Assert domain method was called (role changed to ADMIN)
        assert sample_customer_user.role == UserRole.ADMIN
        assert output.success is True
    
    def test_tc6_15_verify_demote_to_customer_method_called(
        self, mock_user_repository, sample_admin_user
    ):
        """TC6.15: Verify User.demote_to_customer() called"""
        # Setup
        mock_user_repository.find_by_id.return_value = sample_admin_user
        mock_user_repository.count_by_role.return_value = 2  # Multiple admins
        mock_user_repository.save.side_effect = lambda user: user
        
        use_case = ChangeUserRoleUseCase(mock_user_repository)
        input_data = ChangeUserRoleInputData(
            user_id=20,
            new_role="CUSTOMER",
            admin_user_id=1
        )
        
        # Execute
        output = use_case.execute(input_data)
        
        # Assert domain method was called (role changed to CUSTOMER)
        assert sample_admin_user.role == UserRole.CUSTOMER
        assert output.success is True
    
    def test_tc6_16_role_change_reflected_in_database(
        self, mock_user_repository, sample_customer_user
    ):
        """TC6.16: Role change reflected in database"""
        # Setup
        saved_user = None
        def save_side_effect(user):
            nonlocal saved_user
            saved_user = user
            return user
        
        mock_user_repository.find_by_id.return_value = sample_customer_user
        mock_user_repository.save.side_effect = save_side_effect
        
        use_case = ChangeUserRoleUseCase(mock_user_repository)
        input_data = ChangeUserRoleInputData(
            user_id=10,
            new_role="ADMIN",
            admin_user_id=1
        )
        
        # Execute
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert saved_user is not None
        assert saved_user.role == UserRole.ADMIN
        assert saved_user.id == 10
        mock_user_repository.save.assert_called_once()
    
    def test_exception_handling_during_save(
        self, mock_user_repository, sample_customer_user
    ):
        """Test exception handling during repository save"""
        # Setup
        mock_user_repository.find_by_id.return_value = sample_customer_user
        mock_user_repository.save.side_effect = Exception("Database error")
        
        use_case = ChangeUserRoleUseCase(mock_user_repository)
        input_data = ChangeUserRoleInputData(
            user_id=10,
            new_role="ADMIN",
            admin_user_id=1
        )
        
        # Execute
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.user_id is None
        assert "error" in output.message.lower()
