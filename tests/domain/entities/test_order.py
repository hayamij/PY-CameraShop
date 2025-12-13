"""
Tests for Order domain entity
"""
import pytest
from datetime import datetime
from decimal import Decimal
from app.domain.entities.order import Order, OrderItem
from app.domain.value_objects import Money
from app.domain.enums import OrderStatus, PaymentMethod
from app.domain.exceptions import (
    EmptyOrderException,
    InvalidOrderStatusTransitionException,
    OrderAlreadyShippedException
)


class TestOrderItemCreation:
    """Test OrderItem value object creation"""
    
    def test_create_valid_order_item(self):
        """Should create order item with valid data"""
        unit_price = Money(Decimal("1000000"))
        
        item = OrderItem(
            product_id=1,
            product_name="Canon EOS 90D",
            quantity=2,
            unit_price=unit_price
        )
        
        assert item.product_id == 1
        assert item.product_name == "Canon EOS 90D"
        assert item.quantity == 2
        assert item.unit_price == unit_price
    
    def test_order_item_calculate_subtotal(self):
        """Should calculate subtotal correctly"""
        unit_price = Money(Decimal("1000000"))
        
        item = OrderItem(
            product_id=1,
            product_name="Canon EOS 90D",
            quantity=3,
            unit_price=unit_price
        )
        
        subtotal = item.calculate_subtotal()
        assert subtotal.amount == Decimal("3000000")
    
    def test_create_order_item_invalid_product_id(self):
        """Should raise error for invalid product ID"""
        unit_price = Money(Decimal("1000000"))
        
        with pytest.raises(ValueError, match="Invalid product ID"):
            OrderItem(
                product_id=0,
                product_name="Canon EOS 90D",
                quantity=2,
                unit_price=unit_price
            )
    
    def test_create_order_item_empty_product_name(self):
        """Should raise error for empty product name"""
        unit_price = Money(Decimal("1000000"))
        
        with pytest.raises(ValueError, match="Product name cannot be empty"):
            OrderItem(
                product_id=1,
                product_name="",
                quantity=2,
                unit_price=unit_price
            )
    
    def test_create_order_item_invalid_quantity_zero(self):
        """Should raise error for zero quantity"""
        unit_price = Money(Decimal("1000000"))
        
        with pytest.raises(ValueError, match="Quantity must be positive"):
            OrderItem(
                product_id=1,
                product_name="Canon EOS 90D",
                quantity=0,
                unit_price=unit_price
            )
    
    def test_create_order_item_invalid_quantity_negative(self):
        """Should raise error for negative quantity"""
        unit_price = Money(Decimal("1000000"))
        
        with pytest.raises(ValueError, match="Quantity must be positive"):
            OrderItem(
                product_id=1,
                product_name="Canon EOS 90D",
                quantity=-1,
                unit_price=unit_price
            )
    
    def test_create_order_item_invalid_unit_price_zero(self):
        """Should raise error for zero unit price"""
        unit_price = Money(Decimal("0"))
        
        with pytest.raises(ValueError, match="Unit price must be positive"):
            OrderItem(
                product_id=1,
                product_name="Canon EOS 90D",
                quantity=2,
                unit_price=unit_price
            )


