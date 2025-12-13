"""
Test suite for GetOrderDetailUseCase

Test Coverage:
- Success cases: Get complete order details
- Not found cases: Order doesn't exist
- Validation cases: Invalid order ID
- Edge cases: Missing customer/product info
- Repository exception cases
- Output structure validation
"""

import pytest
from unittest.mock import Mock
from datetime import datetime
from decimal import Decimal

from app.business.use_cases.get_order_detail_use_case import (
    GetOrderDetailUseCase,
    GetOrderDetailOutputData,
    OrderDetailItemData
)
from app.domain.entities.order import Order, OrderItem
from app.domain.enums import OrderStatus, PaymentMethod
from app.domain.value_objects.money import Money
from app.domain.exceptions import OrderNotFoundException, ValidationException


class TestGetOrderDetailUseCase:
    """Test cases for GetOrderDetailUseCase"""
    
    # ============ FIXTURES ============
    
    @pytest.fixture
    def order_repository(self):
        """Mock order repository"""
        return Mock()
    
    @pytest.fixture
    def user_repository(self):
        """Mock user repository"""
        return Mock()
    
    @pytest.fixture
    def product_repository(self):
        """Mock product repository"""
        return Mock()
    
    @pytest.fixture
    def use_case(self, order_repository, user_repository, product_repository):
        """Create use case instance"""
        return GetOrderDetailUseCase(order_repository, user_repository, product_repository)
    
    # ============ HELPER METHODS ============
    
    def create_mock_order(self, order_id, customer_id, status, item_count=2):
        """Create mock order with real Money objects"""
        order = Mock()
        order.order_id = order_id  # Implementation uses order.order_id
        order.id = order_id
        order.customer_id = customer_id
        order.status = status
        order.payment_method = PaymentMethod.CASH
        order.shipping_address = "123 Test Street, District 1, HCMC"
        order.phone_number = "0901234567"  # Required by Order entity
        order.notes = "Test order notes"  # Required by Order entity
        order.order_date = datetime(2025, 12, 1, 10, 30, 0)  # Implementation uses order_date
        order.created_at = datetime(2025, 12, 1, 10, 30, 0)
        
        # Create order items with real Money objects
        items = []
        for i in range(item_count):
            item = Mock()
            item.product_id = i + 1
            item.product_name = f"Product {i + 1}"
            item.quantity = 2
            item.unit_price = Money(Decimal("1000000"), "VND")  # Use Money object
            items.append(item)
        
        order.items = items
        return order
    
    def create_mock_user(self, user_id, full_name, email, phone):
        """Create mock user"""
        from app.domain.value_objects.email import Email
        user = Mock()
        user.id = user_id
        user.full_name = full_name
        user.email = Email(email)  # Use real Email value object
        user.phone_number = phone
        return user
    
    def create_mock_product(self, product_id, name, image_url=None):
        """Create mock product"""
        product = Mock()
        product.product_id = product_id
        product.name = name
        product.image_url = image_url
        return product
    
    # ============ SUCCESS CASES ============
    
    def test_get_order_detail_success(self, use_case, order_repository, user_repository, product_repository):
        """Test successfully getting order details"""
        # Arrange
        order_id = 10
        customer_id = 5

        order = self.create_mock_order(order_id, customer_id, OrderStatus.PENDING, item_count=2)
        user = self.create_mock_user(customer_id, "John Doe", "john@example.com", "0901234567")
        product1 = self.create_mock_product(1, "Camera A", "camera_a.jpg")
        product2 = self.create_mock_product(2, "Lens B", "lens_b.jpg")
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        user_repository.find_by_id.side_effect = lambda uid: user if uid == customer_id else None
        product_repository.find_by_id.side_effect = lambda pid: {1: product1, 2: product2}.get(pid)
        
        # Act
        output = use_case.execute(order_id)
        
        # Debug
        if not output.success:
            print(f"ERROR: {output.message}")
        
        # Assert
        assert output.success is True
        assert output.order_id == order_id
        assert output.customer_id == customer_id
        assert output.customer_name == "John Doe"
        assert output.customer_email == "john@example.com"
        assert output.customer_phone == "0901234567"
        assert output.status == "CHO_XAC_NHAN"
        assert output.payment_method == "TIEN_MAT"
        assert output.shipping_address == "123 Test Street, District 1, HCMC"
        assert len(output.items) == 2
        assert output.items[0].product_name == "Camera A"
        assert output.items[1].product_name == "Lens B"
        order_repository.find_by_id.assert_called_once_with(order_id)
    
    def test_get_order_detail_with_single_item(self, use_case, order_repository, user_repository, product_repository):
        """Test getting order with single item"""
        # Arrange
        order_id = 10
        customer_id = 5
        
        order = self.create_mock_order(order_id, customer_id, OrderStatus.SHIPPING, item_count=1)
        user = self.create_mock_user(customer_id, "Jane Smith", "jane@example.com", "0909876543")
        product = self.create_mock_product(1, "Tripod", "tripod.jpg")
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        user_repository.find_by_id.side_effect = lambda uid: user if uid == customer_id else None
        product_repository.find_by_id.side_effect = lambda pid: product if pid == 1 else None
        
        # Act
        output = use_case.execute(order_id)
        
        # Assert
        assert output.success is True
        assert len(output.items) == 1
        assert output.items[0].product_name == "Tripod"
        assert output.items[0].product_image == "tripod.jpg"
        assert output.status == "DANG_GIAO"
    
    def test_get_order_detail_with_multiple_items(self, use_case, order_repository, user_repository, product_repository):
        """Test getting order with multiple items"""
        # Arrange
        order_id = 10
        customer_id = 5
        
        order = self.create_mock_order(order_id, customer_id, OrderStatus.COMPLETED, item_count=5)
        user = self.create_mock_user(customer_id, "Bob Wilson", "bob@example.com", "0908765432")
        products = {i: self.create_mock_product(i, f"Product {i}", f"product_{i}.jpg") for i in range(1, 6)}
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        user_repository.find_by_id.side_effect = lambda uid: user if uid == customer_id else None
        product_repository.find_by_id.side_effect = lambda pid: products.get(pid)
        
        # Act
        output = use_case.execute(order_id)
        
        # Assert
        assert output.success is True
        assert len(output.items) == 5
        assert output.status == "HOAN_THANH"
        assert all(item.product_name.startswith("Product") for item in output.items)
    
    def test_get_order_detail_with_different_statuses(self, use_case, order_repository, user_repository, product_repository):
        """Test getting orders with different statuses"""
        # Arrange
        customer_id = 5
        user = self.create_mock_user(customer_id, "Test User", "test@example.com", "0901234567")
        product = self.create_mock_product(1, "Camera", "camera.jpg")
        
        user_repository.find_by_id.side_effect = lambda uid: user if uid == customer_id else None
        product_repository.find_by_id.side_effect = lambda pid: product if pid == 1 else None
        
        statuses = [
            (OrderStatus.PENDING, "CHO_XAC_NHAN"),
            (OrderStatus.SHIPPING, "DANG_GIAO"),
            (OrderStatus.COMPLETED, "HOAN_THANH"),
            (OrderStatus.CANCELLED, "DA_HUY")
        ]
        
        for order_status, expected_value in statuses:
            order = self.create_mock_order(10, customer_id, order_status, item_count=1)
            order_repository.find_by_id.side_effect = lambda oid: order if oid == 10 else None
            
            # Act
            output = use_case.execute(10)
            
            # Assert
            assert output.success is True
            assert output.status == expected_value, f"Failed for status {order_status}"
    
    def test_get_order_detail_with_different_payment_methods(self, use_case, order_repository, user_repository, product_repository):
        """Test getting orders with different payment methods"""
        # Arrange
        customer_id = 5
        user = self.create_mock_user(customer_id, "Test User", "test@example.com", "0901234567")
        product = self.create_mock_product(1, "Camera", "camera.jpg")
        
        user_repository.find_by_id.side_effect = lambda uid: user if uid == customer_id else None
        product_repository.find_by_id.side_effect = lambda pid: product if pid == 1 else None
        
        payment_methods = [
            (PaymentMethod.CASH, "TIEN_MAT"),
            (PaymentMethod.BANK_TRANSFER, "BANK_TRANSFER"),
            (PaymentMethod.CREDIT_CARD, "CREDIT_CARD")
        ]
        
        for payment_method, expected_value in payment_methods:
            order = self.create_mock_order(10, customer_id, OrderStatus.PENDING, item_count=1)
            order.payment_method = payment_method
            order_repository.find_by_id.side_effect = lambda oid: order if oid == 10 else None
            
            # Act
            output = use_case.execute(10)
            
            # Assert
            assert output.success is True
            assert output.payment_method == expected_value
    
    # ============ NOT FOUND CASES ============
    
    def test_get_order_detail_order_not_found(self, use_case, order_repository, user_repository, product_repository):
        """Test getting non-existent order"""
        # Arrange
        order_id = 999
        order_repository.find_by_id.side_effect = lambda oid: None
        
        # Act
        output = use_case.execute(order_id)
        
        # Assert
        assert output.success is False
        assert "not found" in output.message.lower()
        order_repository.find_by_id.assert_called_once_with(order_id)
    
    def test_get_order_detail_customer_not_found(self, use_case, order_repository, user_repository, product_repository):
        """Test order with non-existent customer"""
        # Arrange
        order_id = 10
        customer_id = 999
        
        order = self.create_mock_order(order_id, customer_id, OrderStatus.PENDING, item_count=1)
        product = self.create_mock_product(1, "Camera", "camera.jpg")
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        user_repository.find_by_id.side_effect = lambda uid: None
        product_repository.find_by_id.side_effect = lambda pid: product if pid == 1 else None
        
        # Act
        output = use_case.execute(order_id)
        
        # Assert
        assert output.success is True
        assert output.customer_name == "Unknown"
        assert output.customer_email == ""
        assert output.customer_phone == ""
    
    def test_get_order_detail_product_not_found(self, use_case, order_repository, user_repository, product_repository):
        """Test order with non-existent product"""
        # Arrange
        order_id = 10
        customer_id = 5
        
        order = self.create_mock_order(order_id, customer_id, OrderStatus.PENDING, item_count=1)
        user = self.create_mock_user(customer_id, "Test User", "test@example.com", "0901234567")
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        user_repository.find_by_id.side_effect = lambda uid: user if uid == customer_id else None
        product_repository.find_by_id.side_effect = lambda pid: None
        
        # Act
        output = use_case.execute(order_id)
        
        # Assert
        assert output.success is True
        assert output.items[0].product_name == "Product Not Found"
        assert output.items[0].product_image is None
    
    # ============ VALIDATION CASES ============
    
    def test_get_order_detail_with_invalid_order_id_zero(self, use_case, order_repository):
        """Test with invalid order ID (zero)"""
        # Arrange
        order_id = 0
        
        # Act
        output = use_case.execute(order_id)
        
        # Assert
        assert output.success is False
        assert "invalid order id" in output.message.lower()
        order_repository.find_by_id.assert_not_called()
    
    def test_get_order_detail_with_negative_order_id(self, use_case, order_repository):
        """Test with negative order ID"""
        # Arrange
        order_id = -1
        
        # Act
        output = use_case.execute(order_id)
        
        # Assert
        assert output.success is False
        assert "invalid order id" in output.message.lower()
        order_repository.find_by_id.assert_not_called()
    
    # ============ REPOSITORY EXCEPTION CASES ============
    
    def test_repository_exception_order_repository(self, use_case, order_repository):
        """Test repository exception from order_repository"""
        # Arrange
        order_id = 10
        order_repository.find_by_id.side_effect = Exception("Database connection error")
        
        # Act
        output = use_case.execute(order_id)
        
        # Assert
        assert output.success is False
        assert "error" in output.message.lower()
    
    def test_repository_exception_user_repository(self, use_case, order_repository, user_repository, product_repository):
        """Test repository exception from user_repository"""
        # Arrange
        order_id = 10
        customer_id = 5
        
        order = self.create_mock_order(order_id, customer_id, OrderStatus.PENDING, item_count=1)
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        user_repository.find_by_id.side_effect = Exception("User database error")
        
        # Act
        output = use_case.execute(order_id)
        
        # Assert
        assert output.success is False
        assert "error" in output.message.lower()
    
    def test_repository_exception_product_repository(self, use_case, order_repository, user_repository, product_repository):
        """Test repository exception from product_repository"""
        # Arrange
        order_id = 10
        customer_id = 5
        
        order = self.create_mock_order(order_id, customer_id, OrderStatus.PENDING, item_count=1)
        user = self.create_mock_user(customer_id, "Test User", "test@example.com", "0901234567")
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        user_repository.find_by_id.side_effect = lambda uid: user if uid == customer_id else None
        product_repository.find_by_id.side_effect = Exception("Product database error")
        
        # Act
        output = use_case.execute(order_id)
        
        # Assert
        assert output.success is False
        assert "error" in output.message.lower()
    
    # ============ OUTPUT STRUCTURE VALIDATION ============
    
    def test_output_data_structure_complete(self, use_case, order_repository, user_repository, product_repository):
        """Test output data has all required fields"""
        # Arrange
        order_id = 10
        customer_id = 5
        
        order = self.create_mock_order(order_id, customer_id, OrderStatus.PENDING, item_count=2)
        user = self.create_mock_user(customer_id, "John Doe", "john@example.com", "0901234567")
        product1 = self.create_mock_product(1, "Camera A", "camera_a.jpg")
        product2 = self.create_mock_product(2, "Lens B", "lens_b.jpg")
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        user_repository.find_by_id.side_effect = lambda uid: user if uid == customer_id else None
        product_repository.find_by_id.side_effect = lambda pid: {1: product1, 2: product2}.get(pid)
        
        # Act
        output = use_case.execute(order_id)
        
        # Assert - Output structure
        assert hasattr(output, 'success')
        assert hasattr(output, 'order_id')
        assert hasattr(output, 'order_date')
        assert hasattr(output, 'status')
        assert hasattr(output, 'customer_id')
        assert hasattr(output, 'customer_name')
        assert hasattr(output, 'customer_email')
        assert hasattr(output, 'customer_phone')
        assert hasattr(output, 'shipping_address')
        assert hasattr(output, 'payment_method')
        assert hasattr(output, 'items')
        assert hasattr(output, 'subtotal')
        assert hasattr(output, 'tax')
        assert hasattr(output, 'shipping_fee')
        assert hasattr(output, 'total_amount')
        
        # Assert - Order item structure
        item = output.items[0]
        assert hasattr(item, 'product_id')
        assert hasattr(item, 'product_name')
        assert hasattr(item, 'product_image')
        assert hasattr(item, 'quantity')
        assert hasattr(item, 'unit_price')
        assert hasattr(item, 'subtotal')
        
        # Assert - Values are correct types
        assert isinstance(output.success, bool)
        assert isinstance(output.order_id, int)
        assert isinstance(output.customer_id, int)
        assert isinstance(output.items, list)
        assert isinstance(item.product_id, int)
        assert isinstance(item.quantity, int)
    
    def test_output_data_structure_on_failure(self, use_case, order_repository):
        """Test output structure on failure"""
        # Arrange
        order_id = 999
        order_repository.find_by_id.side_effect = lambda oid: None
        
        # Act
        output = use_case.execute(order_id)
        
        # Assert
        assert output.success is False
        assert hasattr(output, 'message')
        assert isinstance(output.message, str)
        assert len(output.message) > 0
