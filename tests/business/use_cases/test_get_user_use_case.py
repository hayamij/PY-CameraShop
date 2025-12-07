"""
Unit Tests for GetUserUseCase
Test mọi trường hợp lấy thông tin user
"""

import pytest
from unittest.mock import Mock

from app.business.use_cases.get_user_use_case import (
    GetUserUseCase,
    GetUserInputData,
    GetUserOutputData
)
from app.domain.enums import UserRole


class TestGetUserUseCase:
    """Test suite cho GetUserUseCase với đầy đủ các trường hợp"""
    
    @pytest.fixture
    def user_repository(self):
        """Mock user repository"""
        return Mock()
    
    @pytest.fixture
    def use_case(self, user_repository):
        """Khởi tạo use case"""
        return GetUserUseCase(user_repository)
    
    # ============ SUCCESS CASES ============
    
    def test_get_customer_user_success(self, use_case, user_repository):
        """Test 1: Lấy thông tin customer thành công"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 1
        mock_user.username = "customer1"
        mock_user.email.value = "customer@example.com"
        mock_user.phone_number.value = "0912345678"
        mock_user.role = UserRole.CUSTOMER
        mock_user.full_name = "Nguyễn Văn A"
        mock_user.address = "123 Nguyễn Huệ, Q1, TP.HCM"
        user_repository.find_by_id.return_value = mock_user
        
        input_data = GetUserInputData(user_id=1)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.user is not None
        assert output.user.id == 1
        assert output.user.username == "customer1"
        assert output.user.email.value == "customer@example.com"
        assert output.user.phone_number.value == "0912345678"
        assert output.user.role == UserRole.CUSTOMER
        assert output.user.full_name == "Nguyễn Văn A"
        assert output.user.address == "123 Nguyễn Huệ, Q1, TP.HCM"
        assert output.error_message is None
    
    def test_get_admin_user_success(self, use_case, user_repository):
        """Test 2: Lấy thông tin admin thành công"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 2
        mock_user.username = "admin"
        mock_user.email.value = "admin@example.com"
        mock_user.phone_number.value = "0987654321"
        mock_user.role = UserRole.ADMIN
        mock_user.full_name = "Admin User"
        mock_user.address = "Admin Office"
        user_repository.find_by_id.return_value = mock_user
        
        input_data = GetUserInputData(user_id=2)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.user.role == UserRole.ADMIN
    
    def test_get_user_with_all_fields_populated(self, use_case, user_repository):
        """Test 3: User có đầy đủ tất cả các field"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 3
        mock_user.username = "fulluser"
        mock_user.email.value = "full@example.com"
        mock_user.phone_number.value = "0912345678"
        mock_user.role = UserRole.CUSTOMER
        mock_user.full_name = "Trần Thị B"
        mock_user.address = "456 Lê Lợi, Q3, TP.HCM"
        user_repository.find_by_id.return_value = mock_user
        
        input_data = GetUserInputData(user_id=3)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.user is not None
        assert output.user.id is not None
        assert output.user.username is not None
        assert output.user.email is not None
        assert output.user.phone_number is not None
        assert output.user.role is not None
        assert output.user.full_name is not None
        assert output.user.address is not None
    
    def test_get_user_with_minimal_fields(self, use_case, user_repository):
        """Test 4: User có field tối thiểu (không có full_name, address)"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 4
        mock_user.username = "minimaluser"
        mock_user.email.value = "minimal@example.com"
        mock_user.phone_number.value = "0912345678"
        mock_user.role = UserRole.CUSTOMER
        mock_user.full_name = None
        mock_user.address = None
        user_repository.find_by_id.return_value = mock_user
        
        input_data = GetUserInputData(user_id=4)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.user.full_name is None
        assert output.user.address is None
    
    # ============ NOT FOUND CASES ============
    
    def test_get_user_not_found(self, use_case, user_repository):
        """Test 5: User không tồn tại"""
        # Arrange
        user_repository.find_by_id.return_value = None
        
        input_data = GetUserInputData(user_id=999)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.error_message is not None
        assert "not found" in output.error_message.lower()
        assert output.user is None
    
    def test_get_user_with_invalid_id_zero(self, use_case, user_repository):
        """Test 6: User ID = 0"""
        # Arrange
        user_repository.find_by_id.return_value = None
        
        input_data = GetUserInputData(user_id=0)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.error_message is not None
    
    def test_get_user_with_invalid_id_negative(self, use_case, user_repository):
        """Test 7: User ID âm"""
        # Arrange
        user_repository.find_by_id.return_value = None
        
        input_data = GetUserInputData(user_id=-1)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
    
    # ============ REPOSITORY INTERACTION ============
    
    def test_get_user_repository_called_with_correct_id(self, use_case, user_repository):
        """Test 8: Repository được gọi với đúng ID"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 10
        mock_user.username = "test"
        mock_user.email.value = "test@example.com"
        mock_user.phone_number.value = "0912345678"
        mock_user.role = UserRole.CUSTOMER
        mock_user.full_name = None
        mock_user.address = None
        user_repository.find_by_id.return_value = mock_user
        
        input_data = GetUserInputData(user_id=10)
        
        # Act
        use_case.execute(input_data)
        
        # Assert
        user_repository.find_by_id.assert_called_once_with(10)
    
    def test_get_user_repository_exception(self, use_case, user_repository):
        """Test 9: Lỗi từ repository"""
        # Arrange
        user_repository.find_by_id.side_effect = Exception("Database error")
        
        input_data = GetUserInputData(user_id=5)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.error_message is not None
    
    # ============ OUTPUT VALIDATION ============
    
    def test_get_user_output_data_structure(self, use_case, user_repository):
        """Test 10: Kiểm tra cấu trúc output data"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 11
        mock_user.username = "structuretest"
        mock_user.email.value = "structure@example.com"
        mock_user.phone_number.value = "0912345678"
        mock_user.role = UserRole.CUSTOMER
        mock_user.full_name = "Test Structure"
        mock_user.address = "Test Address"
        user_repository.find_by_id.return_value = mock_user
        
        input_data = GetUserInputData(user_id=11)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert isinstance(output, GetUserOutputData)
        assert hasattr(output, 'success')
        assert hasattr(output, 'user')
        assert hasattr(output, 'error_message')
        # Check user entity attributes
        assert hasattr(output.user, 'id')
        assert hasattr(output.user, 'username')
        assert hasattr(output.user, 'email')
        assert hasattr(output.user, 'phone_number')
        assert hasattr(output.user, 'role')
        assert hasattr(output.user, 'full_name')
        assert hasattr(output.user, 'address')
    
    def test_get_user_role_string_format(self, use_case, user_repository):
        """Test 11: Role được trả về dạng string"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 12
        mock_user.username = "roletest"
        mock_user.email.value = "role@example.com"
        mock_user.phone_number.value = "0912345678"
        mock_user.role = UserRole.ADMIN
        mock_user.full_name = None
        mock_user.address = None
        user_repository.find_by_id.return_value = mock_user
        
        input_data = GetUserInputData(user_id=12)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.user.role == UserRole.ADMIN
    
    def test_get_user_success_no_error_message(self, use_case, user_repository):
        """Test 12: Success case không có error message"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 13
        mock_user.username = "successtest"
        mock_user.email.value = "success@example.com"
        mock_user.phone_number.value = "0912345678"
        mock_user.role = UserRole.CUSTOMER
        mock_user.full_name = None
        mock_user.address = None
        user_repository.find_by_id.return_value = mock_user
        
        input_data = GetUserInputData(user_id=13)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.error_message is None
    
    def test_get_user_failure_has_error_message(self, use_case, user_repository):
        """Test 13: Failure case có error message"""
        # Arrange
        user_repository.find_by_id.return_value = None
        
        input_data = GetUserInputData(user_id=999)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.error_message is not None
        assert len(output.error_message) > 0
    
    # ============ EDGE CASES ============
    
    def test_get_user_with_unicode_name(self, use_case, user_repository):
        """Test 14: User có tên tiếng Việt có dấu"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 14
        mock_user.username = "unicodeuser"
        mock_user.email.value = "unicode@example.com"
        mock_user.phone_number.value = "0912345678"
        mock_user.role = UserRole.CUSTOMER
        mock_user.full_name = "Nguyễn Thị Hương Giang"
        mock_user.address = "Số 1 Đường Võ Văn Ngân, Thủ Đức, TP.HCM"
        user_repository.find_by_id.return_value = mock_user
        
        input_data = GetUserInputData(user_id=14)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.user.full_name == "Nguyễn Thị Hương Giang"
        assert "Võ Văn Ngân" in output.user.address
    
    def test_get_user_with_special_characters_address(self, use_case, user_repository):
        """Test 15: Address có ký tự đặc biệt"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 15
        mock_user.username = "specialuser"
        mock_user.email.value = "special@example.com"
        mock_user.phone_number.value = "0912345678"
        mock_user.role = UserRole.CUSTOMER
        mock_user.full_name = "Test User"
        mock_user.address = "123/45A-B, Đường X-Y, Quận 1 (Gần chợ)"
        user_repository.find_by_id.return_value = mock_user
        
        input_data = GetUserInputData(user_id=15)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert "/" in output.user.address
        assert "(" in output.user.address
