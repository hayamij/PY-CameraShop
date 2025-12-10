"""
Integration tests for CartRepositoryAdapter
Tests the adapter layer with real database operations
"""
import pytest
from app.domain.entities.cart import Cart, CartItem


class TestCartRepositoryIntegration:
    """Test CartRepositoryAdapter with real database"""
    
    def test_save_creates_cart_in_database(self, cart_repository, sample_user):
        """Test that save() creates a cart in the database"""
        # Arrange
        cart = Cart(customer_id=sample_user.id)
        cart.add_item(product_id=1, quantity=2)
        cart.add_item(product_id=2, quantity=1)
        
        # Act
        saved_cart = cart_repository.save(cart)
        
        # Assert
        assert saved_cart.id is not None
        assert saved_cart.customer_id == sample_user.id
        assert len(saved_cart.items) == 2
        
    def test_find_by_id_retrieves_correct_cart(self, cart_repository, sample_cart):
        """Test that find_by_id() retrieves the correct cart"""
        # Act
        found_cart = cart_repository.find_by_id(sample_cart.id)
        
        # Assert
        assert found_cart is not None
        assert found_cart.id == sample_cart.id
        assert found_cart.customer_id == sample_cart.customer_id
        assert len(found_cart.items) == len(sample_cart.items)
        
    def test_find_by_id_returns_none_when_not_found(self, cart_repository):
        """Test that find_by_id() returns None when cart not found"""
        # Act
        result = cart_repository.find_by_id(99999)
        
        # Assert
        assert result is None
        
    def test_find_by_customer_id_retrieves_cart(self, cart_repository, sample_cart):
        """Test that find_by_customer_id() retrieves customer's cart"""
        # Act
        found_cart = cart_repository.find_by_customer_id(sample_cart.customer_id)
        
        # Assert
        assert found_cart is not None
        assert found_cart.id == sample_cart.id
        assert found_cart.customer_id == sample_cart.customer_id
        
    def test_find_by_customer_id_returns_none_when_not_found(self, cart_repository):
        """Test that find_by_customer_id() returns None when no cart exists"""
        # Act
        result = cart_repository.find_by_customer_id(99999)
        
        # Assert
        assert result is None
        
    def test_add_item_to_existing_cart(self, cart_repository, sample_cart):
        """Test adding a new item to existing cart"""
        # Arrange
        original_item_count = len(sample_cart.items)
        sample_cart.add_item(product_id=999, quantity=3)
        
        # Act
        updated_cart = cart_repository.save(sample_cart)
        
        # Assert
        assert len(updated_cart.items) == original_item_count + 1
        
        # Verify persistence
        found_cart = cart_repository.find_by_id(sample_cart.id)
        assert len(found_cart.items) == original_item_count + 1
        
    def test_update_item_quantity_in_cart(self, cart_repository, sample_cart):
        """Test updating quantity of existing item"""
        # Arrange
        first_item = sample_cart.items[0]
        first_item.update_quantity(10)
        
        # Act
        updated_cart = cart_repository.save(sample_cart)
        
        # Assert
        updated_item = next(item for item in updated_cart.items if item.product_id == first_item.product_id)
        assert updated_item.quantity == 10
        
        # Verify persistence
        found_cart = cart_repository.find_by_id(sample_cart.id)
        found_item = next(item for item in found_cart.items if item.product_id == first_item.product_id)
        assert found_item.quantity == 10
        
    def test_remove_item_from_cart(self, cart_repository, sample_cart):
        """Test removing an item from cart"""
        # Arrange
        original_item_count = len(sample_cart.items)
        first_item = sample_cart.items[0]
        sample_cart.remove_item(first_item.product_id)
        
        # Act
        updated_cart = cart_repository.save(sample_cart)
        
        # Assert
        assert len(updated_cart.items) == original_item_count - 1
        assert not any(item.product_id == first_item.product_id for item in updated_cart.items)
        
    def test_clear_cart_removes_all_items(self, cart_repository, sample_cart):
        """Test that clear_cart() removes all items"""
        # Act
        result = cart_repository.clear_cart(sample_cart.customer_id)
        
        # Assert
        assert result is True
        
        # Verify cart still exists but is empty
        found_cart = cart_repository.find_by_customer_id(sample_cart.customer_id)
        assert found_cart is not None
        assert len(found_cart.items) == 0
        
    def test_clear_cart_returns_false_when_cart_not_found(self, cart_repository):
        """Test that clear_cart() returns False when cart doesn't exist"""
        # Act
        result = cart_repository.clear_cart(99999)
        
        # Assert
        assert result is False
        
    def test_delete_cart_removes_from_database(self, cart_repository, sample_cart):
        """Test that delete() removes cart from database"""
        # Arrange
        cart_id = sample_cart.id
        
        # Act
        result = cart_repository.delete(cart_id)
        
        # Assert
        assert result is True
        assert cart_repository.find_by_id(cart_id) is None
        
    def test_delete_returns_false_when_cart_not_found(self, cart_repository):
        """Test that delete() returns False when cart doesn't exist"""
        # Act
        result = cart_repository.delete(99999)
        
        # Assert
        assert result is False
        
    def test_one_cart_per_customer(self, cart_repository, sample_user):
        """Test that each customer has only one cart"""
        # Arrange - Create first cart
        cart1 = Cart(customer_id=sample_user.id)
        cart1.add_item(product_id=1, quantity=1)
        saved_cart1 = cart_repository.save(cart1)
        
        # Act - Find by customer should return the same cart
        found_cart = cart_repository.find_by_customer_id(sample_user.id)
        
        # Assert
        assert found_cart.id == saved_cart1.id
        
    def test_cart_items_persist_with_cart(self, cart_repository, sample_user):
        """Test that cart items are saved and loaded correctly"""
        # Arrange
        cart = Cart(customer_id=sample_user.id)
        cart.add_item(product_id=1, quantity=2)
        cart.add_item(product_id=2, quantity=3)
        cart.add_item(product_id=3, quantity=1)
        
        # Act
        saved_cart = cart_repository.save(cart)
        found_cart = cart_repository.find_by_id(saved_cart.id)
        
        # Assert
        assert len(found_cart.items) == 3
        
        # Verify each item
        product_ids = {item.product_id for item in found_cart.items}
        assert product_ids == {1, 2, 3}
        
        # Verify quantities
        item1 = next(item for item in found_cart.items if item.product_id == 1)
        item2 = next(item for item in found_cart.items if item.product_id == 2)
        item3 = next(item for item in found_cart.items if item.product_id == 3)
        
        assert item1.quantity == 2
        assert item2.quantity == 3
        assert item3.quantity == 1
