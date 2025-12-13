"""
Tests for Product domain entity
"""
import pytest
from datetime import datetime
from decimal import Decimal
from app.domain.entities.product import Product
from app.domain.value_objects import Money
from app.domain.exceptions import InvalidProductPriceException, InsufficientStockException


class TestProductCreation:
    """Test Product entity creation"""
    
    def test_create_valid_product(self):
        """Should create product with valid data"""
        price = Money(Decimal("1000000"))
        
        product = Product(
            name="Canon EOS 90D",
            description="Professional DSLR camera",
            price=price,
            stock_quantity=10,
            category_id=1,
            brand_id=1,
            image_url="https://example.com/image.jpg"
        )
        
        assert product.name == "Canon EOS 90D"
        assert product.description == "Professional DSLR camera"
        assert product.price == price
        assert product.stock_quantity == 10
        assert product.category_id == 1
        assert product.brand_id == 1
        assert product.image_url == "https://example.com/image.jpg"
        assert product.is_visible is True
        assert product.id is None
    
    def test_create_product_without_image(self):
        """Should create product without image URL"""
        price = Money(Decimal("1000000"))
        
        product = Product(
            name="Canon EOS 90D",
            description="Professional DSLR camera",
            price=price,
            stock_quantity=10,
            category_id=1,
            brand_id=1
        )
        
        assert product.image_url is None
    
    def test_create_product_strips_whitespace(self):
        """Should strip whitespace from string fields"""
        price = Money(Decimal("1000000"))
        
        product = Product(
            name="  Canon EOS 90D  ",
            description="  Professional DSLR camera  ",
            price=price,
            stock_quantity=10,
            category_id=1,
            brand_id=1
        )
        
        assert product.name == "Canon EOS 90D"
        assert product.description == "Professional DSLR camera"
    
    def test_create_product_invalid_name_too_short(self):
        """Should raise error for name less than 2 characters"""
        price = Money(Decimal("1000000"))
        
        with pytest.raises(ValueError, match="Product name must be at least 2 characters"):
            Product(
                name="A",
                description="Test description",
                price=price,
                stock_quantity=10,
                category_id=1,
                brand_id=1
            )
    
    def test_create_product_invalid_name_empty(self):
        """Should raise error for empty name"""
        price = Money(Decimal("1000000"))
        
        with pytest.raises(ValueError, match="Product name must be at least 2 characters"):
            Product(
                name="",
                description="Test description",
                price=price,
                stock_quantity=10,
                category_id=1,
                brand_id=1
            )
    
    def test_create_product_invalid_description_empty(self):
        """Should raise error for empty description"""
        price = Money(Decimal("1000000"))
        
        with pytest.raises(ValueError, match="Product description cannot be empty"):
            Product(
                name="Canon EOS 90D",
                description="",
                price=price,
                stock_quantity=10,
                category_id=1,
                brand_id=1
            )
    
    def test_create_product_invalid_price_zero(self):
        """Should raise error for zero price"""
        price = Money(Decimal("0"))
        
        with pytest.raises(InvalidProductPriceException):
            Product(
                name="Canon EOS 90D",
                description="Test description",
                price=price,
                stock_quantity=10,
                category_id=1,
                brand_id=1
            )
    
    def test_create_product_invalid_price_negative(self):
        """Should raise error for negative price (Money prevents this)"""
        with pytest.raises(ValueError, match="Money amount cannot be negative"):
            Money(Decimal("-1000"))
    
    def test_create_product_invalid_stock_negative(self):
        """Should raise error for negative stock quantity"""
        price = Money(Decimal("1000000"))
        
        with pytest.raises(ValueError, match="Stock quantity cannot be negative"):
            Product(
                name="Canon EOS 90D",
                description="Test description",
                price=price,
                stock_quantity=-1,
                category_id=1,
                brand_id=1
            )
    
    def test_create_product_invalid_category_id(self):
        """Should raise error for invalid category ID"""
        price = Money(Decimal("1000000"))
        
        with pytest.raises(ValueError, match="Invalid category ID"):
            Product(
                name="Canon EOS 90D",
                description="Test description",
                price=price,
                stock_quantity=10,
                category_id=0,
                brand_id=1
            )
    
    def test_create_product_invalid_brand_id(self):
        """Should raise error for invalid brand ID"""
        price = Money(Decimal("1000000"))
        
        with pytest.raises(ValueError, match="Invalid brand ID"):
            Product(
                name="Canon EOS 90D",
                description="Test description",
                price=price,
                stock_quantity=10,
                category_id=1,
                brand_id=0
            )


