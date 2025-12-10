"""
Integration tests for OrderRepositoryAdapter
Tests the adapter layer with real database operations
"""
import pytest
from datetime import datetime
from app.domain.entities.order import Order, OrderItem
from app.domain.value_objects.money import Money
from app.domain.enums import OrderStatus, PaymentMethod


class TestOrderRepositoryIntegration:
    """Test OrderRepositoryAdapter with real database"""
    
    def test_save_creates_order_in_database(self, order_repository, sample_user, sample_product):
        """Test that save() creates an order in the database"""
        # Arrange
        items = [
            OrderItem(
                product_id=sample_product.id,
                product_name=sample_product.name,
                quantity=2,
                unit_price=sample_product.price
            )
        ]
        order = Order(
            customer_id=sample_user.id,
            items=items,
            payment_method=PaymentMethod.CREDIT_CARD,
            shipping_address="123 Test Street",
            phone_number="0123456789",
            notes="Test order"
        )
        
        # Act
        saved_order = order_repository.save(order)
        
        # Assert
        assert saved_order.id is not None
        assert saved_order.customer_id == sample_user.id
        assert len(saved_order.items) == 1
        assert saved_order.status == OrderStatus.PENDING
        
    def test_find_by_id_retrieves_correct_order(self, order_repository, sample_order):
        """Test that find_by_id() retrieves the correct order"""
        # Act
        found_order = order_repository.find_by_id(sample_order.id)
        
        # Assert
        assert found_order is not None
        assert found_order.id == sample_order.id
        assert found_order.customer_id == sample_order.customer_id
        assert len(found_order.items) == len(sample_order.items)
        
    def test_find_by_id_returns_none_when_not_found(self, order_repository):
        """Test that find_by_id() returns None when order not found"""
        # Act
        result = order_repository.find_by_id(99999)
        
        # Assert
        assert result is None
        
    def test_find_by_customer_id_retrieves_orders(self, order_repository, sample_order):
        """Test that find_by_customer_id() retrieves customer's orders"""
        # Act
        orders = order_repository.find_by_customer_id(sample_order.customer_id)
        
        # Assert
        assert len(orders) > 0
        assert any(o.id == sample_order.id for o in orders)
        assert all(o.customer_id == sample_order.customer_id for o in orders)
        
    def test_find_by_customer_id_with_pagination(self, order_repository, sample_user, sample_product):
        """Test pagination in find_by_customer_id()"""
        # Arrange - Create multiple orders
        for i in range(5):
            items = [
                OrderItem(
                    product_id=sample_product.id,
                    product_name=f"Product {i}",
                    quantity=1,
                    unit_price=Money(100.00)
                )
            ]
            order = Order(
                customer_id=sample_user.id,
                items=items,
                payment_method=PaymentMethod.CREDIT_CARD,
                shipping_address="Test Address",
                phone_number="0123456789",
                notes="Test order"
            )
            order_repository.save(order)
        
        # Act
        page1 = order_repository.find_by_customer_id(sample_user.id, skip=0, limit=2)
        page2 = order_repository.find_by_customer_id(sample_user.id, skip=2, limit=2)
        
        # Assert
        assert len(page1) == 2
        assert len(page2) == 2
        assert page1[0].id != page2[0].id
        
    def test_find_by_status_retrieves_matching_orders(self, order_repository, sample_order):
        """Test that find_by_status() retrieves orders with matching status"""
        # Act
        pending_orders = order_repository.find_by_status(OrderStatus.PENDING)
        
        # Assert
        assert len(pending_orders) > 0
        assert all(o.status == OrderStatus.PENDING for o in pending_orders)
        assert any(o.id == sample_order.id for o in pending_orders)
        
    def test_update_order_status(self, order_repository, sample_order):
        """Test updating order status"""
        # Arrange - Transition from PENDING to SHIPPING
        sample_order.ship()
        
        # Act
        updated_order = order_repository.save(sample_order)
        
        # Assert
        assert updated_order.status == OrderStatus.SHIPPING
        
        # Verify persistence
        found_order = order_repository.find_by_id(sample_order.id)
        assert found_order.status == OrderStatus.SHIPPING
        
    def test_order_status_transitions(self, order_repository, sample_order):
        """Test complete order status workflow"""
        # PENDING -> SHIPPING
        sample_order.ship()
        order_repository.save(sample_order)
        assert sample_order.status == OrderStatus.SHIPPING
        
        # SHIPPING -> COMPLETED
        sample_order.complete()
        updated_order = order_repository.save(sample_order)
        assert updated_order.status == OrderStatus.COMPLETED
        
        # Verify final state
        found_order = order_repository.find_by_id(sample_order.id)
        assert found_order.status == OrderStatus.COMPLETED
        
    def test_cancel_pending_order(self, order_repository, sample_order):
        """Test cancelling a pending order"""
        # Arrange - Order should be PENDING
        assert sample_order.status == OrderStatus.PENDING
        
        # Act
        sample_order.cancel()
        updated_order = order_repository.save(sample_order)
        
        # Assert
        assert updated_order.status == OrderStatus.CANCELLED
        
        # Verify persistence
        found_order = order_repository.find_by_id(sample_order.id)
        assert found_order.status == OrderStatus.CANCELLED
        
    def test_order_items_persist_correctly(self, order_repository, sample_user, sample_product):
        """Test that order items are saved and loaded correctly"""
        # Arrange
        items = [
            OrderItem(
                product_id=sample_product.id,
                product_name="Product A",
                quantity=2,
                unit_price=Money(100.00)
            ),
            OrderItem(
                product_id=sample_product.id,
                product_name="Product B",
                quantity=3,
                unit_price=Money(150.00)
            ),
            OrderItem(
                product_id=sample_product.id,
                product_name="Product C",
                quantity=1,
                unit_price=Money(200.00)
            )
        ]
        order = Order(
            customer_id=sample_user.id,
            items=items,
            payment_method=PaymentMethod.BANK_TRANSFER,
            shipping_address="123 Main St",
            phone_number="0123456789",
            notes="Test order"
        )
        
        # Act
        saved_order = order_repository.save(order)
        found_order = order_repository.find_by_id(saved_order.id)
        
        # Assert
        assert len(found_order.items) == 3
        
        # Verify each item
        assert found_order.items[0].product_name == "Product A"
        assert found_order.items[0].quantity == 2
        assert found_order.items[0].unit_price.amount == 100.00
        
        assert found_order.items[1].product_name == "Product B"
        assert found_order.items[1].quantity == 3
        assert found_order.items[1].unit_price.amount == 150.00
        
        assert found_order.items[2].product_name == "Product C"
        assert found_order.items[2].quantity == 1
        assert found_order.items[2].unit_price.amount == 200.00
        
    def test_order_total_calculated_correctly(self, order_repository, sample_user, sample_product):
        """Test that order total is calculated from items"""
        # Arrange
        items = [
            OrderItem(
                product_id=sample_product.id,
                product_name="Product",
                quantity=2,
                unit_price=Money(50.00)
            ),
            OrderItem(
                product_id=sample_product.id,
                product_name="Product",
                quantity=3,
                unit_price=Money(30.00)
            )
        ]
        order = Order(
            customer_id=sample_user.id,
            items=items,
            payment_method=PaymentMethod.CASH,
            shipping_address="Test Address",
            phone_number="0123456789",
            notes="Test order"
        )
        
        # Act
        saved_order = order_repository.save(order)
        
        # Assert
        # Total = (2 * 50) + (3 * 30) = 100 + 90 = 190
        assert saved_order.total_amount.amount == 190
        
    def test_payment_method_persists(self, order_repository, sample_user, sample_product):
        """Test that payment method is saved and loaded correctly"""
        # Test each payment method
        payment_methods = [
            PaymentMethod.CREDIT_CARD,
            PaymentMethod.BANK_TRANSFER,
            PaymentMethod.CASH
        ]
        
        for payment_method in payment_methods:
            # Arrange
            items = [
                OrderItem(
                    product_id=sample_product.id,
                    product_name="Product",
                    quantity=1,
                    unit_price=Money(100.00)
                )
            ]
            order = Order(
                customer_id=sample_user.id,
                items=items,
                payment_method=payment_method,
                shipping_address="Test Address",
                phone_number="0123456789",
                notes="Test order"
            )
            
            # Act
            saved_order = order_repository.save(order)
            found_order = order_repository.find_by_id(saved_order.id)
            
            # Assert
            assert found_order.payment_method == payment_method
            
    def test_count_by_status(self, order_repository, sample_user, sample_product):
        """Test counting orders by status"""
        # Arrange - Create orders with different statuses
        for i in range(3):
            items = [
                OrderItem(
                    product_id=sample_product.id,
                    product_name="Product",
                    quantity=1,
                    unit_price=Money(100.00)
                )
            ]
            order = Order(
                customer_id=sample_user.id,
                items=items,
                payment_method=PaymentMethod.CREDIT_CARD,
                shipping_address="Test Address",
                phone_number="0123456789",
                notes="Test order"
            )
            saved_order = order_repository.save(order)
            
            if i == 1:
                saved_order.ship()
                order_repository.save(saved_order)
            elif i == 2:
                saved_order.ship()
                saved_order.complete()
                order_repository.save(saved_order)
        
        # Act
        pending_orders = order_repository.find_by_status(OrderStatus.PENDING)
        shipping_orders = order_repository.find_by_status(OrderStatus.SHIPPING)
        completed_orders = order_repository.find_by_status(OrderStatus.COMPLETED)
        
        # Assert
        assert len([o for o in pending_orders if o.customer_id == sample_user.id]) >= 1
        assert len([o for o in shipping_orders if o.customer_id == sample_user.id]) >= 1
        assert len([o for o in completed_orders if o.customer_id == sample_user.id]) >= 1
        
    def test_order_timestamps_persist(self, order_repository, sample_order):
        """Test that order timestamps are saved correctly"""
        # Act
        found_order = order_repository.find_by_id(sample_order.id)
        
        # Assert
        assert found_order.created_at is not None
        assert isinstance(found_order.created_at, datetime)
        assert found_order.created_at <= datetime.now()