class TestOrderCreation:
    """Test Order entity creation"""
    
    def test_create_valid_order(self):
        """Should create order with valid data"""
        unit_price = Money(Decimal("1000000"))
        items = [
            OrderItem(1, "Canon EOS 90D", 2, unit_price),
            OrderItem(2, "Nikon D850", 1, Money(Decimal("1500000")))
        ]
        
        order = Order(
            customer_id=1,
            items=items,
            payment_method=PaymentMethod.COD,
            shipping_address="123 Test Street, City",
            phone_number="0123456789",
            notes="Please deliver in the morning"
        )
        
        assert order.customer_id == 1
        assert len(order.items) == 2
        assert order.payment_method == PaymentMethod.COD
        assert order.shipping_address == "123 Test Street, City"
        assert order.phone_number == "0123456789"
        assert order.notes == "Please deliver in the morning"
        assert order.status == OrderStatus.PENDING
        assert order.total_amount.amount == Decimal("3500000")
        assert order.id is None
    
    def test_create_order_without_notes(self):
        """Should create order without notes"""
        unit_price = Money(Decimal("1000000"))
        items = [OrderItem(1, "Canon EOS 90D", 2, unit_price)]
        
        order = Order(
            customer_id=1,
            items=items,
            payment_method=PaymentMethod.COD,
            shipping_address="123 Test Street, City",
            phone_number="0123456789"
        )
        
        assert order.notes == ""
    
    def test_create_order_strips_whitespace(self):
        """Should strip whitespace from string fields"""
        unit_price = Money(Decimal("1000000"))
        items = [OrderItem(1, "Canon EOS 90D", 2, unit_price)]
        
        order = Order(
            customer_id=1,
            items=items,
            payment_method=PaymentMethod.COD,
            shipping_address="  123 Test Street, City  ",
            phone_number="  0123456789  ",
            notes="  Please deliver in the morning  "
        )
        
        assert order.shipping_address == "123 Test Street, City"
        assert order.phone_number == "0123456789"
        assert order.notes == "Please deliver in the morning"
    
    def test_create_order_empty_items(self):
        """Should raise error for empty items list"""
        with pytest.raises(EmptyOrderException):
            Order(
                customer_id=1,
                items=[],
                payment_method=PaymentMethod.COD,
                shipping_address="123 Test Street, City",
                phone_number="0123456789"
            )
    
    def test_create_order_none_items(self):
        """Should raise error for None items"""
        with pytest.raises(EmptyOrderException):
            Order(
                customer_id=1,
                items=None,
                payment_method=PaymentMethod.COD,
                shipping_address="123 Test Street, City",
                phone_number="0123456789"
            )
    
    def test_create_order_invalid_customer_id(self):
        """Should raise error for invalid customer ID"""
        unit_price = Money(Decimal("1000000"))
        items = [OrderItem(1, "Canon EOS 90D", 2, unit_price)]
        
        with pytest.raises(ValueError, match="Invalid customer ID"):
            Order(
                customer_id=0,
                items=items,
                payment_method=PaymentMethod.COD,
                shipping_address="123 Test Street, City",
                phone_number="0123456789"
            )
    
    def test_create_order_invalid_shipping_address_too_short(self):
        """Should raise error for short shipping address"""
        unit_price = Money(Decimal("1000000"))
        items = [OrderItem(1, "Canon EOS 90D", 2, unit_price)]
        
        with pytest.raises(ValueError, match="Shipping address must be at least 10 characters"):
            Order(
                customer_id=1,
                items=items,
                payment_method=PaymentMethod.COD,
                shipping_address="Short",
                phone_number="0123456789"
            )
    
    def test_create_order_invalid_phone_number_too_short(self):
        """Should raise error for short phone number"""
        unit_price = Money(Decimal("1000000"))
        items = [OrderItem(1, "Canon EOS 90D", 2, unit_price)]
        
        with pytest.raises(ValueError, match="Phone number must be at least 10 characters"):
            Order(
                customer_id=1,
                items=items,
                payment_method=PaymentMethod.COD,
                shipping_address="123 Test Street, City",
                phone_number="123"
            )


class TestOrderReconstruction:
    """Test Order reconstruction from database"""
    
    def test_reconstruct_order(self):
        """Should reconstruct order from database without validation"""
        unit_price = Money(Decimal("1000000"))
        items = [OrderItem(1, "Canon EOS 90D", 2, unit_price)]
        total_amount = Money(Decimal("2000000"))
        created_at = datetime(2023, 1, 1, 12, 0, 0)
        updated_at = datetime(2023, 1, 2, 12, 0, 0)
        
        order = Order.reconstruct(
            order_id=1,
            customer_id=1,
            items=items,
            payment_method=PaymentMethod.COD,
            shipping_address="123 Test Street, City",
            phone_number="0123456789",
            notes="Test notes",
            status=OrderStatus.COMPLETED,
            total_amount=total_amount,
            created_at=created_at,
            updated_at=updated_at
        )
        
        assert order.id == 1
        assert order.status == OrderStatus.COMPLETED
        assert order.created_at == created_at
        assert order.updated_at == updated_at