class TestProductReconstruction:
    """Test Product reconstruction from database"""
    
    def test_reconstruct_product(self):
        """Should reconstruct product from database without validation"""
        price = Money(Decimal("1000000"))
        created_at = datetime(2023, 1, 1, 12, 0, 0)
        
        product = Product.reconstruct(
            product_id=1,
            name="Canon EOS 90D",
            description="Professional DSLR camera",
            price=price,
            stock_quantity=10,
            category_id=1,
            brand_id=1,
            image_url="https://example.com/image.jpg",
            is_visible=False,
            created_at=created_at
        )
        
        assert product.id == 1
        assert product.name == "Canon EOS 90D"
        assert product.is_visible is False
        assert product.created_at == created_at


class TestProductBehavior:
    """Test Product entity behavior"""
    
    def test_update_price(self):
        """Should update product price"""
        old_price = Money(Decimal("1000000"))
        new_price = Money(Decimal("1200000"))
        
        product = Product(
            name="Canon EOS 90D",
            description="Professional DSLR camera",
            price=old_price,
            stock_quantity=10,
            category_id=1,
            brand_id=1
        )
        
        product.update_price(new_price)
        assert product.price == new_price
    
    def test_update_price_invalid_zero(self):
        """Should raise error for zero price"""
        price = Money(Decimal("1000000"))
        zero_price = Money(Decimal("0"))
        
        product = Product(
            name="Canon EOS 90D",
            description="Professional DSLR camera",
            price=price,
            stock_quantity=10,
            category_id=1,
            brand_id=1
        )
        
        with pytest.raises(InvalidProductPriceException):
            product.update_price(zero_price)
    
    def test_update_details(self):
        """Should update product details"""
        price = Money(Decimal("1000000"))
        
        product = Product(
            name="Canon EOS 90D",
            description="Professional DSLR camera",
            price=price,
            stock_quantity=10,
            category_id=1,
            brand_id=1
        )
        
        product.update_details(
            name="Canon EOS 90D Updated",
            description="Updated description",
            image_url="https://example.com/new-image.jpg"
        )
        
        assert product.name == "Canon EOS 90D Updated"
        assert product.description == "Updated description"
        assert product.image_url == "https://example.com/new-image.jpg"
    
    def test_update_details_invalid_name(self):
        """Should raise error for invalid name"""
        price = Money(Decimal("1000000"))
        
        product = Product(
            name="Canon EOS 90D",
            description="Professional DSLR camera",
            price=price,
            stock_quantity=10,
            category_id=1,
            brand_id=1
        )
        
        with pytest.raises(ValueError, match="Product name must be at least 2 characters"):
            product.update_details(name="A")
    
    def test_add_stock(self):
        """Should add stock quantity"""
        price = Money(Decimal("1000000"))
        
        product = Product(
            name="Canon EOS 90D",
            description="Professional DSLR camera",
            price=price,
            stock_quantity=10,
            category_id=1,
            brand_id=1
        )
        
        product.add_stock(5)
        assert product.stock_quantity == 15
    
    def test_add_stock_invalid_negative(self):
        """Should raise error for negative quantity"""
        price = Money(Decimal("1000000"))
        
        product = Product(
            name="Canon EOS 90D",
            description="Professional DSLR camera",
            price=price,
            stock_quantity=10,
            category_id=1,
            brand_id=1
        )
        
        with pytest.raises(ValueError, match="Quantity to add must be positive"):
            product.add_stock(-5)
    
    def test_reduce_stock(self):
        """Should reduce stock quantity"""
        price = Money(Decimal("1000000"))
        
        product = Product(
            name="Canon EOS 90D",
            description="Professional DSLR camera",
            price=price,
            stock_quantity=10,
            category_id=1,
            brand_id=1
        )
        
        product.reduce_stock(3)
        assert product.stock_quantity == 7
    
    def test_reduce_stock_insufficient(self):
        """Should raise error for insufficient stock"""
        price = Money(Decimal("1000000"))
        
        product = Product(
            name="Canon EOS 90D",
            description="Professional DSLR camera",
            price=price,
            stock_quantity=10,
            category_id=1,
            brand_id=1
        )
        
        with pytest.raises(InsufficientStockException):
            product.reduce_stock(15)
    
    def test_reduce_stock_invalid_negative(self):
        """Should raise error for negative quantity"""
        price = Money(Decimal("1000000"))
        
        product = Product(
            name="Canon EOS 90D",
            description="Professional DSLR camera",
            price=price,
            stock_quantity=10,
            category_id=1,
            brand_id=1
        )
        
        with pytest.raises(ValueError, match="Quantity to reduce must be positive"):
            product.reduce_stock(-5)
    
    def test_is_in_stock(self):
        """Should check if product is in stock"""
        price = Money(Decimal("1000000"))
        
        in_stock_product = Product(
            name="Canon EOS 90D",
            description="Professional DSLR camera",
            price=price,
            stock_quantity=10,
            category_id=1,
            brand_id=1
        )
        
        out_of_stock_product = Product(
            name="Nikon D850",
            description="Professional DSLR camera",
            price=price,
            stock_quantity=0,
            category_id=1,
            brand_id=2
        )
        
        assert in_stock_product.is_in_stock() is True
        assert out_of_stock_product.is_in_stock() is False
    
    def test_has_sufficient_stock(self):
        """Should check if product has sufficient stock"""
        price = Money(Decimal("1000000"))
        
        product = Product(
            name="Canon EOS 90D",
            description="Professional DSLR camera",
            price=price,
            stock_quantity=10,
            category_id=1,
            brand_id=1
        )
        
        assert product.has_sufficient_stock(5) is True
        assert product.has_sufficient_stock(10) is True
        assert product.has_sufficient_stock(15) is False
    
    def test_hide_product(self):
        """Should hide product"""
        price = Money(Decimal("1000000"))
        
        product = Product(
            name="Canon EOS 90D",
            description="Professional DSLR camera",
            price=price,
            stock_quantity=10,
            category_id=1,
            brand_id=1
        )
        
        assert product.is_visible is True
        product.hide()
        assert product.is_visible is False
    
    def test_show_product(self):
        """Should show product"""
        price = Money(Decimal("1000000"))
        
        product = Product.reconstruct(
            product_id=1,
            name="Canon EOS 90D",
            description="Professional DSLR camera",
            price=price,
            stock_quantity=10,
            category_id=1,
            brand_id=1,
            image_url=None,
            is_visible=False,
            created_at=datetime.now()
        )
        
        assert product.is_visible is False
        product.show()
        assert product.is_visible is True
    



