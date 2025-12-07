"""
Test suite for ListOrdersUseCase

Test Coverage:
- Success cases: List all orders, with pagination
- Filter cases: By status, customer, date range
- Sort cases: Different sort options
- Pagination cases: Multiple pages, edge cases
- Search cases: Search query
- Statistics validation
- Validation cases: Invalid page, per_page, dates, sort
- Repository exception cases
- Output structure validation
"""

import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta
from decimal import Decimal

from app.business.use_cases.list_orders_use_case import (
    ListOrdersUseCase,
    ListOrdersInputData,
    ListOrdersOutputData,
    OrderItemOutputData
)
from app.domain.entities.order import Order, OrderItem
from app.domain.enums import OrderStatus, PaymentMethod
from app.domain.value_objects.money import Money
from app.domain.exceptions import ValidationException


class TestListOrdersUseCase:
    """Test cases for ListOrdersUseCase"""
    
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
    def use_case(self, order_repository, user_repository):
        """Create use case instance"""
        return ListOrdersUseCase(order_repository, user_repository)
    
    # ============ HELPER METHODS ============
    
    def create_mock_order(self, order_id, customer_id, status, total_amount=5000000):
        """Create mock order"""
        order = Mock()
        order.order_id = order_id  # Implementation uses order_id
        order.id = order_id
        order.customer_id = customer_id
        order.status = status
        order.payment_method = PaymentMethod.CASH
        order.shipping_address = f"Address for order {order_id}"
        order.order_date = datetime(2025, 12, 1, 10, 30, 0)  # Implementation uses order_date
        order.created_at = datetime(2025, 12, 1, 10, 30, 0)
        order.total_amount = total_amount  # Implementation uses float
        
        # Create mock items
        items = [Mock() for _ in range(2)]
        order.items = items
        
        return order
    
    def create_mock_user(self, user_id, full_name, email):
        """Create mock user"""
        user = Mock()
        user.id = user_id
        user.full_name = full_name
        user.email = email
        return user
    
    # ============ SUCCESS CASES ============
    
    def test_list_all_orders_success(self, use_case, order_repository, user_repository):
        """Test listing all orders"""
        # Arrange
        order1 = self.create_mock_order(10, 1, OrderStatus.PENDING, 5000000)
        order2 = self.create_mock_order(11, 2, OrderStatus.SHIPPING, 8000000)
        user1 = self.create_mock_user(1, "User One", "user1@example.com")
        user2 = self.create_mock_user(2, "User Two", "user2@example.com")
        
        order_repository.find_with_filters.return_value = ([order1, order2], 2)
        order_repository.get_order_statistics.return_value = {
            'total_revenue': 13000000,
            'pending_count': 1,
            'shipping_count': 1,
            'completed_count': 0,
            'cancelled_count': 0
        }
        user_repository.find_by_id.side_effect = lambda uid: {1: user1, 2: user2}.get(uid)
        
        input_data = ListOrdersInputData(page=1, per_page=20)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.orders) == 2
        assert output.total_orders == 2
        assert output.page == 1
        assert output.per_page == 20
        assert output.total_pages == 1
        assert output.total_revenue == 13000000
        assert output.pending_count == 1
        assert output.shipping_count == 1
    
    def test_list_orders_empty_result(self, use_case, order_repository, user_repository):
        """Test listing when no orders exist"""
        # Arrange
        order_repository.find_with_filters.return_value = ([], 0)
        order_repository.get_order_statistics.return_value = {
            'total_revenue': 0,
            'pending_count': 0,
            'shipping_count': 0,
            'completed_count': 0,
            'cancelled_count': 0
        }
        
        input_data = ListOrdersInputData(page=1, per_page=20)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.orders) == 0
        assert output.total_orders == 0
        assert output.total_pages == 0
    
    def test_list_orders_with_customer_info(self, use_case, order_repository, user_repository):
        """Test orders include customer information"""
        # Arrange
        order = self.create_mock_order(10, 5, OrderStatus.PENDING, 7000000)
        user = self.create_mock_user(5, "John Doe", "john@example.com")
        
        order_repository.find_with_filters.return_value = ([order], 1)
        order_repository.get_order_statistics.return_value = {
            'total_revenue': 7000000,
            'pending_count': 1,
            'shipping_count': 0,
            'completed_count': 0,
            'cancelled_count': 0
        }
        user_repository.find_by_id.side_effect = lambda uid: user if uid == 5 else None
        
        input_data = ListOrdersInputData(page=1, per_page=20)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.orders[0].customer_name == "John Doe"
        assert output.orders[0].customer_email == "john@example.com"
        assert output.orders[0].customer_id == 5
    
    def test_list_orders_customer_not_found(self, use_case, order_repository, user_repository):
        """Test orders when customer not found"""
        # Arrange
        order = self.create_mock_order(10, 999, OrderStatus.PENDING)
        
        order_repository.find_with_filters.return_value = ([order], 1)
        order_repository.get_order_statistics.return_value = {
            'total_revenue': 5000000,
            'pending_count': 1,
            'shipping_count': 0,
            'completed_count': 0,
            'cancelled_count': 0
        }
        user_repository.find_by_id.side_effect = lambda uid: None
        
        input_data = ListOrdersInputData(page=1, per_page=20)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.orders[0].customer_name == "Unknown"
        assert output.orders[0].customer_email == ""
    
    # ============ PAGINATION CASES ============
    
    def test_list_orders_pagination_page_1(self, use_case, order_repository, user_repository):
        """Test first page pagination"""
        # Arrange
        orders = [self.create_mock_order(i, 1, OrderStatus.PENDING) for i in range(1, 11)]
        user = self.create_mock_user(1, "User One", "user@example.com")
        
        order_repository.find_with_filters.return_value = (orders, 25)
        order_repository.get_order_statistics.return_value = {'total_revenue': 0, 'pending_count': 25, 'shipping_count': 0, 'completed_count': 0, 'cancelled_count': 0}
        user_repository.find_by_id.side_effect = lambda uid: user
        
        input_data = ListOrdersInputData(page=1, per_page=10)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.page == 1
        assert output.per_page == 10
        assert output.total_orders == 25
        assert output.total_pages == 3
        assert len(output.orders) == 10
    
    def test_list_orders_pagination_page_2(self, use_case, order_repository, user_repository):
        """Test second page pagination"""
        # Arrange
        orders = [self.create_mock_order(i, 1, OrderStatus.PENDING) for i in range(11, 21)]
        user = self.create_mock_user(1, "User One", "user@example.com")
        
        order_repository.find_with_filters.return_value = (orders, 25)
        order_repository.get_order_statistics.return_value = {'total_revenue': 0, 'pending_count': 25, 'shipping_count': 0, 'completed_count': 0, 'cancelled_count': 0}
        user_repository.find_by_id.side_effect = lambda uid: user
        
        input_data = ListOrdersInputData(page=2, per_page=10)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.page == 2
        assert output.total_pages == 3
    
    def test_list_orders_pagination_last_page_partial(self, use_case, order_repository, user_repository):
        """Test last page with partial results"""
        # Arrange
        orders = [self.create_mock_order(i, 1, OrderStatus.PENDING) for i in range(21, 26)]
        user = self.create_mock_user(1, "User One", "user@example.com")
        
        order_repository.find_with_filters.return_value = (orders, 25)
        order_repository.get_order_statistics.return_value = {'total_revenue': 0, 'pending_count': 25, 'shipping_count': 0, 'completed_count': 0, 'cancelled_count': 0}
        user_repository.find_by_id.side_effect = lambda uid: user
        
        input_data = ListOrdersInputData(page=3, per_page=10)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.page == 3
        assert output.total_pages == 3
        assert len(output.orders) == 5
    
    def test_list_orders_custom_per_page(self, use_case, order_repository, user_repository):
        """Test custom per_page value"""
        # Arrange
        orders = [self.create_mock_order(i, 1, OrderStatus.PENDING) for i in range(1, 6)]
        user = self.create_mock_user(1, "User One", "user@example.com")
        
        order_repository.find_with_filters.return_value = (orders, 100)
        order_repository.get_order_statistics.return_value = {'total_revenue': 0, 'pending_count': 100, 'shipping_count': 0, 'completed_count': 0, 'cancelled_count': 0}
        user_repository.find_by_id.side_effect = lambda uid: user
        
        input_data = ListOrdersInputData(page=1, per_page=5)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.per_page == 5
        assert output.total_pages == 20
    
    # ============ FILTER CASES ============
    
    def test_list_orders_filter_by_status(self, use_case, order_repository, user_repository):
        """Test filtering by order status"""
        # Arrange
        order = self.create_mock_order(10, 1, OrderStatus.PENDING)
        user = self.create_mock_user(1, "User One", "user@example.com")
        
        order_repository.find_with_filters.return_value = ([order], 1)
        order_repository.get_order_statistics.return_value = {'total_revenue': 5000000, 'pending_count': 1, 'shipping_count': 0, 'completed_count': 0, 'cancelled_count': 0}
        user_repository.find_by_id.side_effect = lambda uid: user
        
        input_data = ListOrdersInputData(page=1, per_page=20, status="CHO_XAC_NHAN")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert all(order.status == "CHO_XAC_NHAN" for order in output.orders)
        
        # Verify filters passed to repository
        call_args = order_repository.find_with_filters.call_args
        assert call_args[1]['filters']['status'] == "CHO_XAC_NHAN"
    
    def test_list_orders_filter_by_customer(self, use_case, order_repository, user_repository):
        """Test filtering by customer ID"""
        # Arrange
        order = self.create_mock_order(10, 5, OrderStatus.PENDING)
        user = self.create_mock_user(5, "Customer Five", "customer5@example.com")
        
        order_repository.find_with_filters.return_value = ([order], 1)
        order_repository.get_order_statistics.return_value = {'total_revenue': 5000000, 'pending_count': 1, 'shipping_count': 0, 'completed_count': 0, 'cancelled_count': 0}
        user_repository.find_by_id.side_effect = lambda uid: user if uid == 5 else None
        
        input_data = ListOrdersInputData(page=1, per_page=20, customer_id=5)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert all(order.customer_id == 5 for order in output.orders)
        
        # Verify filters
        call_args = order_repository.find_with_filters.call_args
        assert call_args[1]['filters']['customer_id'] == 5
    
    def test_list_orders_filter_by_date_range(self, use_case, order_repository, user_repository):
        """Test filtering by date range"""
        # Arrange
        start_date = datetime(2025, 12, 1)
        end_date = datetime(2025, 12, 31)
        
        order = self.create_mock_order(10, 1, OrderStatus.PENDING)
        user = self.create_mock_user(1, "User One", "user@example.com")
        
        order_repository.find_with_filters.return_value = ([order], 1)
        order_repository.get_order_statistics.return_value = {'total_revenue': 5000000, 'pending_count': 1, 'shipping_count': 0, 'completed_count': 0, 'cancelled_count': 0}
        user_repository.find_by_id.side_effect = lambda uid: user
        
        input_data = ListOrdersInputData(page=1, per_page=20, start_date=start_date, end_date=end_date)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        
        # Verify filters
        call_args = order_repository.find_with_filters.call_args
        assert call_args[1]['filters']['start_date'] == start_date
        assert call_args[1]['filters']['end_date'] == end_date
    
    def test_list_orders_filter_by_search_query(self, use_case, order_repository, user_repository):
        """Test filtering by search query"""
        # Arrange
        order = self.create_mock_order(10, 1, OrderStatus.PENDING)
        user = self.create_mock_user(1, "John Doe", "john@example.com")
        
        order_repository.find_with_filters.return_value = ([order], 1)
        order_repository.get_order_statistics.return_value = {'total_revenue': 5000000, 'pending_count': 1, 'shipping_count': 0, 'completed_count': 0, 'cancelled_count': 0}
        user_repository.find_by_id.side_effect = lambda uid: user
        
        input_data = ListOrdersInputData(page=1, per_page=20, search_query="John")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        
        # Verify filters
        call_args = order_repository.find_with_filters.call_args
        assert call_args[1]['filters']['search_query'] == "John"
    
    def test_list_orders_multiple_filters(self, use_case, order_repository, user_repository):
        """Test combining multiple filters"""
        # Arrange
        order = self.create_mock_order(10, 5, OrderStatus.PENDING)
        user = self.create_mock_user(5, "User Five", "user5@example.com")
        
        order_repository.find_with_filters.return_value = ([order], 1)
        order_repository.get_order_statistics.return_value = {'total_revenue': 5000000, 'pending_count': 1, 'shipping_count': 0, 'completed_count': 0, 'cancelled_count': 0}
        user_repository.find_by_id.side_effect = lambda uid: user if uid == 5 else None
        
        input_data = ListOrdersInputData(
            page=1,
            per_page=20,
            status="CHO_XAC_NHAN",
            customer_id=5,
            search_query="test"
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        
        # Verify all filters
        call_args = order_repository.find_with_filters.call_args
        filters = call_args[1]['filters']
        assert filters['status'] == "CHO_XAC_NHAN"
        assert filters['customer_id'] == 5
        assert filters['search_query'] == "test"
    
    # ============ SORT CASES ============
    
    def test_list_orders_sort_newest(self, use_case, order_repository, user_repository):
        """Test sorting by newest first"""
        # Arrange
        order = self.create_mock_order(10, 1, OrderStatus.PENDING)
        user = self.create_mock_user(1, "User One", "user@example.com")
        
        order_repository.find_with_filters.return_value = ([order], 1)
        order_repository.get_order_statistics.return_value = {'total_revenue': 5000000, 'pending_count': 1, 'shipping_count': 0, 'completed_count': 0, 'cancelled_count': 0}
        user_repository.find_by_id.side_effect = lambda uid: user
        
        input_data = ListOrdersInputData(page=1, per_page=20, sort_by='newest')
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        call_args = order_repository.find_with_filters.call_args
        assert call_args[1]['sort_by'] == 'newest'
    
    def test_list_orders_sort_oldest(self, use_case, order_repository, user_repository):
        """Test sorting by oldest first"""
        # Arrange
        order = self.create_mock_order(10, 1, OrderStatus.PENDING)
        user = self.create_mock_user(1, "User One", "user@example.com")
        
        order_repository.find_with_filters.return_value = ([order], 1)
        order_repository.get_order_statistics.return_value = {'total_revenue': 5000000, 'pending_count': 1, 'shipping_count': 0, 'completed_count': 0, 'cancelled_count': 0}
        user_repository.find_by_id.side_effect = lambda uid: user
        
        input_data = ListOrdersInputData(page=1, per_page=20, sort_by='oldest')
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        call_args = order_repository.find_with_filters.call_args
        assert call_args[1]['sort_by'] == 'oldest'
    
    def test_list_orders_sort_total_asc(self, use_case, order_repository, user_repository):
        """Test sorting by total amount ascending"""
        # Arrange
        order = self.create_mock_order(10, 1, OrderStatus.PENDING)
        user = self.create_mock_user(1, "User One", "user@example.com")
        
        order_repository.find_with_filters.return_value = ([order], 1)
        order_repository.get_order_statistics.return_value = {'total_revenue': 5000000, 'pending_count': 1, 'shipping_count': 0, 'completed_count': 0, 'cancelled_count': 0}
        user_repository.find_by_id.side_effect = lambda uid: user
        
        input_data = ListOrdersInputData(page=1, per_page=20, sort_by='total_asc')
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        call_args = order_repository.find_with_filters.call_args
        assert call_args[1]['sort_by'] == 'total_asc'
    
    def test_list_orders_sort_total_desc(self, use_case, order_repository, user_repository):
        """Test sorting by total amount descending"""
        # Arrange
        order = self.create_mock_order(10, 1, OrderStatus.PENDING)
        user = self.create_mock_user(1, "User One", "user@example.com")
        
        order_repository.find_with_filters.return_value = ([order], 1)
        order_repository.get_order_statistics.return_value = {'total_revenue': 5000000, 'pending_count': 1, 'shipping_count': 0, 'completed_count': 0, 'cancelled_count': 0}
        user_repository.find_by_id.side_effect = lambda uid: user
        
        input_data = ListOrdersInputData(page=1, per_page=20, sort_by='total_desc')
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        call_args = order_repository.find_with_filters.call_args
        assert call_args[1]['sort_by'] == 'total_desc'
    
    # ============ STATISTICS VALIDATION ============
    
    def test_list_orders_statistics_complete(self, use_case, order_repository, user_repository):
        """Test statistics are correctly populated"""
        # Arrange
        order = self.create_mock_order(10, 1, OrderStatus.PENDING, 15000000)
        user = self.create_mock_user(1, "User One", "user@example.com")
        
        order_repository.find_with_filters.return_value = ([order], 1)
        order_repository.get_order_statistics.return_value = {
            'total_revenue': 50000000,
            'pending_count': 10,
            'shipping_count': 5,
            'completed_count': 20,
            'cancelled_count': 3
        }
        user_repository.find_by_id.side_effect = lambda uid: user
        
        input_data = ListOrdersInputData(page=1, per_page=20)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.total_revenue == 50000000
        assert output.pending_count == 10
        assert output.shipping_count == 5
        assert output.completed_count == 20
        assert output.cancelled_count == 3
    
    # ============ VALIDATION CASES ============
    
    def test_list_orders_invalid_page_zero_fails(self, use_case, order_repository):
        """Test with invalid page (zero)"""
        # Arrange
        input_data = ListOrdersInputData(page=0, per_page=20)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "page must be greater than 0" in output.message.lower()
        order_repository.find_with_filters.assert_not_called()
    
    def test_list_orders_invalid_page_negative_fails(self, use_case, order_repository):
        """Test with negative page"""
        # Arrange
        input_data = ListOrdersInputData(page=-1, per_page=20)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        order_repository.find_with_filters.assert_not_called()
    
    def test_list_orders_invalid_per_page_zero_fails(self, use_case, order_repository):
        """Test with invalid per_page (zero)"""
        # Arrange
        input_data = ListOrdersInputData(page=1, per_page=0)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "per page must be between 1 and 100" in output.message.lower()
        order_repository.find_with_filters.assert_not_called()
    
    def test_list_orders_invalid_per_page_exceeds_max_fails(self, use_case, order_repository):
        """Test with per_page exceeding maximum"""
        # Arrange
        input_data = ListOrdersInputData(page=1, per_page=101)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "per page must be between 1 and 100" in output.message.lower()
        order_repository.find_with_filters.assert_not_called()
    
    def test_list_orders_start_date_after_end_date_fails(self, use_case, order_repository):
        """Test with start_date after end_date"""
        # Arrange
        start_date = datetime(2025, 12, 31)
        end_date = datetime(2025, 12, 1)
        
        input_data = ListOrdersInputData(page=1, per_page=20, start_date=start_date, end_date=end_date)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "start date must be before end date" in output.message.lower()
        order_repository.find_with_filters.assert_not_called()
    
    def test_list_orders_invalid_sort_option_fails(self, use_case, order_repository):
        """Test with invalid sort option"""
        # Arrange
        input_data = ListOrdersInputData(page=1, per_page=20, sort_by='invalid_sort')
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "invalid sort option" in output.message.lower()
        order_repository.find_with_filters.assert_not_called()
    
    # ============ REPOSITORY EXCEPTION CASES ============
    
    def test_repository_exception_find_with_filters(self, use_case, order_repository):
        """Test repository exception during find_with_filters"""
        # Arrange
        order_repository.find_with_filters.side_effect = Exception("Database connection error")
        
        input_data = ListOrdersInputData(page=1, per_page=20)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "error" in output.message.lower()
    
    def test_repository_exception_get_statistics(self, use_case, order_repository, user_repository):
        """Test repository exception during get_order_statistics"""
        # Arrange
        order = self.create_mock_order(10, 1, OrderStatus.PENDING)
        user = self.create_mock_user(1, "User One", "user@example.com")
        
        order_repository.find_with_filters.return_value = ([order], 1)
        order_repository.get_order_statistics.side_effect = Exception("Statistics error")
        user_repository.find_by_id.side_effect = lambda uid: user
        
        input_data = ListOrdersInputData(page=1, per_page=20)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "error" in output.message.lower()
    
    # ============ OUTPUT STRUCTURE VALIDATION ============
    
    def test_output_data_structure_complete(self, use_case, order_repository, user_repository):
        """Test output data has all required fields"""
        # Arrange
        order = self.create_mock_order(10, 1, OrderStatus.PENDING, 7500000)
        user = self.create_mock_user(1, "User One", "user@example.com")
        
        order_repository.find_with_filters.return_value = ([order], 1)
        order_repository.get_order_statistics.return_value = {
            'total_revenue': 7500000,
            'pending_count': 1,
            'shipping_count': 0,
            'completed_count': 0,
            'cancelled_count': 0
        }
        user_repository.find_by_id.side_effect = lambda uid: user
        
        input_data = ListOrdersInputData(page=1, per_page=20)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert - Output structure
        assert hasattr(output, 'success')
        assert hasattr(output, 'orders')
        assert hasattr(output, 'total_orders')
        assert hasattr(output, 'page')
        assert hasattr(output, 'per_page')
        assert hasattr(output, 'total_pages')
        assert hasattr(output, 'total_revenue')
        assert hasattr(output, 'pending_count')
        assert hasattr(output, 'shipping_count')
        assert hasattr(output, 'completed_count')
        assert hasattr(output, 'cancelled_count')
        
        # Assert - Order item structure
        order_item = output.orders[0]
        assert hasattr(order_item, 'order_id')
        assert hasattr(order_item, 'customer_id')
        assert hasattr(order_item, 'customer_name')
        assert hasattr(order_item, 'customer_email')
        assert hasattr(order_item, 'total_amount')
        assert hasattr(order_item, 'status')
        assert hasattr(order_item, 'payment_method')
        assert hasattr(order_item, 'shipping_address')
        assert hasattr(order_item, 'order_date')
        assert hasattr(order_item, 'item_count')
    
    def test_output_data_structure_on_failure(self, use_case, order_repository):
        """Test output structure on failure"""
        # Arrange
        input_data = ListOrdersInputData(page=0, per_page=20)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert hasattr(output, 'message')
        assert isinstance(output.message, str)
        assert len(output.message) > 0
        assert output.orders == []
        assert output.total_orders == 0
