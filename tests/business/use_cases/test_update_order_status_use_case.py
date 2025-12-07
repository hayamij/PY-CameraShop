"""
Test suite for UpdateOrderStatusUseCase

Test Coverage:
- Success cases: Valid status transitions
- Invalid transition cases: Cannot go backwards, skip states
- Terminal state cases: Cannot change completed/cancelled orders
- Validation cases: Invalid order ID, empty status, invalid status
- Not found cases: Order doesn't exist
- Repository exception cases
- Output structure validation
"""

import pytest
from unittest.mock import Mock
from datetime import datetime
from decimal import Decimal

from app.business.use_cases.update_order_status_use_case import (
    UpdateOrderStatusUseCase,
    UpdateOrderStatusInputData,
    UpdateOrderStatusOutputData
)
from app.domain.entities.order import Order, OrderItem
from app.domain.enums import OrderStatus, PaymentMethod
from app.domain.value_objects.money import Money
from app.domain.exceptions import (
    OrderNotFoundException,
    InvalidOrderStatusTransitionException,
    ValidationException
)


class TestUpdateOrderStatusUseCase:
    """Test cases for UpdateOrderStatusUseCase"""
    
    # ============ FIXTURES ============
    
    @pytest.fixture
    def order_repository(self):
        """Mock order repository"""
        return Mock()
    
    @pytest.fixture
    def use_case(self, order_repository):
        """Create use case instance"""
        return UpdateOrderStatusUseCase(order_repository)
    
    # ============ HELPER METHODS ============
    
    def create_mock_order(self, order_id, current_status):
        """Create mock order"""
        order = Mock()
        order.order_id = order_id  # Implementation uses order.order_id
        order.id = order_id
        order.status = current_status
        order.customer_id = 5
        order.payment_method = PaymentMethod.CASH
        order.shipping_address = "123 Test Street"
        
        def update_status(new_status):
            if not current_status.can_transition_to(new_status):
                raise InvalidOrderStatusTransitionException(
                    str(current_status),
                    str(new_status)
                )
            order.status = new_status
        
        order.update_status = update_status
        
        return order
    
    # ============ SUCCESS CASES - VALID TRANSITIONS ============
    
    def test_update_pending_to_shipping_success(self, use_case, order_repository):
        """Test updating order from PENDING to SHIPPING"""
        # Arrange
        order_id = 10
        order = self.create_mock_order(order_id, OrderStatus.PENDING)
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        
        input_data = UpdateOrderStatusInputData(order_id=order_id, new_status="DANG_GIAO")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.order_id == order_id
        assert output.old_status == "CHO_XAC_NHAN"
        assert output.new_status == "DANG_GIAO"
        assert "updated" in output.message.lower()
        assert order.status == OrderStatus.SHIPPING
        order_repository.save.assert_called_once_with(order)
    
    def test_update_pending_to_cancelled_success(self, use_case, order_repository):
        """Test updating order from PENDING to CANCELLED"""
        # Arrange
        order_id = 10
        order = self.create_mock_order(order_id, OrderStatus.PENDING)
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        
        input_data = UpdateOrderStatusInputData(order_id=order_id, new_status="DA_HUY")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.old_status == "CHO_XAC_NHAN"
        assert output.new_status == "DA_HUY"
        assert order.status == OrderStatus.CANCELLED
    
    def test_update_shipping_to_completed_success(self, use_case, order_repository):
        """Test updating order from SHIPPING to COMPLETED"""
        # Arrange
        order_id = 10
        order = self.create_mock_order(order_id, OrderStatus.SHIPPING)
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        
        input_data = UpdateOrderStatusInputData(order_id=order_id, new_status="HOAN_THANH")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.old_status == "DANG_GIAO"
        assert output.new_status == "HOAN_THANH"
        assert order.status == OrderStatus.COMPLETED
    
    def test_update_with_admin_notes(self, use_case, order_repository):
        """Test updating status with admin notes"""
        # Arrange
        order_id = 10
        order = self.create_mock_order(order_id, OrderStatus.PENDING)
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        
        input_data = UpdateOrderStatusInputData(
            order_id=order_id,
            new_status="DANG_GIAO",
            admin_notes="Package prepared for shipping"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
    
    def test_update_case_insensitive_status(self, use_case, order_repository):
        """Test status update is case insensitive"""
        # Arrange
        order_id = 10
        order = self.create_mock_order(order_id, OrderStatus.PENDING)
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        
        input_data = UpdateOrderStatusInputData(order_id=order_id, new_status="dang_giao")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.new_status == "DANG_GIAO"
    
    # ============ INVALID TRANSITION CASES ============
    
    def test_update_pending_to_completed_fails(self, use_case, order_repository):
        """Test cannot skip from PENDING directly to COMPLETED"""
        # Arrange
        order_id = 10
        order = self.create_mock_order(order_id, OrderStatus.PENDING)
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        
        input_data = UpdateOrderStatusInputData(order_id=order_id, new_status="HOAN_THANH")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "transition" in output.message.lower() or "invalid" in output.message.lower()
        assert order.status == OrderStatus.PENDING  # Status unchanged
        order_repository.save.assert_not_called()
    
    def test_update_shipping_to_cancelled_fails(self, use_case, order_repository):
        """Test cannot cancel shipping order"""
        # Arrange
        order_id = 10
        order = self.create_mock_order(order_id, OrderStatus.SHIPPING)
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        
        input_data = UpdateOrderStatusInputData(order_id=order_id, new_status="DA_HUY")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert order.status == OrderStatus.SHIPPING  # Status unchanged
        order_repository.save.assert_not_called()
    
    def test_update_shipping_to_pending_fails(self, use_case, order_repository):
        """Test cannot go backwards from SHIPPING to PENDING"""
        # Arrange
        order_id = 10
        order = self.create_mock_order(order_id, OrderStatus.SHIPPING)
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        
        input_data = UpdateOrderStatusInputData(order_id=order_id, new_status="CHO_XAC_NHAN")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert order.status == OrderStatus.SHIPPING
        order_repository.save.assert_not_called()
    
    # ============ TERMINAL STATE CASES ============
    
    def test_update_completed_to_any_status_fails(self, use_case, order_repository):
        """Test cannot change completed order status"""
        # Arrange
        order_id = 10
        order = self.create_mock_order(order_id, OrderStatus.COMPLETED)
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        
        statuses_to_try = ["CHO_XAC_NHAN", "DANG_GIAO", "DA_HUY"]
        
        for new_status in statuses_to_try:
            input_data = UpdateOrderStatusInputData(order_id=order_id, new_status=new_status)
            
            # Act
            output = use_case.execute(input_data)
            
            # Assert
            assert output.success is False, f"Should fail for status {new_status}"
            assert order.status == OrderStatus.COMPLETED
    
    def test_update_cancelled_to_any_status_fails(self, use_case, order_repository):
        """Test cannot change cancelled order status"""
        # Arrange
        order_id = 10
        order = self.create_mock_order(order_id, OrderStatus.CANCELLED)
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        
        statuses_to_try = ["CHO_XAC_NHAN", "DANG_GIAO", "HOAN_THANH"]
        
        for new_status in statuses_to_try:
            input_data = UpdateOrderStatusInputData(order_id=order_id, new_status=new_status)
            
            # Act
            output = use_case.execute(input_data)
            
            # Assert
            assert output.success is False, f"Should fail for status {new_status}"
            assert order.status == OrderStatus.CANCELLED
    
    # ============ VALIDATION CASES ============
    
    def test_update_with_invalid_order_id_zero_fails(self, use_case, order_repository):
        """Test with invalid order ID (zero)"""
        # Arrange
        input_data = UpdateOrderStatusInputData(order_id=0, new_status="DANG_GIAO")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "invalid order id" in output.message.lower()
        order_repository.find_by_id.assert_not_called()
    
    def test_update_with_negative_order_id_fails(self, use_case, order_repository):
        """Test with negative order ID"""
        # Arrange
        input_data = UpdateOrderStatusInputData(order_id=-1, new_status="DANG_GIAO")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "invalid order id" in output.message.lower()
        order_repository.find_by_id.assert_not_called()
    
    def test_update_with_empty_status_fails(self, use_case, order_repository):
        """Test with empty status"""
        # Arrange
        input_data = UpdateOrderStatusInputData(order_id=10, new_status="")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "required" in output.message.lower()
        order_repository.find_by_id.assert_not_called()
    
    def test_update_with_none_status_fails(self, use_case, order_repository):
        """Test with None status"""
        # Arrange
        input_data = UpdateOrderStatusInputData(order_id=10, new_status=None)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        order_repository.find_by_id.assert_not_called()
    
    def test_update_with_invalid_status_value_fails(self, use_case, order_repository):
        """Test with invalid status value"""
        # Arrange
        order_id = 10
        order = self.create_mock_order(order_id, OrderStatus.PENDING)
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        
        input_data = UpdateOrderStatusInputData(order_id=order_id, new_status="INVALID_STATUS")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "invalid status" in output.message.lower()
        order_repository.save.assert_not_called()
    
    # ============ NOT FOUND CASES ============
    
    def test_update_nonexistent_order_fails(self, use_case, order_repository):
        """Test updating non-existent order"""
        # Arrange
        order_id = 999
        
        order_repository.find_by_id.side_effect = lambda oid: None
        
        input_data = UpdateOrderStatusInputData(order_id=order_id, new_status="DANG_GIAO")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "not found" in output.message.lower()
        order_repository.save.assert_not_called()
    
    # ============ REPOSITORY EXCEPTION CASES ============
    
    def test_repository_exception_find_order(self, use_case, order_repository):
        """Test repository exception during find_by_id"""
        # Arrange
        order_id = 10
        
        order_repository.find_by_id.side_effect = Exception("Database connection error")
        
        input_data = UpdateOrderStatusInputData(order_id=order_id, new_status="DANG_GIAO")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "error" in output.message.lower()
    
    def test_repository_exception_save_order(self, use_case, order_repository):
        """Test repository exception during save"""
        # Arrange
        order_id = 10
        order = self.create_mock_order(order_id, OrderStatus.PENDING)
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        order_repository.save.side_effect = Exception("Database save error")
        
        input_data = UpdateOrderStatusInputData(order_id=order_id, new_status="DANG_GIAO")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "error" in output.message.lower()
    
    # ============ OUTPUT STRUCTURE VALIDATION ============
    
    def test_output_data_structure_on_success(self, use_case, order_repository):
        """Test output data structure on success"""
        # Arrange
        order_id = 10
        order = self.create_mock_order(order_id, OrderStatus.PENDING)
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        
        input_data = UpdateOrderStatusInputData(order_id=order_id, new_status="DANG_GIAO")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert hasattr(output, 'success')
        assert hasattr(output, 'order_id')
        assert hasattr(output, 'old_status')
        assert hasattr(output, 'new_status')
        assert hasattr(output, 'message')
        
        assert isinstance(output.success, bool)
        assert isinstance(output.order_id, int)
        assert isinstance(output.old_status, str)
        assert isinstance(output.new_status, str)
        assert isinstance(output.message, str)
    
    def test_output_data_structure_on_failure(self, use_case, order_repository):
        """Test output data structure on failure"""
        # Arrange
        order_id = 999
        
        order_repository.find_by_id.side_effect = lambda oid: None
        
        input_data = UpdateOrderStatusInputData(order_id=order_id, new_status="DANG_GIAO")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert hasattr(output, 'order_id')
        assert hasattr(output, 'message')
        assert isinstance(output.message, str)
        assert len(output.message) > 0
