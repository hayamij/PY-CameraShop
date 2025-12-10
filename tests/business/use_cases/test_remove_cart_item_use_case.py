"""
Unit Tests for RemoveCartItemUseCase
Test mọi trường hợp xóa sản phẩm khỏi giỏ hàng - chi tiết và đáng tin cậy
"""

import pytest
from unittest.mock import Mock

from app.business.use_cases.remove_cart_item_use_case import (
    RemoveCartItemUseCase,
    RemoveCartItemInputData,
    RemoveCartItemOutputData
)
from app.domain.exceptions import (
    CartItemNotFoundException,
    ValidationException
)


class TestRemoveCartItemUseCase:
    """Test suite cho RemoveCartItemUseCase - test kỹ lưỡng mọi trường hợp"""
    
    @pytest.fixture
    def cart_repository(self):
        """Mock cart repository"""
        return Mock()
    
    @pytest.fixture
    def use_case(self, cart_repository):
        """Khởi tạo use case"""
        return RemoveCartItemUseCase(cart_repository)
    
    def create_mock_cart_item(self, cart_item_id, cart_id, product_id, quantity):
        """Helper tạo mock cart item"""
        item = Mock()
        item.cart_item_id = cart_item_id
        item.cart_id = cart_id
        item.product_id = product_id
        item.quantity = quantity
        return item
    
    def create_mock_cart(self, cart_id, user_id):
        """Helper tạo mock cart"""
        cart = Mock()
        cart.id = cart_id  # Changed from cart.cart_id to cart.id
        cart.user_id = user_id
        return cart
    
    # ============ SUCCESS CASES ============
    
    def test_remove_cart_item_success(self, use_case, cart_repository):
        """Test 1: Xóa item thành công"""
        # Arrange
        user_id = 1
        cart_item_id = 5
        
        cart_item = self.create_mock_cart_item(cart_item_id, 1, 10, 2)
        cart_repository.find_cart_item_by_id.return_value = cart_item
        
        cart = self.create_mock_cart(1, user_id)
        cart_repository.find_by_user_id.return_value = cart
        
        input_data = RemoveCartItemInputData(user_id=user_id, cart_item_id=cart_item_id)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert "Item removed from cart successfully" in output.message
        assert output.error_message == ""
        
        cart_repository.remove_cart_item.assert_called_once_with(cart_item_id)
    
    def test_remove_last_item_from_cart_success(self, use_case, cart_repository):
        """Test 2: Xóa item cuối cùng trong giỏ"""
        # Arrange
        cart_item = self.create_mock_cart_item(1, 1, 10, 1)
        cart_repository.find_cart_item_by_id.return_value = cart_item
        
        cart = self.create_mock_cart(1, 1)
        cart_repository.find_by_user_id.return_value = cart
        
        input_data = RemoveCartItemInputData(user_id=1, cart_item_id=1)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        cart_repository.remove_cart_item.assert_called_once_with(1)
    
    def test_remove_one_of_multiple_items_success(self, use_case, cart_repository):
        """Test 3: Xóa 1 item trong giỏ có nhiều items"""
        # Arrange
        cart_item = self.create_mock_cart_item(2, 1, 20, 3)
        cart_repository.find_cart_item_by_id.return_value = cart_item
        
        cart = self.create_mock_cart(1, 1)
        cart_repository.find_by_user_id.return_value = cart
        
        input_data = RemoveCartItemInputData(user_id=1, cart_item_id=2)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        cart_repository.remove_cart_item.assert_called_once_with(2)
    
    # ============ CART ITEM NOT FOUND ============
    
    def test_remove_nonexistent_cart_item_fails(self, use_case, cart_repository):
        """Test 4: Xóa cart item không tồn tại"""
        # Arrange
        cart_repository.find_cart_item_by_id.return_value = None
        
        input_data = RemoveCartItemInputData(user_id=1, cart_item_id=999)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Cart item with ID 999 not found" in output.error_message
        cart_repository.remove_cart_item.assert_not_called()
    
    # ============ CART OWNERSHIP VALIDATION ============
    
    def test_remove_cart_item_not_belonging_to_user_fails(self, use_case, cart_repository):
        """Test 5: Xóa cart item không thuộc về user"""
        # Arrange
        cart_item = self.create_mock_cart_item(1, 10, 5, 2)  # belongs to cart_id=10
        cart_repository.find_cart_item_by_id.return_value = cart_item
        
        # User's cart is cart_id=1, but item belongs to cart_id=10
        user_cart = self.create_mock_cart(1, 1)
        cart_repository.find_by_user_id.return_value = user_cart
        
        input_data = RemoveCartItemInputData(user_id=1, cart_item_id=1)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "This cart item does not belong to you" in output.error_message
        cart_repository.remove_cart_item.assert_not_called()
    
    def test_remove_cart_item_user_has_no_cart_fails(self, use_case, cart_repository):
        """Test 6: User không có cart"""
        # Arrange
        cart_item = self.create_mock_cart_item(1, 1, 5, 2)
        cart_repository.find_cart_item_by_id.return_value = cart_item
        
        # User has no cart
        cart_repository.find_by_user_id.return_value = None
        
        input_data = RemoveCartItemInputData(user_id=1, cart_item_id=1)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "This cart item does not belong to you" in output.error_message
        cart_repository.remove_cart_item.assert_not_called()
    
    def test_remove_cart_item_from_another_users_cart_fails(self, use_case, cart_repository):
        """Test 7: Xóa item từ giỏ của user khác"""
        # Arrange
        cart_item = self.create_mock_cart_item(1, 5, 10, 2)  # belongs to cart_id=5
        cart_repository.find_cart_item_by_id.return_value = cart_item
        
        # User 1's cart is cart_id=1, but item belongs to cart_id=5 (user 2's cart)
        user_cart = self.create_mock_cart(1, 1)  # user_id=1, cart_id=1
        cart_repository.find_by_user_id.return_value = user_cart
        
        input_data = RemoveCartItemInputData(user_id=1, cart_item_id=1)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "This cart item does not belong to you" in output.error_message
    
    # ============ INPUT VALIDATION ============
    
    def test_remove_with_invalid_user_id_fails(self, use_case, cart_repository):
        """Test 8: User ID không hợp lệ (0)"""
        # Arrange
        input_data = RemoveCartItemInputData(user_id=0, cart_item_id=1)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Invalid user ID" in output.error_message
        cart_repository.find_cart_item_by_id.assert_not_called()
    
    def test_remove_with_negative_user_id_fails(self, use_case, cart_repository):
        """Test 9: User ID âm"""
        # Arrange
        input_data = RemoveCartItemInputData(user_id=-1, cart_item_id=1)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Invalid user ID" in output.error_message
    
    def test_remove_with_invalid_cart_item_id_fails(self, use_case, cart_repository):
        """Test 10: Cart item ID không hợp lệ (0)"""
        # Arrange
        input_data = RemoveCartItemInputData(user_id=1, cart_item_id=0)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Invalid cart item ID" in output.error_message
        cart_repository.find_cart_item_by_id.assert_not_called()
    
    def test_remove_with_negative_cart_item_id_fails(self, use_case, cart_repository):
        """Test 11: Cart item ID âm"""
        # Arrange
        input_data = RemoveCartItemInputData(user_id=1, cart_item_id=-5)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Invalid cart item ID" in output.error_message
    
    # ============ REPOSITORY EXCEPTIONS ============
    
    def test_repository_exception_handled(self, use_case, cart_repository):
        """Test 12: Lỗi từ repository được xử lý"""
        # Arrange
        cart_repository.find_cart_item_by_id.side_effect = Exception("Database connection error")
        
        input_data = RemoveCartItemInputData(user_id=1, cart_item_id=1)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "An error occurred while removing cart item" in output.error_message
    
    # ============ OUTPUT DATA STRUCTURE ============
    
    def test_output_data_structure_on_success(self, use_case, cart_repository):
        """Test 13: Cấu trúc output data khi thành công"""
        # Arrange
        cart_item = self.create_mock_cart_item(1, 1, 10, 2)
        cart_repository.find_cart_item_by_id.return_value = cart_item
        
        cart = self.create_mock_cart(1, 1)
        cart_repository.find_by_user_id.return_value = cart
        
        input_data = RemoveCartItemInputData(user_id=1, cart_item_id=1)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert isinstance(output, RemoveCartItemOutputData)
        assert hasattr(output, 'success')
        assert hasattr(output, 'message')
        assert hasattr(output, 'error_message')
        
        assert output.success is True
        assert len(output.message) > 0
        assert output.error_message == ""
    
    def test_output_data_structure_on_failure(self, use_case, cart_repository):
        """Test 14: Cấu trúc output data khi thất bại"""
        # Arrange
        cart_repository.find_cart_item_by_id.return_value = None
        
        input_data = RemoveCartItemInputData(user_id=1, cart_item_id=999)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert isinstance(output, RemoveCartItemOutputData)
        assert output.success is False
        assert output.message == ""
        assert len(output.error_message) > 0
