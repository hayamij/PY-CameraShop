"""
Test suite for GetMyOrdersUseCase

Test Coverage:
- Success cases: Orders retrieval with/without filters
- Empty cases: No orders found
- Filter cases: Status filtering
- Validation cases: Invalid user ID
- Repository exception cases
- Output structure validation
"""

import pytest
from unittest.mock import Mock
from datetime import datetime
from decimal import Decimal

from app.business.use_cases.get_my_orders_use_case import (
    GetMyOrdersUseCase,
    GetMyOrdersInputData,
    GetMyOrdersOutputData
)
from app.domain.entities.order import Order, OrderItem
from app.domain.enums import OrderStatus, PaymentMethod
from app.domain.value_objects.money import Money
from app.domain.exceptions import ValidationException


class TestGetMyOrdersUseCase:
    """Test cases for GetMyOrdersUseCase"""
    
    # ============ FIXTURES ============
    
    @pytest.fixture
    def order_repository(self):
        """Mock order repository"""
        return Mock()
    
    @pytest.fixture
    def use_case(self, order_repository):
        """Create use case instance"""
        return GetMyOrdersUseCase(order_repository)
    
    # ============ HELPER METHODS ============
    
    def create_mock_order(self, order_id, customer_id, status, item_count=2, total_amount=10000000):
        """Create a mock order with real Money object"""
        order = Mock()
        order.id = order_id
        order.customer_id = customer_id
        order.status = status
        order.payment_method = PaymentMethod.CASH
        order.shipping_address = "123 Test Street, District 1, HCMC"
        order.phone_number = "0901234567"
        order.notes = "Test notes"
        order.created_at = datetime(2025, 12, 1, 10, 30, 0)
        
        # CRITICAL: Use real Money object with total_amount property
        order.total_amount = Money(Decimal(str(total_amount)), "VND")
        
        # Create mock items
        items = []
        for i in range(item_count):
            item = Mock()
            item.product_id = i + 1
            item.product_name = f"Product {i + 1}"
            item.quantity = 1
            item.unit_price = Money(Decimal(str(total_amount // item_count)), "VND")
            items.append(item)
        
        order.items = items
        return order
    
    # ============ SUCCESS CASES ============
    
    def test_get_my_orders_no_orders_success(self, use_case, order_repository):
        """Test retrieving orders when user has no orders"""
        # Arrange
        user_id = 1
        order_repository.find_by_customer_id.side_effect = lambda uid: [] if uid == user_id else None
        input_data = GetMyOrdersInputData(user_id=user_id)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.orders == []
        assert output.total_orders == 0
        assert "0 order(s)" in output.message.lower()
        order_repository.find_by_customer_id.assert_called_once_with(user_id)
    
    def test_get_my_orders_single_order_success(self, use_case, order_repository):
        """Test retrieving single order"""
        # Arrange
        user_id = 1
        order = self.create_mock_order(10, user_id, OrderStatus.PENDING, item_count=2, total_amount=5000000)
        order_repository.find_by_customer_id.side_effect = lambda uid: [order] if uid == user_id else []
        input_data = GetMyOrdersInputData(user_id=user_id)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.orders) == 1
        assert output.total_orders == 1
        assert output.orders[0].order_id == 10
        assert output.orders[0].total_amount == 5000000
        assert output.orders[0].status == "CHO_XAC_NHAN"
        assert output.orders[0].item_count == 2
        assert output.orders[0].payment_method == "TIEN_MAT"
        assert output.orders[0].shipping_address == "123 Test Street, District 1, HCMC"
        assert output.orders[0].phone_number == "0901234567"
        assert output.orders[0].created_at == "2025-12-01 10:30:00"
        order_repository.find_by_customer_id.assert_called_once_with(user_id)
    
    def test_get_my_orders_multiple_orders_success(self, use_case, order_repository):
        """Test retrieving multiple orders"""
        # Arrange
        user_id = 1
        order1 = self.create_mock_order(10, user_id, OrderStatus.PENDING, item_count=2, total_amount=5000000)
        order2 = self.create_mock_order(11, user_id, OrderStatus.SHIPPING, item_count=3, total_amount=8000000)
        order3 = self.create_mock_order(12, user_id, OrderStatus.COMPLETED, item_count=1, total_amount=3000000)
        
        order_repository.find_by_customer_id.side_effect = lambda uid: [order1, order2, order3] if uid == user_id else []
        input_data = GetMyOrdersInputData(user_id=user_id)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.orders) == 3
        assert output.total_orders == 3
        
        # Order 1
        assert output.orders[0].order_id == 10
        assert output.orders[0].status == "CHO_XAC_NHAN"
        assert output.orders[0].item_count == 2
        
        # Order 2
        assert output.orders[1].order_id == 11
        assert output.orders[1].status == "DANG_GIAO"
        assert output.orders[1].item_count == 3
        
        # Order 3
        assert output.orders[2].order_id == 12
        assert output.orders[2].status == "HOAN_THANH"
        assert output.orders[2].item_count == 1
    
    def test_get_my_orders_with_different_payment_methods(self, use_case, order_repository):
        """Test orders with different payment methods"""
        # Arrange
        user_id = 1
        order1 = self.create_mock_order(10, user_id, OrderStatus.PENDING)
        order1.payment_method = PaymentMethod.CASH
        
        order2 = self.create_mock_order(11, user_id, OrderStatus.PENDING)
        order2.payment_method = PaymentMethod.BANK_TRANSFER
        
        order3 = self.create_mock_order(12, user_id, OrderStatus.PENDING)
        order3.payment_method = PaymentMethod.CREDIT_CARD
        
        order_repository.find_by_customer_id.side_effect = lambda uid: [order1, order2, order3] if uid == user_id else []
        input_data = GetMyOrdersInputData(user_id=user_id)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.orders[0].payment_method == "TIEN_MAT"
        assert output.orders[1].payment_method == "BANK_TRANSFER"
        assert output.orders[2].payment_method == "CREDIT_CARD"
    
    # ============ FILTER CASES ============
    
    def test_get_my_orders_filter_by_pending_status(self, use_case, order_repository):
        """Test filtering orders by PENDING status"""
        # Arrange
        user_id = 1
        order1 = self.create_mock_order(10, user_id, OrderStatus.PENDING)
        order2 = self.create_mock_order(11, user_id, OrderStatus.PENDING)
        
        order_repository.find_by_user_and_status.side_effect = lambda uid, status: [order1, order2] if uid == user_id and status == "CHO_XAC_NHAN" else []
        input_data = GetMyOrdersInputData(user_id=user_id, status_filter="CHO_XAC_NHAN")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.orders) == 2
        assert all(order.status == "CHO_XAC_NHAN" for order in output.orders)
        order_repository.find_by_user_and_status.assert_called_once_with(user_id, "CHO_XAC_NHAN")
    
    def test_get_my_orders_filter_by_shipping_status(self, use_case, order_repository):
        """Test filtering orders by SHIPPING status"""
        # Arrange
        user_id = 1
        order = self.create_mock_order(10, user_id, OrderStatus.SHIPPING)
        
        order_repository.find_by_user_and_status.side_effect = lambda uid, status: [order] if uid == user_id and status == "DANG_GIAO" else []
        input_data = GetMyOrdersInputData(user_id=user_id, status_filter="DANG_GIAO")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.orders) == 1
        assert output.orders[0].status == "DANG_GIAO"
        order_repository.find_by_user_and_status.assert_called_once_with(user_id, "DANG_GIAO")
    
    def test_get_my_orders_filter_by_completed_status(self, use_case, order_repository):
        """Test filtering orders by COMPLETED status"""
        # Arrange
        user_id = 1
        order = self.create_mock_order(10, user_id, OrderStatus.COMPLETED)
        
        order_repository.find_by_user_and_status.side_effect = lambda uid, status: [order] if uid == user_id and status == "HOAN_THANH" else []
        input_data = GetMyOrdersInputData(user_id=user_id, status_filter="HOAN_THANH")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.orders) == 1
        assert output.orders[0].status == "HOAN_THANH"
    
    def test_get_my_orders_filter_by_cancelled_status(self, use_case, order_repository):
        """Test filtering orders by CANCELLED status"""
        # Arrange
        user_id = 1
        order = self.create_mock_order(10, user_id, OrderStatus.CANCELLED)
        
        order_repository.find_by_user_and_status.side_effect = lambda uid, status: [order] if uid == user_id and status == "DA_HUY" else []
        input_data = GetMyOrdersInputData(user_id=user_id, status_filter="DA_HUY")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.orders) == 1
        assert output.orders[0].status == "DA_HUY"
    
    def test_get_my_orders_filter_returns_empty(self, use_case, order_repository):
        """Test filtering returns no results"""
        # Arrange
        user_id = 1
        order_repository.find_by_user_and_status.side_effect = lambda uid, status: []
        input_data = GetMyOrdersInputData(user_id=user_id, status_filter="HOAN_THANH")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.orders) == 0
        assert output.total_orders == 0
    
    # ============ VALIDATION CASES ============
    
    def test_get_my_orders_with_invalid_user_id_zero_fails(self, use_case, order_repository):
        """Test with invalid user ID (zero)"""
        # Arrange
        input_data = GetMyOrdersInputData(user_id=0)
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            use_case.execute(input_data)
        
        assert "invalid user id" in str(exc_info.value).lower()
        order_repository.find_by_customer_id.assert_not_called()
    
    def test_get_my_orders_with_negative_user_id_fails(self, use_case, order_repository):
        """Test with negative user ID"""
        # Arrange
        input_data = GetMyOrdersInputData(user_id=-1)
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            use_case.execute(input_data)
        
        assert "invalid user id" in str(exc_info.value).lower()
        order_repository.find_by_customer_id.assert_not_called()
    
    # ============ EDGE CASES ============
    
    def test_get_my_orders_with_zero_item_count(self, use_case, order_repository):
        """Test order with zero items (edge case - shouldn't happen but test anyway)"""
        # Arrange
        user_id = 1
        order = self.create_mock_order(10, user_id, OrderStatus.PENDING, item_count=0)
        
        order_repository.find_by_customer_id.side_effect = lambda uid: [order] if uid == user_id else []
        input_data = GetMyOrdersInputData(user_id=user_id)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.orders[0].item_count == 0
    
    def test_get_my_orders_with_large_number_of_orders(self, use_case, order_repository):
        """Test retrieving large number of orders"""
        # Arrange
        user_id = 1
        orders = [self.create_mock_order(i, user_id, OrderStatus.PENDING) for i in range(1, 51)]
        
        order_repository.find_by_customer_id.side_effect = lambda uid: orders if uid == user_id else []
        input_data = GetMyOrdersInputData(user_id=user_id)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.orders) == 50
        assert output.total_orders == 50
    
    # ============ REPOSITORY EXCEPTION CASES ============
    
    def test_repository_exception_find_by_customer_id(self, use_case, order_repository):
        """Test repository exception during find_by_customer_id"""
        # Arrange
        user_id = 1
        order_repository.find_by_customer_id.side_effect = Exception("Database connection error")
        input_data = GetMyOrdersInputData(user_id=user_id)
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            use_case.execute(input_data)
        
        assert "database connection error" in str(exc_info.value).lower()
    
    def test_repository_exception_find_by_user_and_status(self, use_case, order_repository):
        """Test repository exception during find_by_user_and_status"""
        # Arrange
        user_id = 1
        order_repository.find_by_user_and_status.side_effect = Exception("Database connection error")
        input_data = GetMyOrdersInputData(user_id=user_id, status_filter="CHO_XAC_NHAN")
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            use_case.execute(input_data)
        
        assert "database connection error" in str(exc_info.value).lower()
    
    # ============ OUTPUT STRUCTURE VALIDATION ============
    
    def test_output_data_structure_complete(self, use_case, order_repository):
        """Test output data has all required fields"""
        # Arrange
        user_id = 1
        order = self.create_mock_order(10, user_id, OrderStatus.PENDING, item_count=3, total_amount=7500000)
        order_repository.find_by_customer_id.side_effect = lambda uid: [order] if uid == user_id else []
        input_data = GetMyOrdersInputData(user_id=user_id)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert - Output structure
        assert hasattr(output, 'success')
        assert hasattr(output, 'orders')
        assert hasattr(output, 'total_orders')
        assert hasattr(output, 'message')
        
        # Assert - Order item structure
        order_item = output.orders[0]
        assert hasattr(order_item, 'order_id')
        assert hasattr(order_item, 'total_amount')
        assert hasattr(order_item, 'status')
        assert hasattr(order_item, 'payment_method')
        assert hasattr(order_item, 'shipping_address')
        assert hasattr(order_item, 'phone_number')
        assert hasattr(order_item, 'notes')
        assert hasattr(order_item, 'created_at')
        assert hasattr(order_item, 'item_count')
        
        # Assert - Values are correct types
        assert isinstance(output.success, bool)
        assert isinstance(output.orders, list)
        assert isinstance(output.total_orders, int)
        assert isinstance(output.message, str)
        assert isinstance(order_item.order_id, int)
        assert isinstance(order_item.total_amount, (int, float, Decimal))
        assert isinstance(order_item.status, str)
        assert isinstance(order_item.item_count, int)
    
    def test_output_data_structure_empty_orders(self, use_case, order_repository):
        """Test output structure when no orders found"""
        # Arrange
        user_id = 1
        order_repository.find_by_customer_id.side_effect = lambda uid: []
        input_data = GetMyOrdersInputData(user_id=user_id)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert isinstance(output.orders, list)
        assert len(output.orders) == 0
        assert output.total_orders == 0
        assert isinstance(output.message, str)