class TestProductEquality:
    """Test Product equality comparison"""
    
    def test_products_with_same_id_are_equal(self):
        """Should consider products with same ID as equal"""
        price1 = Money(Decimal("1000000"))
        price2 = Money(Decimal("2000000"))
        
        product1 = Product.reconstruct(
            product_id=1,
            name="Canon EOS 90D",
            description="Description 1",
            price=price1,
            stock_quantity=10,
            category_id=1,
            brand_id=1,
            image_url=None,
            is_visible=True,
            created_at=datetime.now()
        )
        
        product2 = Product.reconstruct(
            product_id=1,
            name="Nikon D850",
            description="Description 2",
            price=price2,
            stock_quantity=20,
            category_id=2,
            brand_id=2,
            image_url=None,
            is_visible=False,
            created_at=datetime.now()
        )
        
        assert product1 == product2
    
    def test_products_with_different_id_are_not_equal(self):
        """Should consider products with different IDs as not equal"""
        price = Money(Decimal("1000000"))
        
        product1 = Product.reconstruct(
            product_id=1,
            name="Canon EOS 90D",
            description="Description",
            price=price,
            stock_quantity=10,
            category_id=1,
            brand_id=1,
            image_url=None,
            is_visible=True,
            created_at=datetime.now()
        )
        
        product2 = Product.reconstruct(
            product_id=2,
            name="Canon EOS 90D",
            description="Description",
            price=price,
            stock_quantity=10,
            category_id=1,
            brand_id=1,
            image_url=None,
            is_visible=True,
            created_at=datetime.now()
        )
        
        assert product1 != product2
