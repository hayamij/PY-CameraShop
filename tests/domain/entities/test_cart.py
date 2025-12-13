"""
Tests for Cart domain entity
"""
import pytest
from datetime import datetime
from app.domain.entities.cart import Cart, CartItem
from app.domain.exceptions import InvalidQuantityException, EmptyCartException, ProductNotFoundException


class TestCartItemCreation:
    """Test CartItem value object creation"""
    
    def test_create_valid_cart_item(self):
        """Should create cart item with valid data"""
        item = CartItem(product_id=1, quantity=2)
        
        assert item.product_id == 1
        assert item.quantity == 2
        assert item.cart_item_id is None
        assert item.cart_id is None
    
    def test_create_cart_item_with_ids(self):
        """Should create cart item with cart and item IDs"""
        item = CartItem(product_id=1, quantity=2, cart_item_id=10, cart_id=5)
        
        assert item.cart_item_id == 10
        assert item.cart_id == 5
    
    def test_create_cart_item_invalid_product_id(self):
        """Should raise error for invalid product ID"""
        with pytest.raises(ValueError, match="Invalid product ID"):
            CartItem(product_id=0, quantity=2)
    
    def test_create_cart_item_invalid_quantity_zero(self):
        """Should raise error for zero quantity"""
        with pytest.raises(InvalidQuantityException):
            CartItem(product_id=1, quantity=0)
    
    def test_create_cart_item_invalid_quantity_negative(self):
        """Should raise error for negative quantity"""
        with pytest.raises(InvalidQuantityException):
            CartItem(product_id=1, quantity=-1)
    
    def test_update_cart_item_quantity(self):
        """Should update item quantity"""
        item = CartItem(product_id=1, quantity=2)
        item.update_quantity(5)
        
        assert item.quantity == 5
    
    def test_update_cart_item_quantity_invalid(self):
        """Should raise error for invalid quantity update"""
        item = CartItem(product_id=1, quantity=2)
        
        with pytest.raises(InvalidQuantityException):
            item.update_quantity(0)
    
    def test_increase_cart_item_quantity(self):
        """Should increase item quantity"""
        item = CartItem(product_id=1, quantity=2)
        item.increase_quantity(3)
        
        assert item.quantity == 5
    
    def test_increase_cart_item_quantity_default(self):
        """Should increase by 1 by default"""
        item = CartItem(product_id=1, quantity=2)
        item.increase_quantity()
        
        assert item.quantity == 3
    
    def test_decrease_cart_item_quantity(self):
        """Should decrease item quantity"""
        item = CartItem(product_id=1, quantity=5)
        item.decrease_quantity(2)
        
        assert item.quantity == 3
    
    def test_decrease_cart_item_quantity_to_zero_raises_error(self):
        """Should raise error when decreasing to zero or below"""
        item = CartItem(product_id=1, quantity=2)
        
        with pytest.raises(InvalidQuantityException):
            item.decrease_quantity(2)
    
    def test_cart_item_equality(self):
        """Should check equality based on product_id"""
        item1 = CartItem(product_id=1, quantity=2)
        item2 = CartItem(product_id=1, quantity=5)
        item3 = CartItem(product_id=2, quantity=2)
        
        assert item1 == item2
        assert item1 != item3


class TestCartCreation:
    """Test Cart entity creation"""
    
    def test_create_valid_cart(self):
        """Should create cart with valid customer ID"""
        cart = Cart(customer_id=1)
        
        assert cart.customer_id == 1
        assert len(cart.items) == 0
        assert cart.id is None
    
    def test_create_cart_invalid_customer_id(self):
        """Should raise error for invalid customer ID"""
        with pytest.raises(ValueError, match="Invalid customer ID"):
            Cart(customer_id=0)


class TestCartReconstruction:
    """Test Cart reconstruction from database"""
    
    def test_reconstruct_cart(self):
        """Should reconstruct cart from database"""
        items = [
            CartItem(1, 2, cart_item_id=10, cart_id=5),
            CartItem(2, 3, cart_item_id=11, cart_id=5)
        ]
        created_at = datetime(2023, 1, 1, 12, 0, 0)
        updated_at = datetime(2023, 1, 2, 12, 0, 0)
        
        cart = Cart.reconstruct(
            cart_id=5,
            customer_id=1,
            items=items,
            created_at=created_at,
            updated_at=updated_at
        )
        
        assert cart.id == 5
        assert cart.customer_id == 1
        assert len(cart.items) == 2
        assert cart.created_at == created_at
        assert cart.updated_at == updated_at