class TestOrderBehavior:
    """Test Order entity behavior"""
    
    def test_ship_order_from_pending(self):
        """Should ship order from PENDING status"""
        unit_price = Money(Decimal("1000000"))
        items = [OrderItem(1, "Canon EOS 90D", 2, unit_price)]
        
        order = Order(
            customer_id=1,
            items=items,
            payment_method=PaymentMethod.COD,
            shipping_address="123 Test Street, City",
            phone_number="0123456789"
        )
        
        assert order.status == OrderStatus.PENDING
        order.ship()
        assert order.status == OrderStatus.SHIPPING
    
    def test_ship_order_invalid_transition(self):
        """Should raise error for invalid status transition"""
        unit_price = Money(Decimal("1000000"))
        items = [OrderItem(1, "Canon EOS 90D", 2, unit_price)]
        total_amount = Money(Decimal("2000000"))
        
        order = Order.reconstruct(
            order_id=1,
            customer_id=1,
            items=items,
            payment_method=PaymentMethod.COD,
            shipping_address="123 Test Street, City",
            phone_number="0123456789",
            notes="",
            status=OrderStatus.COMPLETED,
            total_amount=total_amount,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        with pytest.raises(InvalidOrderStatusTransitionException):
            order.ship()
    
    def test_complete_order_from_shipping(self):
        """Should complete order from SHIPPING status"""
        unit_price = Money(Decimal("1000000"))
        items = [OrderItem(1, "Canon EOS 90D", 2, unit_price)]
        total_amount = Money(Decimal("2000000"))
        
        order = Order.reconstruct(
            order_id=1,
            customer_id=1,
            items=items,
            payment_method=PaymentMethod.COD,
            shipping_address="123 Test Street, City",
            phone_number="0123456789",
            notes="",
            status=OrderStatus.SHIPPING,
            total_amount=total_amount,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        order.complete()
        assert order.status == OrderStatus.COMPLETED
    
    def test_cancel_order_from_pending(self):
        """Should cancel order from PENDING status"""
        unit_price = Money(Decimal("1000000"))
        items = [OrderItem(1, "Canon EOS 90D", 2, unit_price)]
        
        order = Order(
            customer_id=1,
            items=items,
            payment_method=PaymentMethod.COD,
            shipping_address="123 Test Street, City",
            phone_number="0123456789"
        )
        
        order.cancel()
        assert order.status == OrderStatus.CANCELLED
    
    def test_cancel_order_invalid_transition(self):
        """Should raise error when cancelling shipped order"""
        unit_price = Money(Decimal("1000000"))
        items = [OrderItem(1, "Canon EOS 90D", 2, unit_price)]
        total_amount = Money(Decimal("2000000"))
        
        order = Order.reconstruct(
            order_id=1,
            customer_id=1,
            items=items,
            payment_method=PaymentMethod.COD,
            shipping_address="123 Test Street, City",
            phone_number="0123456789",
            notes="",
            status=OrderStatus.SHIPPING,
            total_amount=total_amount,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        with pytest.raises(OrderAlreadyShippedException):
            order.cancel()
    
    def test_is_pending(self):
        """Should check if order is pending"""
        unit_price = Money(Decimal("1000000"))
        items = [OrderItem(1, "Canon EOS 90D", 2, unit_price)]
        
        pending_order = Order(
            customer_id=1,
            items=items,
            payment_method=PaymentMethod.COD,
            shipping_address="123 Test Street, City",
            phone_number="0123456789"
        )
        
        completed_order = Order.reconstruct(
            order_id=1,
            customer_id=1,
            items=items,
            payment_method=PaymentMethod.COD,
            shipping_address="123 Test Street, City",
            phone_number="0123456789",
            notes="",
            status=OrderStatus.COMPLETED,
            total_amount=Money(Decimal("2000000")),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert pending_order.is_pending() is True
        assert completed_order.is_pending() is False
    
    def test_is_completed(self):
        """Should check if order is completed"""
        unit_price = Money(Decimal("1000000"))
        items = [OrderItem(1, "Canon EOS 90D", 2, unit_price)]
        
        pending_order = Order(
            customer_id=1,
            items=items,
            payment_method=PaymentMethod.COD,
            shipping_address="123 Test Street, City",
            phone_number="0123456789"
        )
        
        completed_order = Order.reconstruct(
            order_id=1,
            customer_id=1,
            items=items,
            payment_method=PaymentMethod.COD,
            shipping_address="123 Test Street, City",
            phone_number="0123456789",
            notes="",
            status=OrderStatus.COMPLETED,
            total_amount=Money(Decimal("2000000")),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert pending_order.is_completed() is False
        assert completed_order.is_completed() is True
    
    def test_is_cancelled(self):
        """Should check if order is cancelled"""
        unit_price = Money(Decimal("1000000"))
        items = [OrderItem(1, "Canon EOS 90D", 2, unit_price)]
        
        cancelled_order = Order.reconstruct(
            order_id=1,
            customer_id=1,
            items=items,
            payment_method=PaymentMethod.COD,
            shipping_address="123 Test Street, City",
            phone_number="0123456789",
            notes="",
            status=OrderStatus.CANCELLED,
            total_amount=Money(Decimal("2000000")),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert cancelled_order.is_cancelled() is True
    
    def test_can_be_cancelled(self):
        """Should check if order can be cancelled"""
        unit_price = Money(Decimal("1000000"))
        items = [OrderItem(1, "Canon EOS 90D", 2, unit_price)]
        
        pending_order = Order(
            customer_id=1,
            items=items,
            payment_method=PaymentMethod.COD,
            shipping_address="123 Test Street, City",
            phone_number="0123456789"
        )
        
        shipping_order = Order.reconstruct(
            order_id=1,
            customer_id=1,
            items=items,
            payment_method=PaymentMethod.COD,
            shipping_address="123 Test Street, City",
            phone_number="0123456789",
            notes="",
            status=OrderStatus.SHIPPING,
            total_amount=Money(Decimal("2000000")),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert pending_order.can_be_cancelled() is True
        assert shipping_order.can_be_cancelled() is False


class TestOrderEquality:
    """Test Order equality comparison"""
    
    def test_orders_with_same_id_are_equal(self):
        """Should consider orders with same ID as equal"""
        unit_price = Money(Decimal("1000000"))
        items1 = [OrderItem(1, "Canon EOS 90D", 2, unit_price)]
        items2 = [OrderItem(2, "Nikon D850", 1, unit_price)]
        total_amount = Money(Decimal("2000000"))
        
        order1 = Order.reconstruct(
            order_id=1,
            customer_id=1,
            items=items1,
            payment_method=PaymentMethod.COD,
            shipping_address="Address 1",
            phone_number="0123456789",
            notes="",
            status=OrderStatus.PENDING,
            total_amount=total_amount,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        order2 = Order.reconstruct(
            order_id=1,
            customer_id=2,
            items=items2,
            payment_method=PaymentMethod.BANK_TRANSFER,
            shipping_address="Address 2",
            phone_number="0987654321",
            notes="",
            status=OrderStatus.COMPLETED,
            total_amount=total_amount,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert order1 == order2
    
    def test_orders_with_different_id_are_not_equal(self):
        """Should consider orders with different IDs as not equal"""
        unit_price = Money(Decimal("1000000"))
        items = [OrderItem(1, "Canon EOS 90D", 2, unit_price)]
        total_amount = Money(Decimal("2000000"))
        
        order1 = Order.reconstruct(
            order_id=1,
            customer_id=1,
            items=items,
            payment_method=PaymentMethod.COD,
            shipping_address="123 Test Street",
            phone_number="0123456789",
            notes="",
            status=OrderStatus.PENDING,
            total_amount=total_amount,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        order2 = Order.reconstruct(
            order_id=2,
            customer_id=1,
            items=items,
            payment_method=PaymentMethod.COD,
            shipping_address="123 Test Street",
            phone_number="0123456789",
            notes="",
            status=OrderStatus.PENDING,
            total_amount=total_amount,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert order1 != order2
