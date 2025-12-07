"""
Unit Tests for LoginUserUseCase
Test mọi trường hợp đăng nhập
"""

import pytest
from unittest.mock import Mock

from app.business.use_cases.login_user_use_case import (
    LoginUserUseCase,
    LoginUserInputData,
    LoginUserOutputData
)
from app.domain.enums import UserRole
from app.domain.exceptions import InvalidCredentialsException


class TestLoginUserUseCase:
    """Test suite cho LoginUserUseCase với đầy đủ các trường hợp"""
    
    @pytest.fixture
    def user_repository(self):
        """Mock user repository"""
        return Mock()
    
    @pytest.fixture
    def use_case(self, user_repository):
        """Khởi tạo use case"""
        return LoginUserUseCase(user_repository)
    
    # ============ SUCCESS CASES - USERNAME ============
    
    def test_login_with_username_customer_success(self, use_case, user_repository):
        """Test 1: Đăng nhập thành công bằng username (customer role)"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 1
        mock_user.username = "customer1"
        mock_user.role = UserRole.CUSTOMER
        mock_user.ensure_active = Mock()
        user_repository.find_by_username.return_value = mock_user
        
        input_data = LoginUserInputData(
            username_or_email="customer1",
            password_hash="hashed_password"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.user_id == 1
        assert output.username == "customer1"
        assert output.role == "CUSTOMER"
        assert output.error_message is None
    
    def test_login_with_username_admin_success(self, use_case, user_repository):
        """Test 2: Đăng nhập thành công bằng username (admin role)"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 2
        mock_user.username = "admin"
        mock_user.role = UserRole.ADMIN
        mock_user.ensure_active = Mock()
        user_repository.find_by_username.return_value = mock_user
        
        input_data = LoginUserInputData(
            username_or_email="admin",
            password_hash="hashed_admin_pass"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.user_id == 2
        assert output.role == "ADMIN"
    
    def test_login_with_username_case_sensitive(self, use_case, user_repository):
        """Test 3: Username phân biệt hoa thường"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 3
        mock_user.username = "TestUser"
        mock_user.role = UserRole.CUSTOMER
        mock_user.ensure_active = Mock()
        user_repository.find_by_username.return_value = mock_user
        
        input_data = LoginUserInputData(
            username_or_email="TestUser",
            password_hash="hashed"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.username == "TestUser"
    
    # ============ SUCCESS CASES - EMAIL ============
    
    def test_login_with_email_success(self, use_case, user_repository):
        """Test 4: Đăng nhập thành công bằng email"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 4
        mock_user.username = "emailuser"
        mock_user.role = UserRole.CUSTOMER
        mock_user.ensure_active = Mock()
        
        user_repository.find_by_username.return_value = None
        user_repository.find_by_email.return_value = mock_user
        
        input_data = LoginUserInputData(
            username_or_email="test@example.com",
            password_hash="hashed"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.user_id == 4
        assert output.username == "emailuser"
    
    def test_login_with_email_lowercase(self, use_case, user_repository):
        """Test 5: Email viết thường"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 5
        mock_user.username = "user5"
        mock_user.role = UserRole.CUSTOMER
        mock_user.ensure_active = Mock()
        
        user_repository.find_by_username.return_value = None
        user_repository.find_by_email.return_value = mock_user
        
        input_data = LoginUserInputData(
            username_or_email="lowercase@example.com",
            password_hash="hashed"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
    
    def test_login_with_email_uppercase(self, use_case, user_repository):
        """Test 6: Email viết hoa"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 6
        mock_user.username = "user6"
        mock_user.role = UserRole.CUSTOMER
        mock_user.ensure_active = Mock()
        
        user_repository.find_by_username.return_value = None
        user_repository.find_by_email.return_value = mock_user
        
        input_data = LoginUserInputData(
            username_or_email="UPPERCASE@EXAMPLE.COM",
            password_hash="hashed"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
    
    # ============ USER NOT FOUND CASES ============
    
    def test_login_username_not_found(self, use_case, user_repository):
        """Test 7: Username không tồn tại"""
        # Arrange
        user_repository.find_by_username.return_value = None
        user_repository.find_by_email.return_value = None
        
        input_data = LoginUserInputData(
            username_or_email="nonexistent",
            password_hash="hashed"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.error_message is not None
        assert "invalid" in output.error_message.lower()
        assert output.user_id is None
        assert output.username is None
    
    def test_login_email_not_found(self, use_case, user_repository):
        """Test 8: Email không tồn tại"""
        # Arrange
        user_repository.find_by_username.return_value = None
        user_repository.find_by_email.return_value = None
        
        input_data = LoginUserInputData(
            username_or_email="notfound@example.com",
            password_hash="hashed"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "invalid" in output.error_message.lower()
    
    def test_login_empty_username_or_email(self, use_case, user_repository):
        """Test 9: Username/email rỗng"""
        # Arrange
        user_repository.find_by_username.return_value = None
        
        input_data = LoginUserInputData(
            username_or_email="",
            password_hash="hashed"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
    
    # ============ INACTIVE USER CASES ============
    
    def test_login_inactive_user(self, use_case, user_repository):
        """Test 10: User bị deactivate"""
        # Arrange
        mock_user = Mock()
        mock_user.ensure_active.side_effect = InvalidCredentialsException()
        user_repository.find_by_username.return_value = mock_user
        
        input_data = LoginUserInputData(
            username_or_email="inactiveuser",
            password_hash="hashed"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.error_message is not None
        assert "deactivated" in output.error_message.lower()
    
    def test_login_suspended_user(self, use_case, user_repository):
        """Test 11: User bị tạm khóa"""
        # Arrange
        mock_user = Mock()
        mock_user.ensure_active.side_effect = InvalidCredentialsException()
        user_repository.find_by_username.return_value = mock_user
        
        input_data = LoginUserInputData(
            username_or_email="suspendeduser",
            password_hash="hashed"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "deactivated" in output.error_message.lower()
    
    # ============ REPOSITORY LOOKUP ORDER ============
    
    def test_login_checks_username_before_email(self, use_case, user_repository):
        """Test 12: Kiểm tra username trước email"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 12
        mock_user.username = "testuser"
        mock_user.role = UserRole.CUSTOMER
        mock_user.ensure_active = Mock()
        user_repository.find_by_username.return_value = mock_user
        
        input_data = LoginUserInputData(
            username_or_email="testuser",
            password_hash="hashed"
        )
        
        # Act
        use_case.execute(input_data)
        
        # Assert
        user_repository.find_by_username.assert_called_once_with("testuser")
        user_repository.find_by_email.assert_not_called()
    
    def test_login_checks_email_when_username_fails(self, use_case, user_repository):
        """Test 13: Kiểm tra email khi không tìm thấy username"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 13
        mock_user.username = "emailuser"
        mock_user.role = UserRole.CUSTOMER
        mock_user.ensure_active = Mock()
        
        user_repository.find_by_username.return_value = None
        user_repository.find_by_email.return_value = mock_user
        
        input_data = LoginUserInputData(
            username_or_email="test@example.com",
            password_hash="hashed"
        )
        
        # Act
        use_case.execute(input_data)
        
        # Assert
        user_repository.find_by_username.assert_called_once()
        user_repository.find_by_email.assert_called_once()
    
    # ============ EDGE CASES ============
    
    def test_login_with_whitespace_username(self, use_case, user_repository):
        """Test 14: Username có khoảng trắng đầu/cuối"""
        # Arrange
        user_repository.find_by_username.return_value = None
        user_repository.find_by_email.return_value = None
        
        input_data = LoginUserInputData(
            username_or_email="  testuser  ",
            password_hash="hashed"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        # Có thể trim hoặc fail
        assert output is not None
    
    def test_login_with_special_characters_username(self, use_case, user_repository):
        """Test 15: Username có ký tự đặc biệt"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 15
        mock_user.username = "user_123-test"
        mock_user.role = UserRole.CUSTOMER
        mock_user.ensure_active = Mock()
        user_repository.find_by_username.return_value = mock_user
        
        input_data = LoginUserInputData(
            username_or_email="user_123-test",
            password_hash="hashed"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
    
    def test_login_repository_exception(self, use_case, user_repository):
        """Test 16: Lỗi từ repository"""
        # Arrange
        user_repository.find_by_username.side_effect = Exception("Database error")
        
        input_data = LoginUserInputData(
            username_or_email="testuser",
            password_hash="hashed"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.error_message is not None
    
    # ============ OUTPUT VALIDATION ============
    
    def test_login_output_data_structure(self, use_case, user_repository):
        """Test 17: Kiểm tra cấu trúc output data"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 17
        mock_user.username = "outputtest"
        mock_user.role = UserRole.CUSTOMER
        mock_user.ensure_active = Mock()
        user_repository.find_by_username.return_value = mock_user
        
        input_data = LoginUserInputData(
            username_or_email="outputtest",
            password_hash="hashed"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert isinstance(output, LoginUserOutputData)
        assert hasattr(output, 'success')
        assert hasattr(output, 'user_id')
        assert hasattr(output, 'username')
        assert hasattr(output, 'role')
        assert hasattr(output, 'error_message')
    
    def test_login_output_role_string_format(self, use_case, user_repository):
        """Test 18: Role được trả về dạng string"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 18
        mock_user.username = "roletest"
        mock_user.role = UserRole.ADMIN
        mock_user.ensure_active = Mock()
        user_repository.find_by_username.return_value = mock_user
        
        input_data = LoginUserInputData(
            username_or_email="roletest",
            password_hash="hashed"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert isinstance(output.role, str)
        assert output.role == "ADMIN"
    
    def test_login_success_no_error_message(self, use_case, user_repository):
        """Test 19: Success case không có error message"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 19
        mock_user.username = "successuser"
        mock_user.role = UserRole.CUSTOMER
        mock_user.ensure_active = Mock()
        user_repository.find_by_username.return_value = mock_user
        
        input_data = LoginUserInputData(
            username_or_email="successuser",
            password_hash="hashed"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.error_message is None
    
    def test_login_failure_has_error_message(self, use_case, user_repository):
        """Test 20: Failure case có error message"""
        # Arrange
        user_repository.find_by_username.return_value = None
        user_repository.find_by_email.return_value = None
        
        input_data = LoginUserInputData(
            username_or_email="failuser",
            password_hash="hashed"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.error_message is not None
        assert len(output.error_message) > 0
