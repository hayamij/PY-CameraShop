"""
Unit Tests for UpdateCartItemUseCase
Test mọi trường hợp cập nhật số lượng sản phẩm trong giỏ - chi tiết và đáng tin cậy
"""

import pytest
from unittest.mock import Mock
from decimal import Decimal

from app.business.use_cases.update_cart_item_use_case import (
    UpdateCartItemUseCase,
    UpdateCartItemInputData,
    UpdateCartItemOutputData
)
from app.domain.exceptions import (
    CartItemNotFoundException,
    InsufficientStockException,
    ValidationException
)


class TestUpdateCartItemUseCase:
    """Test suite cho UpdateCartItemUseCase - test kỹ lưỡng mọi trường hợp"""
    
    @pytest.fixture
    def cart_repository(self):
        """Mock cart repository"""
        return Mock()
    
    @pytest.fixture
    def product_repository(self):
        """Mock product repository"""
        return Mock()
    
    @pytest.fixture
    def use_case(self, cart_repository, product_repository):
        """Khởi tạo use case"""
        return UpdateCartItemUseCase(cart_repository, product_repository)
    
    def create_mock_product(self, product_id, name, price, stock=10):
        """Helper tạo mock product"""
        product = Mock()
        product.product_id = product_id
        product.name = name
        product.price = Decimal(str(price))
        product.stock_quantity = stock
        return product
    
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
        cart.cart_id = cart_id
        cart.user_id = user_id
        return cart
    
    # ============ SUCCESS CASES - INCREASE QUANTITY ============
    
    def test_update_increase_quantity_success(self, use_case, cart_repository, product_repository):
        """Test 1: Tăng số lượng thành công"""
        # Arrange
        user_id = 1
        cart_item_id = 5
        current_quantity = 2
        new_quantity = 5
        
        cart_item = self.create_mock_cart_item(cart_item_id, 1, 10, current_quantity)
        cart_repository.find_cart_item_by_id.return_value = cart_item
        
        cart = self.create_mock_cart(1, user_id)
        cart_repository.find_by_user_id.return_value = cart
        
        product = self.create_mock_product(10, "Camera", 10000000, stock=20)
        product_repository.find_by_id.return_value = product
        
        updated_item = self.create_mock_cart_item(cart_item_id, 1, 10, new_quantity)
        cart_repository.update_cart_item_quantity.return_value = updated_item
        
        input_data = UpdateCartItemInputData(
            user_id=user_id,
            cart_item_id=cart_item_id,
            new_quantity=new_quantity
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.cart_item_id == cart_item_id
        assert output.new_quantity == new_quantity
        assert "Quantity updated to 5" in output.message
        assert output.error_message == ""
        
        cart_repository.update_cart_item_quantity.assert_called_once_with(cart_item_id, new_quantity)
    
    def test_update_increase_to_max_stock_success(self, use_case, cart_repository, product_repository):
        """Test 2: Tăng lên đúng bằng tồn kho"""
        # Arrange
        cart_item = self.create_mock_cart_item(1, 1, 10, 5)
        cart_repository.find_cart_item_by_id.return_value = cart_item
        
        cart = self.create_mock_cart(1, 1)
        cart_repository.find_by_user_id.return_value = cart
        
        product = self.create_mock_product(10, "Product", 1000000, stock=10)
        product_repository.find_by_id.return_value = product
        
        updated_item = self.create_mock_cart_item(1, 1, 10, 10)
        cart_repository.update_cart_item_quantity.return_value = updated_item
        
        input_data = UpdateCartItemInputData(user_id=1, cart_item_id=1, new_quantity=10)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.new_quantity == 10
    
    # ============ SUCCESS CASES - DECREASE QUANTITY ============
    
    def test_update_decrease_quantity_success(self, use_case, cart_repository, product_repository):
        """Test 3: Giảm số lượng thành công"""
        # Arrange
        cart_item = self.create_mock_cart_item(1, 1, 10, 10)
        cart_repository.find_cart_item_by_id.return_value = cart_item
        
        cart = self.create_mock_cart(1, 1)
        cart_repository.find_by_user_id.return_value = cart
        
        product = self.create_mock_product(10, "Product", 1000000, stock=20)
        product_repository.find_by_id.return_value = product
        
        updated_item = self.create_mock_cart_item(1, 1, 10, 3)
        cart_repository.update_cart_item_quantity.return_value = updated_item
        
        input_data = UpdateCartItemInputData(user_id=1, cart_item_id=1, new_quantity=3)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.new_quantity == 3
    
    def test_update_set_to_one_success(self, use_case, cart_repository, product_repository):
        """Test 4: Giảm xuống còn 1"""
        # Arrange
        cart_item = self.create_mock_cart_item(1, 1, 10, 5)
        cart_repository.find_cart_item_by_id.return_value = cart_item
        
        cart = self.create_mock_cart(1, 1)
        cart_repository.find_by_user_id.return_value = cart
        
        product = self.create_mock_product(10, "Product", 1000000, stock=10)
        product_repository.find_by_id.return_value = product
        
        updated_item = self.create_mock_cart_item(1, 1, 10, 1)
        cart_repository.update_cart_item_quantity.return_value = updated_item
        
        input_data = UpdateCartItemInputData(user_id=1, cart_item_id=1, new_quantity=1)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.new_quantity == 1
    
    # ============ CART ITEM NOT FOUND ============
    
    def test_update_nonexistent_cart_item_fails(self, use_case, cart_repository, product_repository):
        """Test 5: Cập nhật cart item không tồn tại"""
        # Arrange
        cart_repository.find_cart_item_by_id.return_value = None
        
        input_data = UpdateCartItemInputData(user_id=1, cart_item_id=999, new_quantity=5)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Cart item with ID 999 not found" in output.error_message
        cart_repository.update_cart_item_quantity.assert_not_called()
    
    # ============ CART OWNERSHIP VALIDATION ============
    
    def test_update_cart_item_not_belonging_to_user_fails(self, use_case, cart_repository, product_repository):
        """Test 6: Cập nhật cart item không thuộc về user"""
        # Arrange
        cart_item = self.create_mock_cart_item(1, 10, 5, 2)  # belongs to cart_id=10
        cart_repository.find_cart_item_by_id.return_value = cart_item
        
        # User's cart is cart_id=1, but item belongs to cart_id=10
        user_cart = self.create_mock_cart(1, 1)
        cart_repository.find_by_user_id.return_value = user_cart
        
        input_data = UpdateCartItemInputData(user_id=1, cart_item_id=1, new_quantity=5)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "This cart item does not belong to you" in output.error_message
        cart_repository.update_cart_item_quantity.assert_not_called()
    
    def test_update_cart_item_user_has_no_cart_fails(self, use_case, cart_repository, product_repository):
        """Test 7: User không có cart"""
        # Arrange
        cart_item = self.create_mock_cart_item(1, 1, 5, 2)
        cart_repository.find_cart_item_by_id.return_value = cart_item
        
        # User has no cart
        cart_repository.find_by_user_id.return_value = None
        
        input_data = UpdateCartItemInputData(user_id=1, cart_item_id=1, new_quantity=5)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "This cart item does not belong to you" in output.error_message
    
    # ============ INSUFFICIENT STOCK ============
    
    def test_update_quantity_exceeds_stock_fails(self, use_case, cart_repository, product_repository):
        """Test 8: Số lượng mới vượt quá tồn kho"""
        # Arrange
        cart_item = self.create_mock_cart_item(1, 1, 10, 2)
        cart_repository.find_cart_item_by_id.return_value = cart_item
        
        cart = self.create_mock_cart(1, 1)
        cart_repository.find_by_user_id.return_value = cart
        
        product = self.create_mock_product(10, "Limited Stock", 1000000, stock=5)
        product_repository.find_by_id.return_value = product
        
        input_data = UpdateCartItemInputData(user_id=1, cart_item_id=1, new_quantity=10)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Only 5 items available in stock" in output.error_message
        cart_repository.update_cart_item_quantity.assert_not_called()
    
    def test_update_to_zero_stock_product_fails(self, use_case, cart_repository, product_repository):
        """Test 9: Cập nhật cho sản phẩm hết hàng"""
        # Arrange
        cart_item = self.create_mock_cart_item(1, 1, 10, 1)
        cart_repository.find_cart_item_by_id.return_value = cart_item
        
        cart = self.create_mock_cart(1, 1)
        cart_repository.find_by_user_id.return_value = cart
        
        product = self.create_mock_product(10, "Out of Stock", 1000000, stock=0)
        product_repository.find_by_id.return_value = product
        
        input_data = UpdateCartItemInputData(user_id=1, cart_item_id=1, new_quantity=1)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Only 0 items available in stock" in output.error_message
    
    # ============ PRODUCT NOT FOUND ============
    
    def test_update_deleted_product_fails(self, use_case, cart_repository, product_repository):
        """Test 10: Sản phẩm đã bị xóa"""
        # Arrange
        cart_item = self.create_mock_cart_item(1, 1, 999, 2)
        cart_repository.find_cart_item_by_id.return_value = cart_item
        
        cart = self.create_mock_cart(1, 1)
        cart_repository.find_by_user_id.return_value = cart
        
        product_repository.find_by_id.return_value = None
        
        input_data = UpdateCartItemInputData(user_id=1, cart_item_id=1, new_quantity=5)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Product no longer available" in output.error_message
    
    # ============ INPUT VALIDATION ============
    
    def test_update_with_invalid_user_id_fails(self, use_case, cart_repository, product_repository):
        """Test 11: User ID không hợp lệ (0)"""
        # Arrange
        input_data = UpdateCartItemInputData(user_id=0, cart_item_id=1, new_quantity=5)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Invalid user ID" in output.error_message
        cart_repository.find_cart_item_by_id.assert_not_called()
    
    def test_update_with_negative_user_id_fails(self, use_case, cart_repository, product_repository):
        """Test 12: User ID âm"""
        # Arrange
        input_data = UpdateCartItemInputData(user_id=-1, cart_item_id=1, new_quantity=5)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Invalid user ID" in output.error_message
    
    def test_update_with_invalid_cart_item_id_fails(self, use_case, cart_repository, product_repository):
        """Test 13: Cart item ID không hợp lệ"""
        # Arrange
        input_data = UpdateCartItemInputData(user_id=1, cart_item_id=0, new_quantity=5)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Invalid cart item ID" in output.error_message
        cart_repository.find_cart_item_by_id.assert_not_called()
    
    def test_update_with_zero_quantity_fails(self, use_case, cart_repository, product_repository):
        """Test 14: Số lượng = 0 (nên dùng remove thay vì update)"""
        # Arrange
        input_data = UpdateCartItemInputData(user_id=1, cart_item_id=1, new_quantity=0)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Quantity must be positive" in output.error_message
        cart_repository.find_cart_item_by_id.assert_not_called()
    
    def test_update_with_negative_quantity_fails(self, use_case, cart_repository, product_repository):
        """Test 15: Số lượng âm"""
        # Arrange
        input_data = UpdateCartItemInputData(user_id=1, cart_item_id=1, new_quantity=-5)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Quantity must be positive" in output.error_message
    
    def test_update_quantity_exceeds_limit_fails(self, use_case, cart_repository, product_repository):
        """Test 16: Số lượng > 100 (limit)"""
        # Arrange
        input_data = UpdateCartItemInputData(user_id=1, cart_item_id=1, new_quantity=101)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Cannot have more than 100 items" in output.error_message
    
    def test_update_to_exactly_100_success(self, use_case, cart_repository, product_repository):
        """Test 17: Cập nhật lên đúng 100 (boundary)"""
        # Arrange
        cart_item = self.create_mock_cart_item(1, 1, 10, 50)
        cart_repository.find_cart_item_by_id.return_value = cart_item
        
        cart = self.create_mock_cart(1, 1)
        cart_repository.find_by_user_id.return_value = cart
        
        product = self.create_mock_product(10, "Product", 1000000, stock=150)
        product_repository.find_by_id.return_value = product
        
        updated_item = self.create_mock_cart_item(1, 1, 10, 100)
        cart_repository.update_cart_item_quantity.return_value = updated_item
        
        input_data = UpdateCartItemInputData(user_id=1, cart_item_id=1, new_quantity=100)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.new_quantity == 100
    
    # ============ REPOSITORY EXCEPTIONS ============
    
    def test_repository_exception_handled(self, use_case, cart_repository, product_repository):
        """Test 18: Lỗi từ repository được xử lý"""
        # Arrange
        cart_repository.find_cart_item_by_id.side_effect = Exception("Database error")
        
        input_data = UpdateCartItemInputData(user_id=1, cart_item_id=1, new_quantity=5)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "An error occurred while updating cart item" in output.error_message
    
    # ============ OUTPUT DATA STRUCTURE ============
    
    def test_output_data_structure_on_success(self, use_case, cart_repository, product_repository):
        """Test 19: Cấu trúc output data khi thành công"""
        # Arrange
        cart_item = self.create_mock_cart_item(1, 1, 10, 2)
        cart_repository.find_cart_item_by_id.return_value = cart_item
        
        cart = self.create_mock_cart(1, 1)
        cart_repository.find_by_user_id.return_value = cart
        
        product = self.create_mock_product(10, "Product", 1000000, stock=20)
        product_repository.find_by_id.return_value = product
        
        updated_item = self.create_mock_cart_item(1, 1, 10, 8)
        cart_repository.update_cart_item_quantity.return_value = updated_item
        
        input_data = UpdateCartItemInputData(user_id=1, cart_item_id=1, new_quantity=8)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert isinstance(output, UpdateCartItemOutputData)
        assert hasattr(output, 'success')
        assert hasattr(output, 'cart_item_id')
        assert hasattr(output, 'new_quantity')
        assert hasattr(output, 'message')
        assert hasattr(output, 'error_message')
        
        assert output.success is True
        assert output.cart_item_id is not None
        assert output.new_quantity > 0
        assert len(output.message) > 0
        assert output.error_message == ""
    
    def test_output_data_structure_on_failure(self, use_case, cart_repository, product_repository):
        """Test 20: Cấu trúc output data khi thất bại"""
        # Arrange
        cart_repository.find_cart_item_by_id.return_value = None
        
        input_data = UpdateCartItemInputData(user_id=1, cart_item_id=999, new_quantity=5)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert isinstance(output, UpdateCartItemOutputData)
        assert output.success is False
        assert output.cart_item_id is None
        assert output.new_quantity == 0
        assert output.message == ""
        assert len(output.error_message) > 0
