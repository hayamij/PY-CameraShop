"""
Integration tests for ProductRepository
Tests the repository against a real database
"""
import pytest
from app.domain.entities.product import Product
from app.domain.value_objects.money import Money
from app.domain.exceptions import ProductNotFoundException
from app.adapters.repositories.product_repository_adapter import ProductRepositoryAdapter


class TestProductRepositoryIntegration:
    """Integration tests for ProductRepository"""

    def test_save_creates_product_in_database(self, product_repository, sample_category, sample_brand):
        """Test that save() creates a product in the database"""
        # Arrange
        product = Product(
            name="Test Camera XYZ",
            description="A test camera product",
            price=Money(1500.00),
            stock_quantity=10,
            category_id=sample_category.id,
            brand_id=sample_brand.id,
            image_url="http://example.com/test.jpg"
        )

        # Act
        saved_product = product_repository.save(product)

        # Assert
        assert saved_product.id is not None
        assert saved_product.name == "Test Camera XYZ"
        assert saved_product.price.amount == 1500.00
        assert saved_product.stock_quantity == 10
        assert saved_product.is_available_for_purchase() is True

    def test_find_by_id_retrieves_correct_product(self, product_repository, sample_product):
        """Test that find_by_id() retrieves the correct product"""
        # Act
        found_product = product_repository.find_by_id(sample_product.id)

        # Assert
        assert found_product is not None
        assert found_product.id == sample_product.id
        assert found_product.name == sample_product.name
        assert found_product.price.amount == sample_product.price.amount

    def test_find_by_id_returns_none_when_not_found(self, product_repository):
        """Test that find_by_id() returns None when product doesn't exist"""
        # Act
        result = product_repository.find_by_id(99999)
        
        # Assert
        assert result is None

    def test_find_all_returns_products(self, product_repository, sample_product):
        """Test that find_all() returns a list of products"""
        # Act
        products = product_repository.find_all(skip=0, limit=10, visible_only=False)

        # Assert
        assert len(products) > 0
        assert any(p.id == sample_product.id for p in products)

    def test_find_by_category_filters_correctly(self, product_repository, sample_product):
        """Test that find_by_category() filters by category correctly"""
        # Act
        products = product_repository.find_by_category(
            category_id=sample_product.category_id,
            skip=0,
            limit=10
        )

        # Assert
        assert len(products) > 0
        assert all(p.category_id == sample_product.category_id for p in products)

    def test_find_by_brand_filters_correctly(self, product_repository, sample_product):
        """Test that find_by_brand() filters by brand correctly"""
        # Act
        products = product_repository.find_by_brand(
            brand_id=sample_product.brand_id,
            skip=0,
            limit=10
        )

        # Assert
        assert len(products) > 0
        assert all(p.brand_id == sample_product.brand_id for p in products)

    def test_visible_only_filter_works(self, product_repository, sample_product):
        """Test that visible_only parameter filters correctly"""
        # Act - Get only visible products
        visible_products = product_repository.find_all(skip=0, limit=10, visible_only=True)

        # Assert
        assert len(visible_products) > 0
        assert all(p.is_visible for p in visible_products)

    def test_pagination_with_skip_and_limit(self, product_repository):
        """Test that skip and limit pagination works correctly"""
        # Act - Get first 3 products
        page1 = product_repository.find_all(skip=0, limit=3, visible_only=False)
        
        # Act - Get next 3 products
        page2 = product_repository.find_all(skip=3, limit=3, visible_only=False)

        # Assert
        assert len(page1) <= 3
        assert len(page2) <= 3
        # Products should be different
        if len(page1) > 0 and len(page2) > 0:
            page1_ids = {p.id for p in page1}
            page2_ids = {p.id for p in page2}
            assert page1_ids.isdisjoint(page2_ids)

    def test_count_products_returns_correct_count(self, product_repository, sample_product):
        """Test that count() returns the correct number of products"""
        # Act
        count = product_repository.count()

        # Assert
        assert count > 0
        assert isinstance(count, int)

    def test_update_product_successfully(self, product_repository, sample_product):
        """Test that update() updates product information"""
        # Arrange
        original_name = sample_product.name
        sample_product.update_details(name="Updated Product Name")
        sample_product.add_stock(49)  # sample_product has stock_quantity=50, add 49 to get 99

        # Act
        updated_product = product_repository.save(sample_product)

        # Assert
        assert updated_product.name == "Updated Product Name"
        assert updated_product.stock_quantity == 99
        
        # Verify it persisted
        found_product = product_repository.find_by_id(sample_product.id)
        assert found_product.name == "Updated Product Name"
        assert found_product.stock_quantity == 99

    def test_product_availability_updates_based_on_stock(self, product_repository, sample_product):
        """Test that product availability updates when stock changes"""
        # Arrange - Reduce stock to 0
        sample_product.reduce_stock(sample_product.stock_quantity)

        # Act
        updated_product = product_repository.save(sample_product)

        # Assert
        assert updated_product.is_in_stock() is False
        assert updated_product.is_available_for_purchase() is False
        
        # Arrange - Add stock back
        updated_product.add_stock(5)
        
        # Act
        updated_product = product_repository.save(updated_product)
        
        # Assert
        assert updated_product.is_in_stock() is True
        assert updated_product.is_available_for_purchase() is True
