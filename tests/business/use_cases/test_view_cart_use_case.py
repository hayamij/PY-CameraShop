"""
Unit Tests for ViewCartUseCase
Test mọi trường hợp xem giỏ hàng - chi tiết và đáng tin cậy
"""

import pytest
from unittest.mock import Mock
from decimal import Decimal

from app.business.use_cases.view_cart_use_case import (
    ViewCartUseCase,
    ViewCartOutputData,
    CartItemOutputData
)
from app.domain.exceptions import ValidationException
from app.domain.value_objects.money import Money


class TestViewCartUseCase:
    """Test suite cho ViewCartUseCase - test kỹ lưỡng mọi trường hợp"""
    
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
        return ViewCartUseCase(cart_repository, product_repository)
    
    def create_mock_product(self, product_id, name, price, stock=10, is_visible=True, image_url=None):
        """Helper tạo mock product"""
        product = Mock()
        product.id = product_id
        product.product_id = product_id
        product.name = name
        product.price = Money(Decimal(str(price)))  # Use Money value object
        product.stock_quantity = stock
        product.is_visible = is_visible
        product.image_url = image_url
        return product
    
    def create_mock_cart_item(self, cart_item_id, cart_id, product_id, quantity):
        """Helper tạo mock cart item"""
        item = Mock()
        item.cart_item_id = cart_item_id
        item.cart_id = cart_id
        item.product_id = product_id
        item.quantity = quantity
        return item
    
    def create_mock_cart(self, cart_id, user_id, items=None):
        """Helper tạo mock cart"""
        cart = Mock()
        cart.id = cart_id  # Cart entity uses .id
        cart.cart_id = cart_id
        cart.user_id = user_id
        cart.items = items or []
        return cart
    
    # ============ EMPTY CART ============
    
    def test_view_empty_cart_no_cart_exists(self, use_case, cart_repository, product_repository):
        """Test 1: Xem giỏ hàng khi chưa có cart"""
        # Arrange
        user_id = 1
        cart_repository.find_by_user_id.return_value = None
        
        # Act
        output = use_case.execute(user_id)
        
        # Assert
        assert output.success is True
        assert output.cart_id is None
        assert len(output.items) == 0
        assert output.total_items == 0
        assert output.subtotal == Decimal('0.00')
        assert output.tax == Decimal('0.00')
        assert output.shipping == Decimal('0.00')
        assert output.total == Decimal('0.00')
        assert output.error_message == ""
    
    def test_view_empty_cart_cart_exists_no_items(self, use_case, cart_repository, product_repository):
        """Test 2: Xem giỏ hàng có cart nhưng không có items"""
        # Arrange
        user_id = 1
        empty_cart = self.create_mock_cart(1, user_id, items=[])
        cart_repository.find_by_user_id.return_value = empty_cart
        
        # Act
        output = use_case.execute(user_id)
        
        # Assert
        assert output.success is True
        assert output.cart_id is None
        assert len(output.items) == 0
        assert output.total_items == 0
        assert output.subtotal == Decimal('0.00')
    
    # ============ CART WITH SINGLE ITEM ============
    
    def test_view_cart_with_single_item(self, use_case, cart_repository, product_repository):
        """Test 3: Xem giỏ có 1 sản phẩm"""
        # Arrange
        user_id = 1
        cart_item = self.create_mock_cart_item(1, 1, 10, 2)
        cart = self.create_mock_cart(1, user_id, [cart_item])
        cart_repository.find_by_user_id.return_value = cart
        
        product = self.create_mock_product(10, "Camera", 10000000, stock=20, image_url="/img/camera.jpg")
        product_repository.find_by_id.return_value = product
        
        # Act
        output = use_case.execute(user_id)
        
        # Assert
        assert output.success is True
        assert output.cart_id == 1
        assert len(output.items) == 1
        assert output.total_items == 1
        
        # Check item details
        item = output.items[0]
        assert item.cart_item_id == 1
        assert item.product_id == 10
        assert item.product_name == "Camera"
        assert item.product_image == "/img/camera.jpg"
        assert item.price == Decimal('10000000')
        assert item.currency == "VND"
        assert item.quantity == 2
        assert item.subtotal == Decimal('20000000')  # 10M * 2
        assert item.stock_available == 20
        assert item.is_available is True
        
        # Check totals
        assert output.subtotal == Decimal('20000000')
        assert output.tax == Decimal('2000000.00')  # 10% of subtotal
        assert output.shipping == Decimal('0.00')  # Free shipping (subtotal > 500)
        assert output.total == Decimal('22000000.00')
    
    # ============ CART WITH MULTIPLE ITEMS ============
    
    def test_view_cart_with_multiple_items(self, use_case, cart_repository, product_repository):
        """Test 4: Xem giỏ có nhiều sản phẩm"""
        # Arrange
        user_id = 1
        cart_item1 = self.create_mock_cart_item(1, 1, 10, 2)
        cart_item2 = self.create_mock_cart_item(2, 1, 20, 1)
        cart_item3 = self.create_mock_cart_item(3, 1, 30, 3)
        cart = self.create_mock_cart(1, user_id, [cart_item1, cart_item2, cart_item3])
        cart_repository.find_by_user_id.return_value = cart
        
        product1 = self.create_mock_product(10, "Camera", 5000000, stock=10)
        product2 = self.create_mock_product(20, "Lens", 3000000, stock=5)
        product3 = self.create_mock_product(30, "Tripod", 500000, stock=20)
        
        def mock_find_by_id(product_id):
            products = {10: product1, 20: product2, 30: product3}
            return products.get(product_id)
        
        product_repository.find_by_id.side_effect = mock_find_by_id
        
        # Act
        output = use_case.execute(user_id)
        
        # Assert
        assert output.success is True
        assert len(output.items) == 3
        assert output.total_items == 3
        
        # Subtotal = (5M*2) + (3M*1) + (500K*3) = 10M + 3M + 1.5M = 14.5M
        assert output.subtotal == Decimal('14500000')
        # Tax = 10% * 14.5M = 1.45M
        assert output.tax == Decimal('1450000.00')
        # Shipping = 0 (free, subtotal > 500)
        assert output.shipping == Decimal('0.00')
        # Total = 14.5M + 1.45M = 15,950,000
        assert output.total == Decimal('15950000.00')
    
    # ============ PRODUCT AVAILABILITY ============
    
    def test_view_cart_item_out_of_stock(self, use_case, cart_repository, product_repository):
        """Test 5: Item trong giỏ hết hàng"""
        # Arrange
        user_id = 1
        cart_item = self.create_mock_cart_item(1, 1, 10, 5)
        cart = self.create_mock_cart(1, user_id, [cart_item])
        cart_repository.find_by_user_id.return_value = cart
        
        product = self.create_mock_product(10, "Out of Stock Product", 1000000, stock=0)
        product_repository.find_by_id.return_value = product
        
        # Act
        output = use_case.execute(user_id)
        
        # Assert
        assert output.success is True
        item = output.items[0]
        assert item.stock_available == 0
        assert item.is_available is False  # Not available because stock < quantity
    
    def test_view_cart_item_insufficient_stock(self, use_case, cart_repository, product_repository):
        """Test 6: Stock không đủ cho quantity trong giỏ"""
        # Arrange
        user_id = 1
        cart_item = self.create_mock_cart_item(1, 1, 10, 10)
        cart = self.create_mock_cart(1, user_id, [cart_item])
        cart_repository.find_by_user_id.return_value = cart
        
        product = self.create_mock_product(10, "Low Stock Product", 1000000, stock=5)
        product_repository.find_by_id.return_value = product
        
        # Act
        output = use_case.execute(user_id)
        
        # Assert
        item = output.items[0]
        assert item.stock_available == 5
        assert item.is_available is False  # Not available: stock (5) < quantity (10)
    
    def test_view_cart_item_exact_stock(self, use_case, cart_repository, product_repository):
        """Test 7: Stock đúng bằng quantity trong giỏ"""
        # Arrange
        user_id = 1
        cart_item = self.create_mock_cart_item(1, 1, 10, 8)
        cart = self.create_mock_cart(1, user_id, [cart_item])
        cart_repository.find_by_user_id.return_value = cart
        
        product = self.create_mock_product(10, "Exact Stock Product", 1000000, stock=8)
        product_repository.find_by_id.return_value = product
        
        # Act
        output = use_case.execute(user_id)
        
        # Assert
        item = output.items[0]
        assert item.stock_available == 8
        assert item.is_available is True  # Available: stock (8) >= quantity (8)
    
    def test_view_cart_item_hidden_product(self, use_case, cart_repository, product_repository):
        """Test 8: Sản phẩm trong giỏ bị ẩn"""
        # Arrange
        user_id = 1
        cart_item = self.create_mock_cart_item(1, 1, 10, 2)
        cart = self.create_mock_cart(1, user_id, [cart_item])
        cart_repository.find_by_user_id.return_value = cart
        
        product = self.create_mock_product(10, "Hidden Product", 1000000, stock=20, is_visible=False)
        product_repository.find_by_id.return_value = product
        
        # Act
        output = use_case.execute(user_id)
        
        # Assert
        item = output.items[0]
        assert item.is_available is False  # Not available because product is hidden
    
    def test_view_cart_with_mixed_availability(self, use_case, cart_repository, product_repository):
        """Test 9: Giỏ có cả items available và unavailable"""
        # Arrange
        user_id = 1
        cart_item1 = self.create_mock_cart_item(1, 1, 10, 2)  # Available
        cart_item2 = self.create_mock_cart_item(2, 1, 20, 5)  # Out of stock
        cart_item3 = self.create_mock_cart_item(3, 1, 30, 3)  # Hidden
        cart = self.create_mock_cart(1, user_id, [cart_item1, cart_item2, cart_item3])
        cart_repository.find_by_user_id.return_value = cart
        
        product1 = self.create_mock_product(10, "Available", 1000000, stock=20, is_visible=True)
        product2 = self.create_mock_product(20, "Out of Stock", 2000000, stock=0, is_visible=True)
        product3 = self.create_mock_product(30, "Hidden", 500000, stock=10, is_visible=False)
        
        def mock_find_by_id(product_id):
            products = {10: product1, 20: product2, 30: product3}
            return products.get(product_id)
        
        product_repository.find_by_id.side_effect = mock_find_by_id
        
        # Act
        output = use_case.execute(user_id)
        
        # Assert
        assert len(output.items) == 3
        assert output.items[0].is_available is True   # Available product
        assert output.items[1].is_available is False  # Out of stock
        assert output.items[2].is_available is False  # Hidden
    
    # ============ SHIPPING CALCULATION ============
    
    def test_view_cart_with_free_shipping(self, use_case, cart_repository, product_repository):
        """Test 10: Miễn phí ship khi subtotal >= 500"""
        # Arrange
        user_id = 1
        cart_item = self.create_mock_cart_item(1, 1, 10, 1)
        cart = self.create_mock_cart(1, user_id, [cart_item])
        cart_repository.find_by_user_id.return_value = cart
        
        # Product price = 600 (>= 500 for free shipping)
        product = self.create_mock_product(10, "Expensive Camera", 600, stock=10)
        product_repository.find_by_id.return_value = product
        
        # Act
        output = use_case.execute(user_id)
        
        # Assert
        assert output.subtotal == Decimal('600')
        assert output.shipping == Decimal('0.00')  # Free shipping
        assert output.tax == Decimal('60.00')  # 10% of 600
        assert output.total == Decimal('660.00')  # 600 + 60 + 0
    
    def test_view_cart_with_standard_shipping(self, use_case, cart_repository, product_repository):
        """Test 11: Ship phí 20 khi subtotal < 500"""
        # Arrange
        user_id = 1
        cart_item = self.create_mock_cart_item(1, 1, 10, 1)
        cart = self.create_mock_cart(1, user_id, [cart_item])
        cart_repository.find_by_user_id.return_value = cart
        
        # Product price = 400 (< 500, standard shipping applies)
        product = self.create_mock_product(10, "Cheap Lens", 400, stock=10)
        product_repository.find_by_id.return_value = product
        
        # Act
        output = use_case.execute(user_id)
        
        # Assert
        assert output.subtotal == Decimal('400')
        assert output.shipping == Decimal('20.00')  # Standard shipping
        assert output.tax == Decimal('40.00')  # 10% of 400
        assert output.total == Decimal('460.00')  # 400 + 40 + 20
    
    def test_view_cart_at_free_shipping_threshold(self, use_case, cart_repository, product_repository):
        """Test 12: Subtotal đúng bằng threshold (500)"""
        # Arrange
        user_id = 1
        cart_item = self.create_mock_cart_item(1, 1, 10, 1)
        cart = self.create_mock_cart(1, user_id, [cart_item])
        cart_repository.find_by_user_id.return_value = cart
        
        # Product price = exactly 500
        product = self.create_mock_product(10, "Product", 500, stock=10)
        product_repository.find_by_id.return_value = product
        
        # Act
        output = use_case.execute(user_id)
        
        # Assert
        assert output.subtotal == Decimal('500')
        assert output.shipping == Decimal('0.00')  # Free shipping at threshold
    
    # ============ TAX CALCULATION ============
    
    def test_view_cart_tax_calculation_10_percent(self, use_case, cart_repository, product_repository):
        """Test 13: Thuế 10% được tính chính xác"""
        # Arrange
        user_id = 1
        cart_item = self.create_mock_cart_item(1, 1, 10, 1)
        cart = self.create_mock_cart(1, user_id, [cart_item])
        cart_repository.find_by_user_id.return_value = cart
        
        product = self.create_mock_product(10, "Product", 1000, stock=10)
        product_repository.find_by_id.return_value = product
        
        # Act
        output = use_case.execute(user_id)
        
        # Assert
        assert output.subtotal == Decimal('1000')
        assert output.tax == Decimal('100.00')  # Exactly 10%
    
    def test_view_cart_tax_rounding(self, use_case, cart_repository, product_repository):
        """Test 14: Thuế được làm tròn 2 chữ số thập phân"""
        # Arrange
        user_id = 1
        cart_item = self.create_mock_cart_item(1, 1, 10, 3)
        cart = self.create_mock_cart(1, user_id, [cart_item])
        cart_repository.find_by_user_id.return_value = cart
        
        # 333 * 3 = 999, tax = 99.9 rounded to 99.90
        product = self.create_mock_product(10, "Product", 333, stock=10)
        product_repository.find_by_id.return_value = product
        
        # Act
        output = use_case.execute(user_id)
        
        # Assert
        assert output.subtotal == Decimal('999')
        assert output.tax == Decimal('99.90')  # Rounded to 2 decimal places
    
    # ============ PRODUCT NOT FOUND ============
    
    def test_view_cart_with_deleted_product(self, use_case, cart_repository, product_repository):
        """Test 15: Sản phẩm trong giỏ đã bị xóa"""
        # Arrange
        user_id = 1
        cart_item = self.create_mock_cart_item(1, 1, 999, 2)
        cart = self.create_mock_cart(1, user_id, [cart_item])
        cart_repository.find_by_user_id.return_value = cart
        
        # Product not found
        product_repository.find_by_id.return_value = None
        
        # Act
        output = use_case.execute(user_id)
        
        # Assert
        assert output.success is True
        assert len(output.items) == 0  # Item not included in output
        assert output.total_items == 0
        assert output.subtotal == Decimal('0.00')
    
    # ============ INPUT VALIDATION ============
    
    def test_view_cart_with_zero_user_id_fails(self, use_case, cart_repository, product_repository):
        """Test 16: User ID = 0"""
        # Arrange
        user_id = 0
        
        # Act
        output = use_case.execute(user_id)
        
        # Assert
        assert output.success is False
        assert "Invalid user ID" in output.error_message
        cart_repository.find_by_user_id.assert_not_called()
    
    def test_view_cart_with_negative_user_id_fails(self, use_case, cart_repository, product_repository):
        """Test 17: User ID âm"""
        # Arrange
        user_id = -1
        
        # Act
        output = use_case.execute(user_id)
        
        # Assert
        assert output.success is False
        assert "Invalid user ID" in output.error_message
    
    # ============ REPOSITORY EXCEPTIONS ============
    
    def test_view_cart_repository_exception_handled(self, use_case, cart_repository, product_repository):
        """Test 18: Lỗi từ repository được xử lý"""
        # Arrange
        user_id = 1
        cart_repository.find_by_user_id.side_effect = Exception("Database connection error")
        
        # Act
        output = use_case.execute(user_id)
        
        # Assert
        assert output.success is False
        assert "An error occurred while viewing cart" in output.error_message
    
    # ============ OUTPUT DATA STRUCTURE ============
    
    def test_output_data_structure_complete(self, use_case, cart_repository, product_repository):
        """Test 19: Cấu trúc output data đầy đủ"""
        # Arrange
        user_id = 1
        cart_item = self.create_mock_cart_item(1, 1, 10, 2)
        cart = self.create_mock_cart(1, user_id, [cart_item])
        cart_repository.find_by_user_id.return_value = cart
        
        product = self.create_mock_product(10, "Product", 1000000, stock=10)
        product_repository.find_by_id.return_value = product
        
        # Act
        output = use_case.execute(user_id)
        
        # Assert
        assert isinstance(output, ViewCartOutputData)
        assert hasattr(output, 'success')
        assert hasattr(output, 'cart_id')
        assert hasattr(output, 'items')
        assert hasattr(output, 'total_items')
        assert hasattr(output, 'subtotal')
        assert hasattr(output, 'tax')
        assert hasattr(output, 'shipping')
        assert hasattr(output, 'total')
        assert hasattr(output, 'error_message')
        
        # Verify item structure
        assert isinstance(output.items, list)
        if output.items:
            item = output.items[0]
            assert isinstance(item, CartItemOutputData)
            assert hasattr(item, 'cart_item_id')
            assert hasattr(item, 'product_id')
            assert hasattr(item, 'product_name')
            assert hasattr(item, 'product_image')
            assert hasattr(item, 'price')
            assert hasattr(item, 'currency')
            assert hasattr(item, 'quantity')
            assert hasattr(item, 'subtotal')
            assert hasattr(item, 'stock_available')
            assert hasattr(item, 'is_available')
