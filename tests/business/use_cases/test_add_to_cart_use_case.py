"""
Unit Tests for AddToCartUseCase
Test mọi trường hợp thêm sản phẩm vào giỏ hàng - chi tiết và đáng tin cậy
"""

import pytest
from unittest.mock import Mock
from decimal import Decimal

from app.business.use_cases.add_to_cart_use_case import (
    AddToCartUseCase,
    AddToCartInputData,
    AddToCartOutputData
)
from app.domain.exceptions import (
    ProductNotFoundException,
    InsufficientStockException,
    ValidationException
)


class TestAddToCartUseCase:
    """Test suite cho AddToCartUseCase - test kỹ lưỡng mọi trường hợp"""
    
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
        return AddToCartUseCase(cart_repository, product_repository)
    
    def create_mock_product(self, product_id, name, price, stock=10, is_visible=True):
        """Helper tạo mock product"""
        product = Mock()
        product.product_id = product_id
        product.name = name
        product.price = Mock()
        product.price.amount = Decimal(str(price))
        product.price.currency = "VND"
        product.stock_quantity = stock
        product.is_visible = is_visible
        return product
    
    def create_mock_cart(self, cart_id, user_id, items=None):
        """Helper tạo mock cart"""
        cart = Mock()
        cart.cart_id = cart_id
        cart.user_id = user_id
        cart.items = items or []
        cart.get_total = Mock(return_value=0.0)
        return cart
    
    def create_mock_cart_item(self, cart_item_id, cart_id, product_id, quantity):
        """Helper tạo mock cart item"""
        item = Mock()
        item.cart_item_id = cart_item_id
        item.cart_id = cart_id
        item.product_id = product_id
        item.quantity = quantity
        return item
    
    # ============ SUCCESS CASES - NEW ITEM ============
    
    def test_add_new_item_to_empty_cart_success(self, use_case, cart_repository, product_repository):
        """Test 1: Thêm sản phẩm mới vào giỏ trống"""
        # Arrange
        user_id = 1
        product_id = 10
        quantity = 2
        
        mock_product = self.create_mock_product(product_id, "Camera", 10000000, stock=20)
        product_repository.find_by_id.return_value = mock_product
        
        # Cart doesn't exist yet
        cart_repository.find_by_user_id.return_value = None
        
        # Create new cart
        new_cart = self.create_mock_cart(1, user_id)
        cart_repository.create_cart.return_value = new_cart
        
        # No existing item
        cart_repository.find_cart_item.return_value = None
        
        # Add item
        new_item = self.create_mock_cart_item(1, 1, product_id, quantity)
        cart_repository.add_item_to_cart.return_value = new_item
        
        # After adding, cart has 1 item
        cart_with_items = self.create_mock_cart(1, user_id, [new_item])
        cart_with_items.get_total = Mock(return_value=20000000.0)
        cart_repository.find_by_user_id.side_effect = [None, cart_with_items]
        
        input_data = AddToCartInputData(user_id=user_id, product_id=product_id, quantity=quantity)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.cart_id == 1
        assert output.cart_item_id == 1
        assert "Added 2 item(s) to cart" in output.message
        assert output.total_items == 2
        assert output.cart_total == 20000000.0
        assert output.error_message == ""
        
        # Verify repository calls
        cart_repository.create_cart.assert_called_once_with(user_id)
        cart_repository.add_item_to_cart.assert_called_once_with(1, product_id, quantity)
    
    def test_add_new_item_to_existing_cart_success(self, use_case, cart_repository, product_repository):
        """Test 2: Thêm sản phẩm mới vào giỏ đã có sản phẩm khác"""
        # Arrange
        user_id = 1
        product_id = 20
        
        mock_product = self.create_mock_product(product_id, "Lens", 5000000, stock=15)
        product_repository.find_by_id.return_value = mock_product
        
        # Existing cart with another item
        existing_item = self.create_mock_cart_item(1, 1, 10, 1)
        existing_cart = self.create_mock_cart(1, user_id, [existing_item])
        cart_repository.find_by_user_id.return_value = existing_cart
        
        # No existing item for this product
        cart_repository.find_cart_item.return_value = None
        
        # Add new item
        new_item = self.create_mock_cart_item(2, 1, product_id, 1)
        cart_repository.add_item_to_cart.return_value = new_item
        
        # After adding, cart has 2 items
        cart_with_items = self.create_mock_cart(1, user_id, [existing_item, new_item])
        cart_with_items.get_total = Mock(return_value=15000000.0)
        cart_repository.find_by_user_id.side_effect = [existing_cart, cart_with_items]
        
        input_data = AddToCartInputData(user_id=user_id, product_id=product_id, quantity=1)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.cart_item_id == 2
        assert "Added 1 item(s) to cart" in output.message
        assert output.total_items == 2
        cart_repository.create_cart.assert_not_called()
    
    def test_add_multiple_quantity_success(self, use_case, cart_repository, product_repository):
        """Test 3: Thêm nhiều số lượng cùng lúc"""
        # Arrange
        mock_product = self.create_mock_product(1, "Tripod", 1000000, stock=50)
        product_repository.find_by_id.return_value = mock_product
        
        cart = self.create_mock_cart(1, 1)
        cart_repository.find_by_user_id.return_value = cart
        cart_repository.find_cart_item.return_value = None
        
        new_item = self.create_mock_cart_item(1, 1, 1, 10)
        cart_repository.add_item_to_cart.return_value = new_item
        
        cart_with_items = self.create_mock_cart(1, 1, [new_item])
        cart_with_items.get_total = Mock(return_value=10000000.0)
        cart_repository.find_by_user_id.side_effect = [cart, cart_with_items]
        
        input_data = AddToCartInputData(user_id=1, product_id=1, quantity=10)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.total_items == 10
        cart_repository.add_item_to_cart.assert_called_once_with(1, 1, 10)
    
    # ============ SUCCESS CASES - UPDATE EXISTING ITEM ============
    
    def test_add_to_existing_cart_item_updates_quantity(self, use_case, cart_repository, product_repository):
        """Test 4: Thêm vào sản phẩm đã có trong giỏ - cập nhật số lượng"""
        # Arrange
        user_id = 1
        product_id = 15
        
        mock_product = self.create_mock_product(product_id, "Memory Card", 500000, stock=20)
        product_repository.find_by_id.return_value = mock_product
        
        cart = self.create_mock_cart(1, user_id)
        cart_repository.find_by_user_id.return_value = cart
        
        # Existing item with quantity 3
        existing_item = self.create_mock_cart_item(5, 1, product_id, 3)
        cart_repository.find_cart_item.return_value = existing_item
        
        # Update quantity to 3 + 2 = 5
        updated_item = self.create_mock_cart_item(5, 1, product_id, 5)
        cart_repository.update_cart_item_quantity.return_value = updated_item
        
        cart_with_updated = self.create_mock_cart(1, user_id, [updated_item])
        cart_with_updated.get_total = Mock(return_value=2500000.0)
        cart_repository.find_by_user_id.side_effect = [cart, cart_with_updated]
        
        input_data = AddToCartInputData(user_id=user_id, product_id=product_id, quantity=2)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.cart_item_id == 5
        assert "Updated quantity to 5" in output.message
        assert output.total_items == 5
        cart_repository.update_cart_item_quantity.assert_called_once_with(5, 5)
        cart_repository.add_item_to_cart.assert_not_called()
    
    def test_add_one_more_to_existing_item(self, use_case, cart_repository, product_repository):
        """Test 5: Thêm 1 sản phẩm vào item đã có"""
        # Arrange
        mock_product = self.create_mock_product(1, "Battery", 300000, stock=10)
        product_repository.find_by_id.return_value = mock_product
        
        cart = self.create_mock_cart(1, 1)
        existing_item = self.create_mock_cart_item(3, 1, 1, 2)
        cart_repository.find_by_user_id.return_value = cart
        cart_repository.find_cart_item.return_value = existing_item
        
        updated_item = self.create_mock_cart_item(3, 1, 1, 3)
        cart_repository.update_cart_item_quantity.return_value = updated_item
        
        cart_with_updated = self.create_mock_cart(1, 1, [updated_item])
        cart_with_updated.get_total = Mock(return_value=900000.0)
        cart_repository.find_by_user_id.side_effect = [cart, cart_with_updated]
        
        input_data = AddToCartInputData(user_id=1, product_id=1, quantity=1)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.total_items == 3
        cart_repository.update_cart_item_quantity.assert_called_once_with(3, 3)
    
    # ============ PRODUCT NOT FOUND ============
    
    def test_add_nonexistent_product_fails(self, use_case, cart_repository, product_repository):
        """Test 6: Thêm sản phẩm không tồn tại"""
        # Arrange
        product_repository.find_by_id.return_value = None
        
        input_data = AddToCartInputData(user_id=1, product_id=999, quantity=1)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Product with ID 999 not found" in output.error_message
        assert output.cart_id is None
        assert output.cart_item_id is None
        cart_repository.add_item_to_cart.assert_not_called()
    
    # ============ PRODUCT NOT VISIBLE ============
    
    def test_add_hidden_product_fails(self, use_case, cart_repository, product_repository):
        """Test 7: Thêm sản phẩm bị ẩn"""
        # Arrange
        mock_product = self.create_mock_product(1, "Hidden Product", 1000000, stock=10, is_visible=False)
        product_repository.find_by_id.return_value = mock_product
        
        input_data = AddToCartInputData(user_id=1, product_id=1, quantity=1)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "This product is not available" in output.error_message
        cart_repository.add_item_to_cart.assert_not_called()
    
    # ============ INSUFFICIENT STOCK ============
    
    def test_add_quantity_exceeds_stock_fails(self, use_case, cart_repository, product_repository):
        """Test 8: Thêm số lượng vượt quá tồn kho"""
        # Arrange
        mock_product = self.create_mock_product(1, "Limited Stock", 1000000, stock=5)
        product_repository.find_by_id.return_value = mock_product
        
        input_data = AddToCartInputData(user_id=1, product_id=1, quantity=10)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Only 5 items available in stock" in output.error_message
        cart_repository.add_item_to_cart.assert_not_called()
    
    def test_add_to_existing_item_exceeds_stock_fails(self, use_case, cart_repository, product_repository):
        """Test 9: Cập nhật số lượng item có sẵn vượt quá tồn kho"""
        # Arrange
        mock_product = self.create_mock_product(1, "Product", 1000000, stock=10)
        product_repository.find_by_id.return_value = mock_product
        
        cart = self.create_mock_cart(1, 1)
        cart_repository.find_by_user_id.return_value = cart
        
        # Already have 8 in cart, trying to add 5 more (total 13 > stock 10)
        existing_item = self.create_mock_cart_item(1, 1, 1, 8)
        cart_repository.find_cart_item.return_value = existing_item
        
        input_data = AddToCartInputData(user_id=1, product_id=1, quantity=5)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Cannot add 5 more items" in output.error_message
        assert "Only 2 more available" in output.error_message
        cart_repository.update_cart_item_quantity.assert_not_called()
    
    def test_add_exact_remaining_stock_to_existing_item_success(self, use_case, cart_repository, product_repository):
        """Test 10: Thêm đúng số lượng còn lại vào item có sẵn"""
        # Arrange
        mock_product = self.create_mock_product(1, "Product", 1000000, stock=10)
        product_repository.find_by_id.return_value = mock_product
        
        cart = self.create_mock_cart(1, 1)
        existing_item = self.create_mock_cart_item(1, 1, 1, 7)
        cart_repository.find_by_user_id.return_value = cart
        cart_repository.find_cart_item.return_value = existing_item
        
        # Add 3 more (7 + 3 = 10 = stock)
        updated_item = self.create_mock_cart_item(1, 1, 1, 10)
        cart_repository.update_cart_item_quantity.return_value = updated_item
        
        cart_with_updated = self.create_mock_cart(1, 1, [updated_item])
        cart_with_updated.get_total = Mock(return_value=10000000.0)
        cart_repository.find_by_user_id.side_effect = [cart, cart_with_updated]
        
        input_data = AddToCartInputData(user_id=1, product_id=1, quantity=3)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.total_items == 10
        cart_repository.update_cart_item_quantity.assert_called_once_with(1, 10)
    
    def test_add_to_out_of_stock_product_fails(self, use_case, cart_repository, product_repository):
        """Test 11: Thêm sản phẩm hết hàng"""
        # Arrange
        mock_product = self.create_mock_product(1, "Out of Stock", 1000000, stock=0)
        product_repository.find_by_id.return_value = mock_product
        
        input_data = AddToCartInputData(user_id=1, product_id=1, quantity=1)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Only 0 items available in stock" in output.error_message
    
    # ============ INPUT VALIDATION ============
    
    def test_add_with_invalid_user_id_fails(self, use_case, cart_repository, product_repository):
        """Test 12: User ID không hợp lệ (0)"""
        # Arrange
        input_data = AddToCartInputData(user_id=0, product_id=1, quantity=1)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Invalid user ID" in output.error_message
        product_repository.find_by_id.assert_not_called()
    
    def test_add_with_negative_user_id_fails(self, use_case, cart_repository, product_repository):
        """Test 13: User ID âm"""
        # Arrange
        input_data = AddToCartInputData(user_id=-1, product_id=1, quantity=1)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Invalid user ID" in output.error_message
    
    def test_add_with_invalid_product_id_fails(self, use_case, cart_repository, product_repository):
        """Test 14: Product ID không hợp lệ"""
        # Arrange
        input_data = AddToCartInputData(user_id=1, product_id=0, quantity=1)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Invalid product ID" in output.error_message
        product_repository.find_by_id.assert_not_called()
    
    def test_add_with_zero_quantity_fails(self, use_case, cart_repository, product_repository):
        """Test 15: Số lượng = 0"""
        # Arrange
        input_data = AddToCartInputData(user_id=1, product_id=1, quantity=0)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Quantity must be positive" in output.error_message
        product_repository.find_by_id.assert_not_called()
    
    def test_add_with_negative_quantity_fails(self, use_case, cart_repository, product_repository):
        """Test 16: Số lượng âm"""
        # Arrange
        input_data = AddToCartInputData(user_id=1, product_id=1, quantity=-5)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Quantity must be positive" in output.error_message
    
    def test_add_quantity_exceeds_limit_fails(self, use_case, cart_repository, product_repository):
        """Test 17: Số lượng vượt quá giới hạn (>100)"""
        # Arrange
        input_data = AddToCartInputData(user_id=1, product_id=1, quantity=101)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Cannot add more than 100 items at once" in output.error_message
    
    def test_add_exactly_100_items_success(self, use_case, cart_repository, product_repository):
        """Test 18: Thêm đúng 100 items (boundary)"""
        # Arrange
        mock_product = self.create_mock_product(1, "Product", 1000000, stock=150)
        product_repository.find_by_id.return_value = mock_product
        
        cart = self.create_mock_cart(1, 1)
        cart_repository.find_by_user_id.return_value = cart
        cart_repository.find_cart_item.return_value = None
        
        new_item = self.create_mock_cart_item(1, 1, 1, 100)
        cart_repository.add_item_to_cart.return_value = new_item
        
        cart_with_items = self.create_mock_cart(1, 1, [new_item])
        cart_with_items.get_total = Mock(return_value=100000000.0)
        cart_repository.find_by_user_id.side_effect = [cart, cart_with_items]
        
        input_data = AddToCartInputData(user_id=1, product_id=1, quantity=100)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.total_items == 100
    
    # ============ REPOSITORY EXCEPTIONS ============
    
    def test_repository_exception_handled(self, use_case, cart_repository, product_repository):
        """Test 19: Lỗi từ repository được xử lý"""
        # Arrange
        product_repository.find_by_id.side_effect = Exception("Database connection error")
        
        input_data = AddToCartInputData(user_id=1, product_id=1, quantity=1)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "An error occurred while adding to cart" in output.error_message
    
    # ============ OUTPUT DATA STRUCTURE ============
    
    def test_output_data_structure_on_success(self, use_case, cart_repository, product_repository):
        """Test 20: Cấu trúc output data khi thành công"""
        # Arrange
        mock_product = self.create_mock_product(1, "Product", 1000000, stock=10)
        product_repository.find_by_id.return_value = mock_product
        
        cart = self.create_mock_cart(1, 1)
        cart_repository.find_by_user_id.return_value = cart
        cart_repository.find_cart_item.return_value = None
        
        new_item = self.create_mock_cart_item(1, 1, 1, 2)
        cart_repository.add_item_to_cart.return_value = new_item
        
        cart_with_items = self.create_mock_cart(1, 1, [new_item])
        cart_with_items.get_total = Mock(return_value=2000000.0)
        cart_repository.find_by_user_id.side_effect = [cart, cart_with_items]
        
        input_data = AddToCartInputData(user_id=1, product_id=1, quantity=2)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert isinstance(output, AddToCartOutputData)
        assert hasattr(output, 'success')
        assert hasattr(output, 'cart_id')
        assert hasattr(output, 'cart_item_id')
        assert hasattr(output, 'message')
        assert hasattr(output, 'error_message')
        assert hasattr(output, 'total_items')
        assert hasattr(output, 'cart_total')
        
        assert output.success is True
        assert output.cart_id is not None
        assert output.cart_item_id is not None
        assert len(output.message) > 0
        assert output.error_message == ""
        assert output.total_items > 0
        assert output.cart_total > 0
    
    def test_output_data_structure_on_failure(self, use_case, cart_repository, product_repository):
        """Test 21: Cấu trúc output data khi thất bại"""
        # Arrange
        product_repository.find_by_id.return_value = None
        
        input_data = AddToCartInputData(user_id=1, product_id=999, quantity=1)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert isinstance(output, AddToCartOutputData)
        assert output.success is False
        assert output.cart_id is None
        assert output.cart_item_id is None
        assert output.message == ""
        assert len(output.error_message) > 0
        assert output.total_items == 0
        assert output.cart_total == 0.0
