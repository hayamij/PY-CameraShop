"""
Tests for DeleteOrderUseCase
"""
import pytest
from datetime import datetime
from decimal import Decimal
from app.business.use_cases.delete_order_use_case import (
    DeleteOrderUseCase,
    DeleteOrderInputData
)
from app.domain.entities.order import Order, OrderItem
from app.domain.value_objects import Money
from app.domain.enums import OrderStatus, PaymentMethod


class MockOrderRepository:
    """Mock order repository for testing"""
    def __init__(self):
        self.orders = {}
        self.deleted_ids = []
    
    def find_by_id(self, order_id):
        if order_id in self.deleted_ids:
            return None
        return self.orders.get(order_id)
    
    def delete(self, order_id):
        if order_id in self.orders:
            self.deleted_ids.append(order_id)
            del self.orders[order_id]
        else:
            raise ValueError(f"Order {order_id} not found")
    
    def add_order(self, order):
        self.orders[order.id] = order


class TestDeleteOrderUseCase:
    """Test DeleteOrderUseCase"""
    
    @pytest.fixture
    def order_repository(self):
        """Setup mock order repository with test data"""
        repo = MockOrderRepository()
        
        # Add test orders
        unit_price = Money(Decimal("1000000"))
        items = [OrderItem(1, "Canon EOS 90D", 2, unit_price)]
        
        order1 = Order.reconstruct(
            order_id=1,
            customer_id=1,
            items=items,
            payment_method=PaymentMethod.COD,
            shipping_address="123 Test Street",
            phone_number="0123456789",
            notes="Test order",
            status=OrderStatus.PENDING,
            total_amount=Money(Decimal("2000000")),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        order2 = Order.reconstruct(
            order_id=2,
            customer_id=2,
            items=items,
            payment_method=PaymentMethod.BANK_TRANSFER,
            shipping_address="456 Test Avenue",
            phone_number="0987654321",
            notes="Another order",
            status=OrderStatus.COMPLETED,
            total_amount=Money(Decimal("2000000")),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        repo.add_order(order1)
        repo.add_order(order2)
        
        return repo
    
    @pytest.fixture
    def use_case(self, order_repository):
        """Create use case with mock repository"""
        return DeleteOrderUseCase(order_repository)
    
    def test_delete_order_success(self, use_case, order_repository):
        """Should successfully delete order"""
        input_data = DeleteOrderInputData(order_id=1)
        
        result = use_case.execute(input_data)
        
        assert result.success is True
        assert "deleted successfully" in result.message
        assert order_repository.find_by_id(1) is None
    
    def test_delete_order_not_found(self, use_case):
        """Should fail when order not found"""
        input_data = DeleteOrderInputData(order_id=999)
        
        result = use_case.execute(input_data)
        
        assert result.success is False
        assert "not found" in result.message.lower()
    
    def test_delete_order_pending_status(self, use_case, order_repository):
        """Should delete order with PENDING status"""
        input_data = DeleteOrderInputData(order_id=1)
        
        # Verify order exists before deletion
        assert order_repository.find_by_id(1) is not None
        
        result = use_case.execute(input_data)
        
        assert result.success is True
        assert order_repository.find_by_id(1) is None
    
    def test_delete_order_completed_status(self, use_case, order_repository):
        """Should delete order with COMPLETED status"""
        input_data = DeleteOrderInputData(order_id=2)
        
        # Verify order exists before deletion
        assert order_repository.find_by_id(2) is not None
        
        result = use_case.execute(input_data)
        
        assert result.success is True
        assert order_repository.find_by_id(2) is None
    
    def test_delete_order_multiple_deletions(self, use_case, order_repository):
        """Should handle multiple order deletions"""
        # Delete first order
        result1 = use_case.execute(DeleteOrderInputData(order_id=1))
        assert result1.success is True
        
        # Delete second order
        result2 = use_case.execute(DeleteOrderInputData(order_id=2))
        assert result2.success is True
        
        # Verify both deleted
        assert order_repository.find_by_id(1) is None
        assert order_repository.find_by_id(2) is None
    
    def test_delete_order_already_deleted(self, use_case):
        """Should fail when trying to delete already deleted order"""
        # Delete once
        result1 = use_case.execute(DeleteOrderInputData(order_id=1))
        assert result1.success is True
        
        # Try to delete again
        result2 = use_case.execute(DeleteOrderInputData(order_id=1))
        assert result2.success is False
        assert "not found" in result2.message.lower()


class TestDeleteOrderUseCaseEdgeCases:
    """Test edge cases for DeleteOrderUseCase"""
    
    def test_delete_order_repository_exception(self):
        """Should handle repository exceptions gracefully"""
        class FailingRepository:
            def find_by_id(self, order_id):
                return Order.reconstruct(
                    order_id=1,
                    customer_id=1,
                    items=[],
                    payment_method=PaymentMethod.COD,
                    shipping_address="Test",
                    phone_number="0123456789",
                    notes="",
                    status=OrderStatus.PENDING,
                    total_amount=Money(Decimal("0")),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
            
            def delete(self, order_id):
                raise Exception("Database connection error")
        
        use_case = DeleteOrderUseCase(FailingRepository())
        input_data = DeleteOrderInputData(order_id=1)
        
        result = use_case.execute(input_data)
        
        assert result.success is False
        assert "failed" in result.message.lower()