class TestCartBehavior:
    """Test Cart entity behavior"""
    
    def test_add_item_to_empty_cart(self):
        """Should add item to empty cart"""
        cart = Cart(customer_id=1)
        cart.add_item(product_id=1, quantity=2)
        
        assert len(cart.items) == 1
        assert cart.items[0].product_id == 1
        assert cart.items[0].quantity == 2
    
    def test_add_multiple_items(self):
        """Should add multiple different items"""
        cart = Cart(customer_id=1)
        cart.add_item(product_id=1, quantity=2)
        cart.add_item(product_id=2, quantity=3)
        
        assert len(cart.items) == 2
    
    def test_add_existing_item_increases_quantity(self):
        """Should increase quantity when adding existing item"""
        cart = Cart(customer_id=1)
        cart.add_item(product_id=1, quantity=2)
        cart.add_item(product_id=1, quantity=3)
        
        assert len(cart.items) == 1
        assert cart.items[0].quantity == 5
    
    def test_add_item_invalid_product_id(self):
        """Should raise error for invalid product ID"""
        cart = Cart(customer_id=1)
        
        with pytest.raises(ValueError, match="Invalid product ID"):
            cart.add_item(product_id=0, quantity=2)
    
    def test_add_item_invalid_quantity(self):
        """Should raise error for invalid quantity"""
        cart = Cart(customer_id=1)
        
        with pytest.raises(InvalidQuantityException):
            cart.add_item(product_id=1, quantity=0)
    
    def test_remove_item(self):
        """Should remove item from cart"""
        cart = Cart(customer_id=1)
        cart.add_item(product_id=1, quantity=2)
        cart.add_item(product_id=2, quantity=3)
        
        cart.remove_item(product_id=1)
        
        assert len(cart.items) == 1
        assert cart.items[0].product_id == 2
    
    def test_remove_nonexistent_item(self):
        """Should raise error when removing non-existent item"""
        cart = Cart(customer_id=1)
        cart.add_item(product_id=1, quantity=2)
        
        with pytest.raises(ProductNotFoundException):
            cart.remove_item(product_id=999)
    
    def test_update_item_quantity(self):
        """Should update item quantity"""
        cart = Cart(customer_id=1)
        cart.add_item(product_id=1, quantity=2)
        cart.update_item_quantity(product_id=1, new_quantity=5)
        
        assert cart.items[0].quantity == 5
    
    def test_update_nonexistent_item(self):
        """Should raise error when updating non-existent item"""
        cart = Cart(customer_id=1)
        
        with pytest.raises(ProductNotFoundException):
            cart.update_item_quantity(product_id=999, new_quantity=5)
    
    def test_clear_cart(self):
        """Should clear all items from cart"""
        cart = Cart(customer_id=1)
        cart.add_item(product_id=1, quantity=2)
        cart.add_item(product_id=2, quantity=3)
        
        cart.clear()
        
        assert len(cart.items) == 0
        assert cart.is_empty() is True
    
    def test_is_empty(self):
        """Should check if cart is empty"""
        cart = Cart(customer_id=1)
        
        assert cart.is_empty() is True
        
        cart.add_item(product_id=1, quantity=2)
        assert cart.is_empty() is False
        
        cart.clear()
        assert cart.is_empty() is True
    
    def test_get_item_count(self):
        """Should get total number of items"""
        cart = Cart(customer_id=1)
        
        assert cart.get_item_count() == 0
        
        cart.add_item(product_id=1, quantity=2)
        cart.add_item(product_id=2, quantity=3)
        
        assert cart.get_item_count() == 2
    
    def test_get_total_quantity(self):
        """Should get total quantity of all items"""
        cart = Cart(customer_id=1)
        
        assert cart.get_total_quantity() == 0
        
        cart.add_item(product_id=1, quantity=2)
        cart.add_item(product_id=2, quantity=3)
        
        assert cart.get_total_quantity() == 5
    
    def test_has_item(self):
        """Should check if cart has specific item"""
        cart = Cart(customer_id=1)
        cart.add_item(product_id=1, quantity=2)
        
        assert cart.has_item(product_id=1) is True
        assert cart.has_item(product_id=999) is False
    
    def test_get_item(self):
        """Should get specific item from cart"""
        cart = Cart(customer_id=1)
        cart.add_item(product_id=1, quantity=2)
        
        item = cart.get_item(product_id=1)
        assert item.product_id == 1
        assert item.quantity == 2
    
    def test_get_nonexistent_item(self):
        """Should raise error when getting non-existent item"""
        cart = Cart(customer_id=1)
        
        with pytest.raises(ProductNotFoundException):
            cart.get_item(product_id=999)


class TestCartValidation:
    """Test Cart validation methods"""
    
    def test_validate_for_checkout_with_items(self):
        """Should validate successfully when cart has items"""
        cart = Cart(customer_id=1)
        cart.add_item(product_id=1, quantity=2)
        
        # Should not raise
        cart.validate_for_checkout()
    
    def test_validate_for_checkout_empty_cart(self):
        """Should raise error for empty cart"""
        cart = Cart(customer_id=1)
        
        with pytest.raises(EmptyCartException):
            cart.validate_for_checkout()


class TestCartEquality:
    """Test Cart equality comparison"""
    
    def test_carts_with_same_id_are_equal(self):
        """Should consider carts with same ID as equal"""
        cart1 = Cart.reconstruct(
            cart_id=1,
            customer_id=1,
            items=[CartItem(1, 2)],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        cart2 = Cart.reconstruct(
            cart_id=1,
            customer_id=2,
            items=[CartItem(2, 3)],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert cart1 == cart2
    
    def test_carts_with_different_id_are_not_equal(self):
        """Should consider carts with different IDs as not equal"""
        cart1 = Cart.reconstruct(
            cart_id=1,
            customer_id=1,
            items=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        cart2 = Cart.reconstruct(
            cart_id=2,
            customer_id=1,
            items=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert cart1 != cart2
