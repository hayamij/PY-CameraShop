"""
Unit Tests for RegisterUserUseCase
Test mọi trường hợp input và validation
"""

import pytest
from unittest.mock import Mock
from werkzeug.security import generate_password_hash

from app.business.use_cases.register_user_use_case import (
    RegisterUserUseCase,
    RegisterUserInputData,
    RegisterUserOutputData
)
from app.domain.exceptions import UserAlreadyExistsException


class TestRegisterUserUseCase:
    """Test suite cho RegisterUserUseCase với đầy đủ các trường hợp"""
    
    @pytest.fixture
    def user_repository(self):
        """Mock user repository"""
        return Mock()
    
    @pytest.fixture
    def use_case(self, user_repository):
        """Khởi tạo use case"""
        return RegisterUserUseCase(user_repository)
    
    # ============ SUCCESS CASES ============
    
    def test_register_user_with_all_fields_success(self, use_case, user_repository):
        """Test 1: Đăng ký thành công với đầy đủ thông tin"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 1
        user_repository.save.return_value = mock_user
        
        input_data = RegisterUserInputData(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("Password123!"),
            full_name="Test User",
            phone_number="0123456789",
            address="123 Test Street, Hanoi"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.user_id == 1
        assert output.error_message is None
        user_repository.save.assert_called_once()
    
    def test_register_user_with_minimum_fields_success(self, use_case, user_repository):
        """Test 2: Đăng ký thành công với thông tin tối thiểu (không có phone, address)"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 2
        user_repository.save.return_value = mock_user
        
        input_data = RegisterUserInputData(
            username="minimumuser",
            email="minimum@example.com",
            password_hash=generate_password_hash("Pass1234!"),
            full_name="Minimum User"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.user_id == 2
        assert output.error_message is None
    
    def test_register_user_with_phone_only_success(self, use_case, user_repository):
        """Test 3: Đăng ký với phone number (không có address)"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 3
        user_repository.save.return_value = mock_user
        
        input_data = RegisterUserInputData(
            username="phoneuser",
            email="phone@example.com",
            password_hash=generate_password_hash("Password123!"),
            full_name="Phone User",
            phone_number="0987654321"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.user_id == 3
    
    def test_register_user_with_address_only_success(self, use_case, user_repository):
        """Test 4: Đăng ký với address (không có phone)"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 4
        user_repository.save.return_value = mock_user
        
        input_data = RegisterUserInputData(
            username="addressuser",
            email="address@example.com",
            password_hash=generate_password_hash("Password123!"),
            full_name="Address User",
            address="456 Another Street"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.user_id == 4
    
    # ============ EMAIL VALIDATION CASES ============
    
    def test_register_user_invalid_email_no_at_sign(self, use_case):
        """Test 5: Email không có @"""
        # Arrange
        input_data = RegisterUserInputData(
            username="testuser",
            email="invalidemail.com",
            password_hash=generate_password_hash("Password123!"),
            full_name="Test User"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.error_message is not None
        assert output.user_id is None
    
    def test_register_user_invalid_email_no_domain(self, use_case):
        """Test 6: Email không có domain"""
        # Arrange
        input_data = RegisterUserInputData(
            username="testuser",
            email="test@",
            password_hash=generate_password_hash("Password123!"),
            full_name="Test User"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.error_message is not None
    
    def test_register_user_invalid_email_spaces(self, use_case):
        """Test 7: Email có khoảng trắng"""
        # Arrange
        input_data = RegisterUserInputData(
            username="testuser",
            email="test user@example.com",
            password_hash=generate_password_hash("Password123!"),
            full_name="Test User"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.error_message is not None
    
    def test_register_user_invalid_email_special_chars(self, use_case):
        """Test 8: Email có ký tự đặc biệt không hợp lệ"""
        # Arrange
        input_data = RegisterUserInputData(
            username="testuser",
            email="test!#$%@example.com",
            password_hash=generate_password_hash("Password123!"),
            full_name="Test User"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.error_message is not None
    
    def test_register_user_empty_email(self, use_case):
        """Test 9: Email rỗng"""
        # Arrange
        input_data = RegisterUserInputData(
            username="testuser",
            email="",
            password_hash=generate_password_hash("Password123!"),
            full_name="Test User"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.error_message is not None
    
    # ============ PHONE NUMBER VALIDATION CASES ============
    
    def test_register_user_invalid_phone_too_short(self, use_case):
        """Test 10: Số điện thoại quá ngắn"""
        # Arrange
        input_data = RegisterUserInputData(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("Password123!"),
            full_name="Test User",
            phone_number="012345"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.error_message is not None
    
    def test_register_user_invalid_phone_too_long(self, use_case):
        """Test 11: Số điện thoại quá dài"""
        # Arrange
        input_data = RegisterUserInputData(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("Password123!"),
            full_name="Test User",
            phone_number="012345678901234"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.error_message is not None
    
    def test_register_user_invalid_phone_not_start_with_zero(self, use_case):
        """Test 12: Số điện thoại không bắt đầu bằng 0"""
        # Arrange
        input_data = RegisterUserInputData(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("Password123!"),
            full_name="Test User",
            phone_number="1234567890"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.error_message is not None
    
    def test_register_user_invalid_phone_contains_letters(self, use_case):
        """Test 13: Số điện thoại chứa chữ cái"""
        # Arrange
        input_data = RegisterUserInputData(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("Password123!"),
            full_name="Test User",
            phone_number="012345abcd"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.error_message is not None
    
    def test_register_user_invalid_phone_contains_special_chars(self, use_case):
        """Test 14: Số điện thoại chứa ký tự đặc biệt"""
        # Arrange
        input_data = RegisterUserInputData(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("Password123!"),
            full_name="Test User",
            phone_number="0123@456#789"  # Use clearly invalid characters
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.error_message is not None
    
    def test_register_user_valid_phone_all_providers(self, use_case, user_repository):
        """Test 15: Số điện thoại hợp lệ của các nhà mạng VN"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 5
        user_repository.save.return_value = mock_user
        
        valid_phones = [
            "0912345678",  # Viettel
            "0987654321",  # Viettel
            "0812345678",  # Vinaphone
            "0762345678",  # Mobifone
        ]
        
        for phone in valid_phones:
            input_data = RegisterUserInputData(
                username=f"user_{phone}",
                email=f"{phone}@example.com",
                password_hash=generate_password_hash("Password123!"),
                full_name="Test User",
                phone_number=phone
            )
            
            # Act
            output = use_case.execute(input_data)
            
            # Assert
            assert output.success is True
    
    # ============ DUPLICATE USER CASES ============
    
    def test_register_user_duplicate_email(self, use_case, user_repository):
        """Test 16: Email đã tồn tại"""
        # Arrange
        user_repository.save.side_effect = UserAlreadyExistsException("email test@example.com")
        
        input_data = RegisterUserInputData(
            username="newuser",
            email="test@example.com",
            password_hash=generate_password_hash("Password123!"),
            full_name="New User"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.error_message is not None
        assert "exists" in output.error_message.lower()
        assert output.user_id is None
    
    def test_register_user_duplicate_username(self, use_case, user_repository):
        """Test 17: Username đã tồn tại"""
        # Arrange
        user_repository.save.side_effect = UserAlreadyExistsException("username testuser")
        
        input_data = RegisterUserInputData(
            username="testuser",
            email="newemail@example.com",
            password_hash=generate_password_hash("Password123!"),
            full_name="New User"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "exists" in output.error_message.lower()
    
    # ============ REPOSITORY ERROR CASES ============
    
    def test_register_user_repository_generic_error(self, use_case, user_repository):
        """Test 18: Lỗi không xác định từ repository"""
        # Arrange
        user_repository.save.side_effect = Exception("Database connection failed")
        
        input_data = RegisterUserInputData(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("Password123!"),
            full_name="Test User"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.error_message is not None
        assert output.user_id is None
    
    # ============ EDGE CASES ============
    
    def test_register_user_with_very_long_username(self, use_case, user_repository):
        """Test 19: Username rất dài"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 6
        user_repository.save.return_value = mock_user
        
        long_username = "a" * 100
        input_data = RegisterUserInputData(
            username=long_username,
            email="test@example.com",
            password_hash=generate_password_hash("Password123!"),
            full_name="Test User"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert - Có thể success hoặc fail tùy validation
        # Chỉ cần không crash
        assert output is not None
    
    def test_register_user_with_unicode_full_name(self, use_case, user_repository):
        """Test 20: Tên có ký tự Unicode (tiếng Việt)"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 7
        user_repository.save.return_value = mock_user
        
        input_data = RegisterUserInputData(
            username="vietnameseuser",
            email="vietnamese@example.com",
            password_hash=generate_password_hash("Password123!"),
            full_name="Nguyễn Văn Tèo"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.user_id == 7
    
    def test_register_user_with_special_chars_in_address(self, use_case, user_repository):
        """Test 21: Địa chỉ có ký tự đặc biệt"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 8
        user_repository.save.return_value = mock_user
        
        input_data = RegisterUserInputData(
            username="specialuser",
            email="special@example.com",
            password_hash=generate_password_hash("Password123!"),
            full_name="Special User",
            address="123/45-B, Đường Láng, P.Láng Hạ, Q.Đống Đa, Hà Nội"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
    
    def test_register_user_output_data_structure(self, use_case, user_repository):
        """Test 22: Kiểm tra cấu trúc output data"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 9
        user_repository.save.return_value = mock_user
        
        input_data = RegisterUserInputData(
            username="structuretest",
            email="structure@example.com",
            password_hash=generate_password_hash("Password123!"),
            full_name="Structure Test"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert isinstance(output, RegisterUserOutputData)
        assert hasattr(output, 'success')
        assert hasattr(output, 'user_id')
        assert hasattr(output, 'error_message')
        assert isinstance(output.success, bool)
