"""
Unit Tests for PlaceOrderUseCase
Test mọi trường hợp đặt hàng - usecase phức tạp nhất với nhiều business rules
"""

import pytest
from unittest.mock import Mock
from decimal import Decimal

from app.business.use_cases.place_order_use_case import (
    PlaceOrderUseCase,
    PlaceOrderInputData,
    PlaceOrderOutputData
)
from app.domain.exceptions import (
    CartNotFoundException,
    InsufficientStockException,
    ProductNotFoundException,
    ValidationException
)


class TestPlaceOrderUseCase:
    """Test suite cho PlaceOrderUseCase - test kỹ lưỡng usecase phức tạp nhất"""
    
    @pytest.fixture
    def order_repository(self):
        """Mock order repository"""
        return Mock()
    
    @pytest.fixture
    def cart_repository(self):
        """Mock cart repository"""
        return Mock()
    
    @pytest.fixture
    def product_repository(self):
        """Mock product repository"""
        return Mock()
    
    @pytest.fixture
    def use_case(self, cart_repository, product_repository, order_repository):
        """Khởi tạo use case - correct parameter order!"""
        # PlaceOrderUseCase.__init__(order_repository, cart_repository, product_repository)
        return PlaceOrderUseCase(order_repository, cart_repository, product_repository)
    
    def create_mock_product(self, product_id, name, price, stock, is_visible=True):
        """Helper tạo mock product"""
        product = Mock()
        product.product_id = product_id
        product.name = name
        
        # Product price is Money object with .amount attribute
        # Import Money to create real Money object instead of Mock
        from app.domain.value_objects.money import Money
        product.price = Money(Decimal(str(price)), "VND")
        
        product.stock_quantity = stock
        product.is_visible = is_visible
        product.currency = "VND"
        
        # Method for reducing stock
        def reduce_stock(quantity):
            product.stock_quantity -= quantity
        product.reduce_stock = reduce_stock
        
        return product
    
    def create_mock_cart_item(self, cart_item_id, cart_id, product_id, quantity, product=None):
        """Helper tạo mock cart item with embedded product"""
        item = Mock()
        item.cart_item_id = cart_item_id
        item.cart_id = cart_id
        item.product_id = product_id
        item.quantity = quantity
        
        # Cart item has embedded product object with price
        if product:
            item.product = product
        else:
            # Default product mock with real Money price
            from app.domain.value_objects.money import Money
            mock_product = Mock()
            mock_product.product_id = product_id
            mock_product.name = f"Product {product_id}"
            mock_product.price = Money(Decimal('1000000'), "VND")
            item.product = mock_product
        
        return item
    
    def create_mock_cart(self, cart_id, user_id, items):
        """Helper tạo mock cart with items list"""
        cart = Mock()
        cart.cart_id = cart_id
        cart.user_id = user_id
        
        # Ensure items is iterable - configure Mock to return list on access
        cart.configure_mock(items=items)
        
        # Calculate total from items
        total = Decimal('0')
        if items:
            for item in items:
                total += item.product.price.amount * item.quantity
        
        cart.get_total = Mock(return_value=float(total))
        return cart
    
    def create_mock_order(self, order_id, user_id, total, status="Pending"):
        """Helper tạo mock order"""
        order = Mock()
        order.order_id = order_id
        order.user_id = user_id
        order.total_amount = Decimal(str(total))
        order.status = status
        return order
    
    # ============ SUCCESS CASES ============
    
    def test_place_order_with_single_item_success(self, use_case, cart_repository, product_repository, order_repository):
        """Test 1: Đặt hàng thành công với 1 sản phẩm"""
        # Arrange
        user_id = 1
        
        # Create product first
        product = self.create_mock_product(10, "Camera A", 5000000, 10)
        
        # Create cart item with embedded product
        cart_item = self.create_mock_cart_item(1, 1, 10, 2, product=product)
        
        # Create cart with items as actual list 
        cart = Mock(cart_id=1, user_id=user_id)
        cart.items = [cart_item]  # MUST be actual list, not Mock
        
        # Mock find_by_user_id to return our cart
        cart_repository.find_by_user_id.side_effect = lambda uid: cart if uid == user_id else None
        
        # Mock product_repository.find_by_id to return same product for all calls
        product_repository.find_by_id.return_value = product
        
        # Mock saved order (order_repository.save will be called with real Order entity)
        mock_saved_order = Mock()
        mock_saved_order.id = 1
        mock_total = Mock()
        mock_total.amount = 10000000
        mock_saved_order.total = mock_total
        order_repository.save.return_value = mock_saved_order
        
        input_data = PlaceOrderInputData(
            user_id=user_id,
            shipping_address="123 Test Street, District 1, HCMC",
            phone_number="0901234567",
            payment_method="CASH"  # Valid: CASH, BANK_TRANSFER, CREDIT_CARD
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert "placed successfully" in output.message
        assert output.order_id == 1
        assert output.total_amount > 0
        assert output.error_message == ""
        
        # Verify stock was reduced
        product_repository.save.assert_called()
        
        # Verify cart was cleared
        cart_repository.clear_cart.assert_called_once_with(user_id)
    
    def test_place_order_with_multiple_items_success(self, use_case, cart_repository, product_repository, order_repository):
        """Test 2: Đặt hàng thành công với nhiều sản phẩm"""
        # Arrange
        product1 = self.create_mock_product(10, "Camera A", 5000000, 10)
        product2 = self.create_mock_product(20, "Lens B", 3000000, 5)
        product3 = self.create_mock_product(30, "Tripod C", 500000, 20)
        
        cart_item1 = self.create_mock_cart_item(1, 1, 10, 2, product=product1)
        cart_item2 = self.create_mock_cart_item(2, 1, 20, 1, product=product2)
        cart_item3 = self.create_mock_cart_item(3, 1, 30, 3, product=product3)
        
        cart = Mock(cart_id=1, user_id=1)
        cart.items = [cart_item1, cart_item2, cart_item3]
        cart_repository.find_by_user_id.side_effect = lambda uid: cart if uid == 1 else None
        
        def find_by_id_side_effect(product_id):
            if product_id == 10: return product1
            elif product_id == 20: return product2
            elif product_id == 30: return product3
            return None
        
        product_repository.find_by_id.side_effect = find_by_id_side_effect
        
        mock_saved_order = Mock()
        mock_saved_order.id = 1
        mock_total = Mock()
        mock_total.amount = 14500000
        mock_saved_order.total = mock_total
        order_repository.save.return_value = mock_saved_order
        
        input_data = PlaceOrderInputData(
            user_id=1,
            shipping_address="123 Test Street, District 1, HCMC",
            phone_number="0901234567",
            payment_method="BANK_TRANSFER"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.order_id == 1
        
        # Verify stock was reduced for all products
        assert product_repository.save.call_count == 3
    
    def test_place_order_with_exact_stock_success(self, use_case, cart_repository, product_repository, order_repository):
        """Test 3: Đặt hàng với số lượng bằng đúng stock"""
        # Arrange
        product = self.create_mock_product(10, "Camera A", 5000000, 5)  # Stock exactly 5
        cart_item = self.create_mock_cart_item(1, 1, 10, 5, product=product)  # Order exactly 5
        
        cart = Mock(cart_id=1, user_id=1)
        cart.items = [cart_item]
        cart_repository.find_by_user_id.side_effect = lambda uid: cart if uid == 1 else None
        
        product_repository.find_by_id.return_value = product
        
        mock_saved_order = Mock()
        mock_saved_order.id = 1
        mock_total = Mock()
        mock_total.amount = 25000000
        mock_saved_order.total = mock_total
        order_repository.save.return_value = mock_saved_order
        
        input_data = PlaceOrderInputData(
            user_id=1,
            shipping_address="123 Test Street, District 1, HCMC",
            phone_number="0901234567",
            payment_method="CASH"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        # After reduce_stock(5), stock should be 0
        assert product.stock_quantity == 0
    
    def test_place_order_with_different_payment_methods_success(self, use_case, cart_repository, product_repository, order_repository):
        """Test 4: Đặt hàng với các phương thức thanh toán khác nhau"""
        # Test all valid payment methods
        product = self.create_mock_product(10, "Camera", 5000000, 10)
        cart_item = self.create_mock_cart_item(1, 1, 10, 1, product=product)
        
        cart = Mock(cart_id=1, user_id=1)
        cart.items = [cart_item]
        cart_repository.find_by_user_id.side_effect = lambda uid: cart if uid == 1 else None
        
        product_repository.find_by_id.return_value = product
        
        mock_saved_order = Mock()
        mock_saved_order.id = 1
        mock_total = Mock()
        mock_total.amount = 5000000
        mock_saved_order.total = mock_total
        order_repository.save.return_value = mock_saved_order
        
        # Valid payment methods: CASH, BANK_TRANSFER, CREDIT_CARD
        for payment_method in ["CASH", "BANK_TRANSFER", "CREDIT_CARD"]:
            # Reset product stock for each iteration
            product.stock_quantity = 10
            
            input_data = PlaceOrderInputData(
                user_id=1,
                shipping_address="123 Test Street, District 1",
                phone_number="0901234567",
                payment_method=payment_method
            )
            
            output = use_case.execute(input_data)
            assert output.success is True
    
    # ============ EMPTY CART ============
    
    def test_place_order_with_no_cart_fails(self, use_case, cart_repository, product_repository, order_repository):
        """Test 5: Đặt hàng khi user chưa có giỏ hàng"""
        # Arrange
        cart_repository.find_by_user_id.side_effect = lambda uid: None
        
        input_data = PlaceOrderInputData(
            user_id=1,
            shipping_address="123 Test Street, District 1",
            phone_number="0901234567",
            payment_method="CASH"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Cart is empty" in output.error_message or "Cart not found" in output.error_message
        order_repository.save.assert_not_called()
    
    def test_place_order_with_empty_cart_fails(self, use_case, cart_repository, product_repository, order_repository):
        """Test 6: Đặt hàng với giỏ hàng trống"""
        # Arrange
        cart = Mock(cart_id=1, user_id=1)
        cart.items = []  # Empty items list
        cart_repository.find_by_user_id.side_effect = lambda uid: cart if uid == 1 else None
        
        input_data = PlaceOrderInputData(
            user_id=1,
            shipping_address="123 Test Street, District 1",
            phone_number="0901234567",
            payment_method="CASH"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Cart is empty" in output.error_message
        order_repository.save.assert_not_called()
    
    # ============ STOCK VALIDATION ============
    
    def test_place_order_with_insufficient_stock_fails(self, use_case, cart_repository, product_repository, order_repository):
        """Test 7: Đặt hàng khi stock không đủ"""
        # Arrange
        product = self.create_mock_product(10, "Camera A", 5000000, 3)  # Only 3 available
        cart_item = self.create_mock_cart_item(1, 1, 10, 5, product=product)  # Want 5
        
        cart = Mock(cart_id=1, user_id=1)
        cart.items = [cart_item]
        cart_repository.find_by_user_id.side_effect = lambda uid: cart if uid == 1 else None
        
        product_repository.find_by_id.return_value = product
        
        input_data = PlaceOrderInputData(
            user_id=1,
            shipping_address="123 Test Street, District 1",
            phone_number="0901234567",
            payment_method="CASH"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        # InsufficientStockException format: "Product {id}: requested {qty}, but only {available} available"
        assert "requested" in output.error_message and "available" in output.error_message
        order_repository.save.assert_not_called()
        product_repository.save.assert_not_called()
    
    def test_place_order_with_out_of_stock_product_fails(self, use_case, cart_repository, product_repository, order_repository):
        """Test 8: Đặt hàng khi sản phẩm hết hàng (stock = 0)"""
        # Arrange
        product = self.create_mock_product(10, "Camera A", 5000000, 0)  # Out of stock
        cart_item = self.create_mock_cart_item(1, 1, 10, 1, product=product)
        
        cart = Mock(cart_id=1, user_id=1)
        cart.items = [cart_item]
        cart_repository.find_by_user_id.side_effect = lambda uid: cart if uid == 1 else None
        
        product_repository.find_by_id.return_value = product
        
        input_data = PlaceOrderInputData(
            user_id=1,
            shipping_address="123 Test Street, District 1",
            phone_number="0901234567",
            payment_method="CASH"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        # InsufficientStockException format: "Product {id}: requested {qty}, but only {available} available"
        assert "requested" in output.error_message.lower() and "available" in output.error_message.lower()
    
    def test_place_order_one_item_insufficient_stock_in_multiple_items_fails(self, use_case, cart_repository, product_repository, order_repository):
        """Test 9: Đặt hàng với nhiều items, 1 item không đủ stock"""
        # Arrange
        product1 = self.create_mock_product(10, "Camera A", 5000000, 10)  # Enough
        product2 = self.create_mock_product(20, "Lens B", 3000000, 5)  # Not enough (want 10, have 5)
        
        cart_item1 = self.create_mock_cart_item(1, 1, 10, 2, product=product1)  # OK
        cart_item2 = self.create_mock_cart_item(2, 1, 20, 10, product=product2)  # Insufficient
        
        cart = Mock(cart_id=1, user_id=1)
        cart.items = [cart_item1, cart_item2]
        cart_repository.find_by_user_id.side_effect = lambda uid: cart if uid == 1 else None
        
        def find_by_id_side_effect(product_id):
            if product_id == 10: return product1
            elif product_id == 20: return product2
            return None
        
        product_repository.find_by_id.side_effect = find_by_id_side_effect
        
        input_data = PlaceOrderInputData(
            user_id=1,
            shipping_address="123 Test Street, District 1",
            phone_number="0901234567",
            payment_method="CASH"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        # InsufficientStockException format: "Product {id}: requested {qty}, but only {available} available"
        assert "requested" in output.error_message.lower() and "available" in output.error_message.lower()
        order_repository.save.assert_not_called()
    
    # ============ PRODUCT VALIDATION ============
    
    def test_place_order_with_hidden_product_fails(self, use_case, cart_repository, product_repository, order_repository):
        """Test 10: Đặt hàng với sản phẩm bị ẩn"""
        # Arrange
        product = self.create_mock_product(10, "Camera A", 5000000, 10, is_visible=False)
        cart_item = self.create_mock_cart_item(1, 1, 10, 2, product=product)
        
        cart = Mock(cart_id=1, user_id=1)
        cart.items = [cart_item]
        cart_repository.find_by_user_id.side_effect = lambda uid: cart if uid == 1 else None
        
        product_repository.find_by_id.return_value = product
        
        input_data = PlaceOrderInputData(
            user_id=1,
            shipping_address="123 Test Street, District 1",
            phone_number="0901234567",
            payment_method="CASH"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "no longer available" in output.error_message.lower() or "not available" in output.error_message.lower()
    
    def test_place_order_with_deleted_product_fails(self, use_case, cart_repository, product_repository, order_repository):
        """Test 11: Đặt hàng với sản phẩm đã bị xóa"""
        # Arrange
        # Create cart item with product, but product_repository will return None
        from app.domain.value_objects.money import Money
        mock_product = Mock()
        mock_product.product_id = 999
        mock_product.price = Money(Decimal('5000000'), "VND")
        
        cart_item = self.create_mock_cart_item(1, 1, 999, 1, product=mock_product)
        
        cart = Mock(cart_id=1, user_id=1)
        cart.items = [cart_item]
        cart_repository.find_by_user_id.side_effect = lambda uid: cart if uid == 1 else None
        
        product_repository.find_by_id.return_value = None  # Product not found
        
        input_data = PlaceOrderInputData(
            user_id=1,
            shipping_address="123 Test Street, District 1",
            phone_number="0901234567",
            payment_method="CASH"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "not found" in output.error_message.lower()
    
    # ============ INPUT VALIDATION - SHIPPING ADDRESS ============
    
    def test_place_order_with_missing_shipping_address_fails(self, use_case, cart_repository, product_repository, order_repository):
        """Test 12: Đặt hàng thiếu địa chỉ giao hàng"""
        # Arrange
        input_data = PlaceOrderInputData(
            user_id=1,
            shipping_address="",
            phone_number="0901234567",
            payment_method="CASH"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Shipping address" in output.error_message
    
    def test_place_order_with_short_shipping_address_fails(self, use_case, cart_repository, product_repository, order_repository):
        """Test 13: Đặt hàng với địa chỉ quá ngắn (< 10 ký tự)"""
        # Arrange
        input_data = PlaceOrderInputData(
            user_id=1,
            shipping_address="Short",  # Only 5 chars
            phone_number="0901234567",
            payment_method="CASH"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Shipping address" in output.error_message
        assert "10 characters" in output.error_message
    
    def test_place_order_with_whitespace_only_address_fails(self, use_case, cart_repository, product_repository, order_repository):
        """Test 14: Đặt hàng với địa chỉ chỉ có khoảng trắng"""
        # Arrange
        input_data = PlaceOrderInputData(
            user_id=1,
            shipping_address="           ",  # Whitespace only
            phone_number="0901234567",
            payment_method="CASH"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Shipping address" in output.error_message
    
    # ============ INPUT VALIDATION - PHONE NUMBER ============
    
    def test_place_order_with_missing_phone_number_fails(self, use_case, cart_repository, product_repository, order_repository):
        """Test 15: Đặt hàng thiếu số điện thoại"""
        # Arrange
        input_data = PlaceOrderInputData(
            user_id=1,
            shipping_address="123 Test Street, District 1",
            phone_number="",
            payment_method="CASH"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Phone number" in output.error_message
    
    def test_place_order_with_short_phone_number_fails(self, use_case, cart_repository, product_repository, order_repository):
        """Test 16: Đặt hàng với số điện thoại quá ngắn (< 10 số)"""
        # Arrange
        input_data = PlaceOrderInputData(
            user_id=1,
            shipping_address="123 Test Street, District 1",
            phone_number="090123",  # Only 6 digits
            payment_method="CASH"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Phone number" in output.error_message
        assert "10 digits" in output.error_message
    
    def test_place_order_with_whitespace_only_phone_fails(self, use_case, cart_repository, product_repository, order_repository):
        """Test 17: Đặt hàng với số điện thoại chỉ có khoảng trắng"""
        # Arrange
        input_data = PlaceOrderInputData(
            user_id=1,
            shipping_address="123 Test Street, District 1",
            phone_number="     ",
            payment_method="CASH"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Phone number" in output.error_message
    
    # ============ INPUT VALIDATION - PAYMENT METHOD ============
    
    def test_place_order_with_missing_payment_method_fails(self, use_case, cart_repository, product_repository, order_repository):
        """Test 18: Đặt hàng thiếu phương thức thanh toán"""
        # Arrange
        input_data = PlaceOrderInputData(
            user_id=1,
            shipping_address="123 Test Street, District 1",
            phone_number="0901234567",
            payment_method=""
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Payment method" in output.error_message
    
    def test_place_order_with_none_payment_method_fails(self, use_case, cart_repository, product_repository, order_repository):
        """Test 19: Đặt hàng với payment method = None"""
        # Arrange
        input_data = PlaceOrderInputData(
            user_id=1,
            shipping_address="123 Test Street, District 1",
            phone_number="0901234567",
            payment_method=None
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Payment method" in output.error_message
    
    # ============ INPUT VALIDATION - USER ID ============
    
    def test_place_order_with_invalid_user_id_fails(self, use_case, cart_repository, product_repository, order_repository):
        """Test 20: Đặt hàng với user ID không hợp lệ (0)"""
        # Arrange
        input_data = PlaceOrderInputData(
            user_id=0,
            shipping_address="123 Test Street, District 1",
            phone_number="0901234567",
            payment_method="CASH"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Invalid user ID" in output.error_message
    
    def test_place_order_with_negative_user_id_fails(self, use_case, cart_repository, product_repository, order_repository):
        """Test 21: Đặt hàng với user ID âm"""
        # Arrange
        input_data = PlaceOrderInputData(
            user_id=-1,
            shipping_address="123 Test Street, District 1",
            phone_number="0901234567",
            payment_method="CASH"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "Invalid user ID" in output.error_message
    
    # ============ REPOSITORY EXCEPTIONS ============
    
    def test_repository_exception_handled(self, use_case, cart_repository, product_repository, order_repository):
        """Test 22: Lỗi từ repository được xử lý"""
        # Arrange
        cart_repository.find_by_user_id.side_effect = Exception("Database connection error")
        
        input_data = PlaceOrderInputData(
            user_id=1,
            shipping_address="123 Test Street, District 1",
            phone_number="0901234567",
            payment_method="CASH"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "An error occurred" in output.error_message
    
    def test_order_save_exception_handled(self, use_case, cart_repository, product_repository, order_repository):
        """Test 23: Lỗi khi save order được xử lý"""
        # Arrange
        product = self.create_mock_product(10, "Camera", 5000000, 10)
        cart_item = self.create_mock_cart_item(1, 1, 10, 1, product=product)
        
        cart = Mock(cart_id=1, user_id=1)
        cart.items = [cart_item]
        cart_repository.find_by_user_id.side_effect = lambda uid: cart if uid == 1 else None
        
        product_repository.find_by_id.return_value = product
        
        order_repository.save.side_effect = Exception("Failed to save order")
        
        input_data = PlaceOrderInputData(
            user_id=1,
            shipping_address="123 Test Street, District 1",
            phone_number="0901234567",
            payment_method="CASH"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "An error occurred" in output.error_message
    
    # ============ OUTPUT DATA STRUCTURE ============
    
    def test_output_data_structure_on_success(self, use_case, cart_repository, product_repository, order_repository):
        """Test 24: Cấu trúc output data khi thành công"""
        # Arrange
        product = self.create_mock_product(10, "Camera", 5000000, 10)
        cart_item = self.create_mock_cart_item(1, 1, 10, 1, product=product)
        
        cart = Mock(cart_id=1, user_id=1)
        cart.items = [cart_item]
        cart_repository.find_by_user_id.side_effect = lambda uid: cart if uid == 1 else None
        
        product_repository.find_by_id.return_value = product
        
        mock_saved_order = Mock()
        mock_saved_order.id = 123
        mock_total = Mock()
        mock_total.amount = 5000000
        mock_saved_order.total = mock_total
        order_repository.save.return_value = mock_saved_order
        
        input_data = PlaceOrderInputData(
            user_id=1,
            shipping_address="123 Test Street, District 1",
            phone_number="0901234567",
            payment_method="CASH"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert isinstance(output, PlaceOrderOutputData)
        assert hasattr(output, 'success')
        assert hasattr(output, 'message')
        assert hasattr(output, 'order_id')
        assert hasattr(output, 'total_amount')
        assert hasattr(output, 'error_message')
        
        assert output.success is True
        assert output.order_id == 123
        assert output.total_amount > 0
        assert len(output.message) > 0
        assert output.error_message == ""
    
    def test_output_data_structure_on_failure(self, use_case, cart_repository, product_repository, order_repository):
        """Test 25: Cấu trúc output data khi thất bại"""
        # Arrange
        cart_repository.find_by_user_id.side_effect = lambda uid: None
        
        input_data = PlaceOrderInputData(
            user_id=1,
            shipping_address="123 Test Street, District 1",
            phone_number="0901234567",
            payment_method="CASH"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert isinstance(output, PlaceOrderOutputData)
        assert output.success is False
        assert output.order_id is None
        assert output.total_amount == 0
        assert output.message == ""
        assert len(output.error_message) > 0
