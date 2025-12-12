"""
Test suite for CancelOrderUseCase

Test Coverage:
- Success cases: Cancel pending order
- Validation cases: Invalid order ID, user ID
- Permission cases: User doesn't own order
- Status cases: Cannot cancel non-pending orders
- Not found cases: Order doesn't exist
- Stock restoration verification
- Repository exception cases
- Output structure validation
"""

import pytest
from unittest.mock import Mock, call
from datetime import datetime
from decimal import Decimal

from app.business.use_cases.cancel_order_use_case import (
    CancelOrderUseCase,
    CancelOrderInputData,
    CancelOrderOutputData
)
from app.domain.entities.order import Order, OrderItem
from app.domain.enums import OrderStatus, PaymentMethod
from app.domain.value_objects.money import Money
from app.domain.exceptions import (
    ValidationException,
    OrderNotFoundException,
    InvalidOrderStatusTransitionException,
    OrderAlreadyShippedException
)


class TestCancelOrderUseCase:
    """Test cases for CancelOrderUseCase"""
    
    # ============ FIXTURES ============
    
    @pytest.fixture
    def order_repository(self):
        """Mock order repository"""
        return Mock()
    
    @pytest.fixture
    def product_repository(self):
        """Mock product repository"""
        return Mock()
    
    @pytest.fixture
    def use_case(self, order_repository, product_repository):
        """Create use case instance"""
        return CancelOrderUseCase(order_repository, product_repository)
    
    # ============ HELPER METHODS ============
    
    def create_mock_order(self, order_id, user_id, status, item_count=2):
        """Create mock order with real Money"""
        order = Mock()
        order.id = order_id
        order.user_id = user_id  # Implementation uses user_id
        order.customer_id = user_id
        order.status = status
        order.payment_method = PaymentMethod.CASH
        order.shipping_address = "123 Test Street, District 1, HCMC"
        order.created_at = datetime(2025, 12, 1, 10, 30, 0)
        
        # Create order items
        items = []
        for i in range(item_count):
            item = Mock()
            item.product_id = i + 1
            item.product_name = f"Product {i + 1}"
            item.quantity = 2
            item.unit_price = Money(Decimal("1000000"), "VND")
            items.append(item)
        
        order.items = items
        
        # Mock cancel method
        def cancel_order():
            if status == OrderStatus.SHIPPING or status == OrderStatus.COMPLETED:
                raise OrderAlreadyShippedException(order_id)
            if not status.can_transition_to(OrderStatus.CANCELLED):
                raise InvalidOrderStatusTransitionException(str(status), str(OrderStatus.CANCELLED))
            order.status = OrderStatus.CANCELLED
        
        order.cancel = cancel_order
        
        return order
    
    def create_mock_product(self, product_id, stock_quantity):
        """Create mock product"""
        product = Mock()
        product.product_id = product_id
        product.stock_quantity = stock_quantity
        
        def add_stock(quantity):
            product.stock_quantity += quantity
        
        product.add_stock = add_stock
        
        return product
    
    # ============ SUCCESS CASES ============
    
    def test_cancel_pending_order_success(self, use_case, order_repository, product_repository):
        """Test successfully canceling a pending order"""
        # Arrange
        order_id = 10
        user_id = 5
        
        order = self.create_mock_order(order_id, user_id, OrderStatus.PENDING, item_count=2)
        product1 = self.create_mock_product(1, 50)
        product2 = self.create_mock_product(2, 30)
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        product_repository.find_by_id.side_effect = lambda pid: {1: product1, 2: product2}.get(pid)
        
        input_data = CancelOrderInputData(order_id=order_id, user_id=user_id)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.order_id == order_id
        assert "cancelled successfully" in output.message.lower()
        assert order.status == OrderStatus.CANCELLED
        
        # Verify stock restored
        assert product1.stock_quantity == 52  # 50 + 2
        assert product2.stock_quantity == 32  # 30 + 2
        
        # Verify repository calls
        order_repository.find_by_id.assert_called_once_with(order_id)
        order_repository.save.assert_called_once_with(order)
        assert product_repository.save.call_count == 2
    
    def test_cancel_order_with_single_item(self, use_case, order_repository, product_repository):
        """Test canceling order with single item"""
        # Arrange
        order_id = 10
        user_id = 5
        
        order = self.create_mock_order(order_id, user_id, OrderStatus.PENDING, item_count=1)
        product = self.create_mock_product(1, 100)
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        product_repository.find_by_id.side_effect = lambda pid: product if pid == 1 else None
        
        input_data = CancelOrderInputData(order_id=order_id, user_id=user_id)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert product.stock_quantity == 102  # 100 + 2
        product_repository.save.assert_called_once_with(product)
    
    def test_cancel_order_with_multiple_items(self, use_case, order_repository, product_repository):
        """Test canceling order with multiple items"""
        # Arrange
        order_id = 10
        user_id = 5
        
        order = self.create_mock_order(order_id, user_id, OrderStatus.PENDING, item_count=5)
        products = {i: self.create_mock_product(i, 100) for i in range(1, 6)}
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        product_repository.find_by_id.side_effect = lambda pid: products.get(pid)
        
        input_data = CancelOrderInputData(order_id=order_id, user_id=user_id)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert all(p.stock_quantity == 102 for p in products.values())
        assert product_repository.save.call_count == 5
    
    def test_cancel_order_product_not_found_skips_stock_restore(self, use_case, order_repository, product_repository):
        """Test canceling order when product no longer exists"""
        # Arrange
        order_id = 10
        user_id = 5
        
        order = self.create_mock_order(order_id, user_id, OrderStatus.PENDING, item_count=2)
        product1 = self.create_mock_product(1, 50)
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        product_repository.find_by_id.side_effect = lambda pid: product1 if pid == 1 else None
        
        input_data = CancelOrderInputData(order_id=order_id, user_id=user_id)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert product1.stock_quantity == 52  # Product 1 restored
        product_repository.save.assert_called_once_with(product1)  # Only called for product 1
    
    # ============ VALIDATION CASES ============
    
    def test_cancel_order_with_invalid_order_id_zero_fails(self, use_case, order_repository):
        """Test with invalid order ID (zero)"""
        # Arrange
        input_data = CancelOrderInputData(order_id=0, user_id=5)
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            use_case.execute(input_data)
        
        assert "invalid order id" in str(exc_info.value).lower()
        order_repository.find_by_id.assert_not_called()
    
    def test_cancel_order_with_negative_order_id_fails(self, use_case, order_repository):
        """Test with negative order ID"""
        # Arrange
        input_data = CancelOrderInputData(order_id=-1, user_id=5)
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            use_case.execute(input_data)
        
        assert "invalid order id" in str(exc_info.value).lower()
        order_repository.find_by_id.assert_not_called()
    
    def test_cancel_order_with_invalid_user_id_zero_fails(self, use_case, order_repository):
        """Test with invalid user ID (zero)"""
        # Arrange
        input_data = CancelOrderInputData(order_id=10, user_id=0)
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            use_case.execute(input_data)
        
        assert "invalid user id" in str(exc_info.value).lower()
        order_repository.find_by_id.assert_not_called()
    
    def test_cancel_order_with_negative_user_id_fails(self, use_case, order_repository):
        """Test with negative user ID"""
        # Arrange
        input_data = CancelOrderInputData(order_id=10, user_id=-1)
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            use_case.execute(input_data)
        
        assert "invalid user id" in str(exc_info.value).lower()
        order_repository.find_by_id.assert_not_called()
    
    # ============ PERMISSION CASES ============
    
    def test_cancel_order_not_owned_by_user_fails(self, use_case, order_repository, product_repository):
        """Test canceling order that doesn't belong to user"""
        # Arrange
        order_id = 10
        order_owner = 5
        requesting_user = 7
        
        order = self.create_mock_order(order_id, order_owner, OrderStatus.PENDING)
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        
        input_data = CancelOrderInputData(order_id=order_id, user_id=requesting_user)
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            use_case.execute(input_data)
        
        assert "permission" in str(exc_info.value).lower()
        order_repository.save.assert_not_called()
        product_repository.save.assert_not_called()
    
    # ============ STATUS CASES ============
    
    def test_cancel_shipping_order_fails(self, use_case, order_repository, product_repository):
        """Test cannot cancel order that is shipping"""
        # Arrange
        order_id = 10
        user_id = 5
        
        order = self.create_mock_order(order_id, user_id, OrderStatus.SHIPPING)
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        
        input_data = CancelOrderInputData(order_id=order_id, user_id=user_id)
        
        # Act & Assert
        with pytest.raises((ValidationException, OrderAlreadyShippedException)) as exc_info:
            use_case.execute(input_data)
        
        # Implementation may raise either exception type
        order_repository.save.assert_not_called()
        product_repository.save.assert_not_called()
    
    def test_cancel_completed_order_fails(self, use_case, order_repository, product_repository):
        """Test cannot cancel completed order"""
        # Arrange
        order_id = 10
        user_id = 5
        
        order = self.create_mock_order(order_id, user_id, OrderStatus.COMPLETED)
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        
        input_data = CancelOrderInputData(order_id=order_id, user_id=user_id)
        
        # Act & Assert
        with pytest.raises((ValidationException, OrderAlreadyShippedException)) as exc_info:
            use_case.execute(input_data)
        
        order_repository.save.assert_not_called()
        product_repository.save.assert_not_called()
    
    def test_cancel_already_cancelled_order_fails(self, use_case, order_repository, product_repository):
        """Test cannot cancel already cancelled order"""
        # Arrange
        order_id = 10
        user_id = 5
        
        order = self.create_mock_order(order_id, user_id, OrderStatus.CANCELLED)
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        
        input_data = CancelOrderInputData(order_id=order_id, user_id=user_id)
        
        # Act & Assert
        with pytest.raises((ValidationException, InvalidOrderStatusTransitionException)) as exc_info:
            use_case.execute(input_data)
        
        order_repository.save.assert_not_called()
        product_repository.save.assert_not_called()
    
    # ============ NOT FOUND CASES ============
    
    def test_cancel_nonexistent_order_fails(self, use_case, order_repository, product_repository):
        """Test canceling non-existent order"""
        # Arrange
        order_id = 999
        user_id = 5
        
        order_repository.find_by_id.side_effect = lambda oid: None
        
        input_data = CancelOrderInputData(order_id=order_id, user_id=user_id)
        
        # Act & Assert
        with pytest.raises(OrderNotFoundException) as exc_info:
            use_case.execute(input_data)
        
        order_repository.save.assert_not_called()
        product_repository.save.assert_not_called()
    
    # ============ REPOSITORY EXCEPTION CASES ============
    
    def test_repository_exception_find_order(self, use_case, order_repository):
        """Test repository exception during find_by_id"""
        # Arrange
        order_id = 10
        user_id = 5
        
        order_repository.find_by_id.side_effect = Exception("Database connection error")
        
        input_data = CancelOrderInputData(order_id=order_id, user_id=user_id)
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            use_case.execute(input_data)
        
        assert "database connection error" in str(exc_info.value).lower()
    
    def test_repository_exception_save_order(self, use_case, order_repository, product_repository):
        """Test repository exception during save order"""
        # Arrange
        order_id = 10
        user_id = 5
        
        order = self.create_mock_order(order_id, user_id, OrderStatus.PENDING, item_count=1)
        product = self.create_mock_product(1, 50)
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        product_repository.find_by_id.side_effect = lambda pid: product if pid == 1 else None
        order_repository.save.side_effect = Exception("Database save error")
        
        input_data = CancelOrderInputData(order_id=order_id, user_id=user_id)
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            use_case.execute(input_data)
        
        assert "database save error" in str(exc_info.value).lower()
    
    def test_repository_exception_find_product(self, use_case, order_repository, product_repository):
        """Test repository exception during find product"""
        # Arrange
        order_id = 10
        user_id = 5
        
        order = self.create_mock_order(order_id, user_id, OrderStatus.PENDING, item_count=1)
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        product_repository.find_by_id.side_effect = Exception("Product database error")
        
        input_data = CancelOrderInputData(order_id=order_id, user_id=user_id)
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            use_case.execute(input_data)
        
        assert "product database error" in str(exc_info.value).lower()
    
    def test_repository_exception_save_product(self, use_case, order_repository, product_repository):
        """Test repository exception during save product"""
        # Arrange
        order_id = 10
        user_id = 5
        
        order = self.create_mock_order(order_id, user_id, OrderStatus.PENDING, item_count=1)
        product = self.create_mock_product(1, 50)
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        product_repository.find_by_id.side_effect = lambda pid: product if pid == 1 else None
        product_repository.save.side_effect = Exception("Product save error")
        
        input_data = CancelOrderInputData(order_id=order_id, user_id=user_id)
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            use_case.execute(input_data)
        
        assert "product save error" in str(exc_info.value).lower()
    
    # ============ OUTPUT STRUCTURE VALIDATION ============
    
    def test_output_data_structure_complete(self, use_case, order_repository, product_repository):
        """Test output data has all required fields"""
        # Arrange
        order_id = 10
        user_id = 5
        
        order = self.create_mock_order(order_id, user_id, OrderStatus.PENDING, item_count=1)
        product = self.create_mock_product(1, 50)
        
        order_repository.find_by_id.side_effect = lambda oid: order if oid == order_id else None
        product_repository.find_by_id.side_effect = lambda pid: product if pid == 1 else None
        
        input_data = CancelOrderInputData(order_id=order_id, user_id=user_id)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert hasattr(output, 'success')
        assert hasattr(output, 'order_id')
        assert hasattr(output, 'message')
        
        assert isinstance(output.success, bool)
        assert isinstance(output.order_id, int)
        assert isinstance(output.message, str)
        assert len(output.message) > 0
