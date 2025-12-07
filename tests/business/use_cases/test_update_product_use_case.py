"""
Test suite for UpdateProductUseCase

Test Coverage:
- Success cases: Update product with various field combinations
- Validation cases: Invalid product_id, name, description, price, stock, category, brand
- Not found cases: Product/Category/Brand doesn't exist
- Duplicate cases: Name already exists for different product
- Visibility cases: Show/hide product
- Stock change cases: Increase/decrease stock
- Repository exception cases
- Output structure validation
"""

import pytest
from unittest.mock import Mock
from decimal import Decimal

from app.business.use_cases.update_product_use_case import (
    UpdateProductUseCase,
    UpdateProductInputData,
    UpdateProductOutputData
)
from app.domain.entities.product import Product
from app.domain.value_objects.money import Money
from app.domain.exceptions import (
    ProductNotFoundException,
    ValidationException,
    CategoryNotFoundException,
    BrandNotFoundException
)


class TestUpdateProductUseCase:
    """Test cases for UpdateProductUseCase"""
    
    # ============ FIXTURES ============
    
    @pytest.fixture
    def product_repository(self):
        """Mock product repository"""
        return Mock()
    
    @pytest.fixture
    def category_repository(self):
        """Mock category repository"""
        return Mock()
    
    @pytest.fixture
    def brand_repository(self):
        """Mock brand repository"""
        return Mock()
    
    @pytest.fixture
    def use_case(self, product_repository, category_repository, brand_repository):
        """Create use case instance"""
        return UpdateProductUseCase(product_repository, category_repository, brand_repository)
    
    # ============ HELPER METHODS ============
    
    def create_mock_product(self, product_id, name, description, price, stock, category_id, brand_id, is_visible=True):
        """Create mock product"""
        product = Mock(spec=Product)
        product.id = product_id
        product.name = name
        product.description = description
        product.price = Money(Decimal(str(price)), "VND")
        product.stock_quantity = stock
        product.category_id = category_id
        product.brand_id = brand_id
        product.is_visible = is_visible
        product.update_details = Mock()
        product.add_stock = Mock()
        product.reduce_stock = Mock()
        product.show = Mock()
        product.hide = Mock()
        return product
    
    def create_mock_category(self, category_id, name):
        """Create mock category"""
        category = Mock()
        category.id = category_id
        category.name = name
        return category
    
    def create_mock_brand(self, brand_id, name):
        """Create mock brand"""
        brand = Mock()
        brand.id = brand_id
        brand.name = name
        return brand
    
    # ============ SUCCESS CASES ============
    
    def test_update_product_success(self, use_case, product_repository, category_repository, brand_repository):
        """Test successfully updating a product"""
        # Arrange
        existing_product = self.create_mock_product(10, "Old Name", "Old description", 1000000, 5, 1, 1)
        category = self.create_mock_category(1, "Cameras")
        brand = self.create_mock_brand(1, "Canon")
        
        product_repository.find_by_id.side_effect = lambda pid: existing_product if pid == 10 else None
        category_repository.find_by_id.side_effect = lambda cid: category if cid == 1 else None
        brand_repository.find_by_id.side_effect = lambda bid: brand if bid == 1 else None
        product_repository.find_by_name.side_effect = lambda name: None
        product_repository.save.return_value = existing_product
        
        input_data = UpdateProductInputData(
            product_id=10,
            name="Canon EOS R5",
            description="Professional mirrorless camera with 45MP sensor",
            price=89900000,
            stock_quantity=10,
            category_id=1,
            brand_id=1,
            image_url="/images/canon-eos-r5.jpg",
            is_visible=True
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.product_id == 10
        assert "thành công" in output.message.lower()
        
        # Verify domain methods called
        existing_product.update_details.assert_called_once()
        product_repository.save.assert_called_once()
    
    def test_update_product_name_only(self, use_case, product_repository, category_repository, brand_repository):
        """Test updating only product name"""
        # Arrange
        existing_product = self.create_mock_product(10, "Old Name", "Description text here", 1000000, 5, 1, 1)
        category = self.create_mock_category(1, "Cameras")
        brand = self.create_mock_brand(1, "Canon")
        
        product_repository.find_by_id.side_effect = lambda pid: existing_product if pid == 10 else None
        category_repository.find_by_id.side_effect = lambda cid: category if cid == 1 else None
        brand_repository.find_by_id.side_effect = lambda bid: brand if bid == 1 else None
        product_repository.find_by_name.side_effect = lambda name: None
        product_repository.save.return_value = existing_product
        
        input_data = UpdateProductInputData(
            product_id=10,
            name="New Name",
            description="Description text here",
            price=1000000,
            stock_quantity=5,
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
    
    def test_update_product_increase_stock(self, use_case, product_repository, category_repository, brand_repository):
        """Test updating product with increased stock"""
        # Arrange
        existing_product = self.create_mock_product(10, "Product", "Description text here", 1000000, 5, 1, 1)
        category = self.create_mock_category(1, "Cameras")
        brand = self.create_mock_brand(1, "Canon")
        
        product_repository.find_by_id.side_effect = lambda pid: existing_product if pid == 10 else None
        category_repository.find_by_id.side_effect = lambda cid: category if cid == 1 else None
        brand_repository.find_by_id.side_effect = lambda bid: brand if bid == 1 else None
        product_repository.find_by_name.side_effect = lambda name: None
        product_repository.save.return_value = existing_product
        
        input_data = UpdateProductInputData(
            product_id=10,
            name="Product",
            description="Description text here",
            price=1000000,
            stock_quantity=15,  # Increased from 5 to 15
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        existing_product.add_stock.assert_called_once_with(10)
    
    def test_update_product_decrease_stock(self, use_case, product_repository, category_repository, brand_repository):
        """Test updating product with decreased stock"""
        # Arrange
        existing_product = self.create_mock_product(10, "Product", "Description text here", 1000000, 15, 1, 1)
        category = self.create_mock_category(1, "Cameras")
        brand = self.create_mock_brand(1, "Canon")
        
        product_repository.find_by_id.side_effect = lambda pid: existing_product if pid == 10 else None
        category_repository.find_by_id.side_effect = lambda cid: category if cid == 1 else None
        brand_repository.find_by_id.side_effect = lambda bid: brand if bid == 1 else None
        product_repository.find_by_name.side_effect = lambda name: None
        product_repository.save.return_value = existing_product
        
        input_data = UpdateProductInputData(
            product_id=10,
            name="Product",
            description="Description text here",
            price=1000000,
            stock_quantity=5,  # Decreased from 15 to 5
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        existing_product.reduce_stock.assert_called_once_with(10)
    
    def test_update_product_hide(self, use_case, product_repository, category_repository, brand_repository):
        """Test hiding a visible product"""
        # Arrange
        existing_product = self.create_mock_product(10, "Product", "Description text here", 1000000, 5, 1, 1, is_visible=True)
        category = self.create_mock_category(1, "Cameras")
        brand = self.create_mock_brand(1, "Canon")
        
        product_repository.find_by_id.side_effect = lambda pid: existing_product if pid == 10 else None
        category_repository.find_by_id.side_effect = lambda cid: category if cid == 1 else None
        brand_repository.find_by_id.side_effect = lambda bid: brand if bid == 1 else None
        product_repository.find_by_name.side_effect = lambda name: None
        product_repository.save.return_value = existing_product
        
        input_data = UpdateProductInputData(
            product_id=10,
            name="Product",
            description="Description text here",
            price=1000000,
            stock_quantity=5,
            category_id=1,
            brand_id=1,
            is_visible=False
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        existing_product.hide.assert_called_once()
    
    def test_update_product_show(self, use_case, product_repository, category_repository, brand_repository):
        """Test showing a hidden product"""
        # Arrange
        existing_product = self.create_mock_product(10, "Product", "Description text here", 1000000, 5, 1, 1, is_visible=False)
        category = self.create_mock_category(1, "Cameras")
        brand = self.create_mock_brand(1, "Canon")
        
        product_repository.find_by_id.side_effect = lambda pid: existing_product if pid == 10 else None
        category_repository.find_by_id.side_effect = lambda cid: category if cid == 1 else None
        brand_repository.find_by_id.side_effect = lambda bid: brand if bid == 1 else None
        product_repository.find_by_name.side_effect = lambda name: None
        product_repository.save.return_value = existing_product
        
        input_data = UpdateProductInputData(
            product_id=10,
            name="Product",
            description="Description text here",
            price=1000000,
            stock_quantity=5,
            category_id=1,
            brand_id=1,
            is_visible=True
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        existing_product.show.assert_called_once()
    
    # ============ VALIDATION CASES - PRODUCT_ID ============
    
    def test_update_product_with_invalid_product_id_zero_fails(self, use_case, product_repository):
        """Test updating with invalid product ID (zero)"""
        # Arrange
        input_data = UpdateProductInputData(
            product_id=0,
            name="Product",
            description="Description text here",
            price=1000000,
            stock_quantity=5,
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "id" in output.message.lower()
        product_repository.find_by_id.assert_not_called()
    
    def test_update_product_with_negative_product_id_fails(self, use_case, product_repository):
        """Test updating with negative product ID"""
        # Arrange
        input_data = UpdateProductInputData(
            product_id=-1,
            name="Product",
            description="Description text here",
            price=1000000,
            stock_quantity=5,
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "id" in output.message.lower()
        product_repository.find_by_id.assert_not_called()
    
    # ============ VALIDATION CASES - NAME ============
    
    def test_update_product_with_empty_name_fails(self, use_case, product_repository):
        """Test updating with empty name"""
        # Arrange
        input_data = UpdateProductInputData(
            product_id=10,
            name="",
            description="Description text here",
            price=1000000,
            stock_quantity=5,
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "tên" in output.message.lower()
    
    def test_update_product_with_short_name_fails(self, use_case, product_repository):
        """Test updating with name too short"""
        # Arrange
        input_data = UpdateProductInputData(
            product_id=10,
            name="AB",
            description="Description text here",
            price=1000000,
            stock_quantity=5,
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "tên" in output.message.lower() and "3" in output.message
    
    # ============ VALIDATION CASES - DESCRIPTION ============
    
    def test_update_product_with_empty_description_fails(self, use_case, product_repository):
        """Test updating with empty description"""
        # Arrange
        input_data = UpdateProductInputData(
            product_id=10,
            name="Product Name",
            description="",
            price=1000000,
            stock_quantity=5,
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "mô tả" in output.message.lower()
    
    def test_update_product_with_short_description_fails(self, use_case, product_repository):
        """Test updating with description too short"""
        # Arrange
        input_data = UpdateProductInputData(
            product_id=10,
            name="Product Name",
            description="Short",
            price=1000000,
            stock_quantity=5,
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "mô tả" in output.message.lower() and "10" in output.message
    
    # ============ VALIDATION CASES - PRICE ============
    
    def test_update_product_with_zero_price_fails(self, use_case, product_repository):
        """Test updating with zero price"""
        # Arrange
        input_data = UpdateProductInputData(
            product_id=10,
            name="Product Name",
            description="Description text here",
            price=0,
            stock_quantity=5,
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "giá" in output.message.lower()
    
    def test_update_product_with_negative_price_fails(self, use_case, product_repository):
        """Test updating with negative price"""
        # Arrange
        input_data = UpdateProductInputData(
            product_id=10,
            name="Product Name",
            description="Description text here",
            price=-1000000,
            stock_quantity=5,
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "giá" in output.message.lower()
    
    # ============ VALIDATION CASES - STOCK ============
    
    def test_update_product_with_negative_stock_fails(self, use_case, product_repository):
        """Test updating with negative stock"""
        # Arrange
        input_data = UpdateProductInputData(
            product_id=10,
            name="Product Name",
            description="Description text here",
            price=1000000,
            stock_quantity=-5,
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "tồn kho" in output.message.lower()
    
    # ============ VALIDATION CASES - CATEGORY/BRAND ============
    
    def test_update_product_with_invalid_category_id_fails(self, use_case, product_repository):
        """Test updating with invalid category ID"""
        # Arrange
        input_data = UpdateProductInputData(
            product_id=10,
            name="Product Name",
            description="Description text here",
            price=1000000,
            stock_quantity=5,
            category_id=0,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "danh mục" in output.message.lower()
    
    def test_update_product_with_invalid_brand_id_fails(self, use_case, product_repository):
        """Test updating with invalid brand ID"""
        # Arrange
        input_data = UpdateProductInputData(
            product_id=10,
            name="Product Name",
            description="Description text here",
            price=1000000,
            stock_quantity=5,
            category_id=1,
            brand_id=0
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "thương hiệu" in output.message.lower()
    
    # ============ NOT FOUND CASES ============
    
    def test_update_nonexistent_product_fails(self, use_case, product_repository):
        """Test updating non-existent product"""
        # Arrange
        product_repository.find_by_id.side_effect = lambda pid: None
        
        input_data = UpdateProductInputData(
            product_id=999,
            name="Product Name",
            description="Description text here",
            price=1000000,
            stock_quantity=5,
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "not found" in output.message.lower() or "không tìm thấy" in output.message.lower()
    
    def test_update_product_with_nonexistent_category_fails(self, use_case, product_repository, category_repository, brand_repository):
        """Test updating with non-existent category"""
        # Arrange
        existing_product = self.create_mock_product(10, "Product", "Description text here", 1000000, 5, 1, 1)
        
        product_repository.find_by_id.side_effect = lambda pid: existing_product if pid == 10 else None
        category_repository.find_by_id.side_effect = lambda cid: None
        
        input_data = UpdateProductInputData(
            product_id=10,
            name="Product Name",
            description="Description text here",
            price=1000000,
            stock_quantity=5,
            category_id=999,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "not found" in output.message.lower() or "không tìm thấy" in output.message.lower()
    
    def test_update_product_with_nonexistent_brand_fails(self, use_case, product_repository, category_repository, brand_repository):
        """Test updating with non-existent brand"""
        # Arrange
        existing_product = self.create_mock_product(10, "Product", "Description text here", 1000000, 5, 1, 1)
        category = self.create_mock_category(1, "Cameras")
        
        product_repository.find_by_id.side_effect = lambda pid: existing_product if pid == 10 else None
        category_repository.find_by_id.side_effect = lambda cid: category if cid == 1 else None
        brand_repository.find_by_id.side_effect = lambda bid: None
        
        input_data = UpdateProductInputData(
            product_id=10,
            name="Product Name",
            description="Description text here",
            price=1000000,
            stock_quantity=5,
            category_id=1,
            brand_id=999
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "not found" in output.message.lower() or "không tìm thấy" in output.message.lower()
    
    # ============ DUPLICATE CASES ============
    
    def test_update_product_with_duplicate_name_fails(self, use_case, product_repository, category_repository, brand_repository):
        """Test updating product with name that exists for another product"""
        # Arrange
        existing_product = self.create_mock_product(10, "Old Name", "Description text here", 1000000, 5, 1, 1)
        other_product = self.create_mock_product(20, "Existing Name", "Other description", 2000000, 3, 1, 1)
        category = self.create_mock_category(1, "Cameras")
        brand = self.create_mock_brand(1, "Canon")
        
        product_repository.find_by_id.side_effect = lambda pid: existing_product if pid == 10 else None
        category_repository.find_by_id.side_effect = lambda cid: category if cid == 1 else None
        brand_repository.find_by_id.side_effect = lambda bid: brand if bid == 1 else None
        product_repository.find_by_name.side_effect = lambda name: other_product if name == "Existing Name" else None
        
        input_data = UpdateProductInputData(
            product_id=10,
            name="Existing Name",
            description="Description text here",
            price=1000000,
            stock_quantity=5,
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "đã tồn tại" in output.message.lower()
    
    def test_update_product_keep_same_name_success(self, use_case, product_repository, category_repository, brand_repository):
        """Test updating product keeping the same name (should succeed)"""
        # Arrange
        existing_product = self.create_mock_product(10, "Product Name", "Description text here", 1000000, 5, 1, 1)
        category = self.create_mock_category(1, "Cameras")
        brand = self.create_mock_brand(1, "Canon")
        
        product_repository.find_by_id.side_effect = lambda pid: existing_product if pid == 10 else None
        category_repository.find_by_id.side_effect = lambda cid: category if cid == 1 else None
        brand_repository.find_by_id.side_effect = lambda bid: brand if bid == 1 else None
        product_repository.find_by_name.side_effect = lambda name: existing_product if name == "Product Name" else None
        product_repository.save.return_value = existing_product
        
        input_data = UpdateProductInputData(
            product_id=10,
            name="Product Name",
            description="New description text for product",
            price=2000000,
            stock_quantity=10,
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
    
    # ============ REPOSITORY EXCEPTION CASES ============
    
    def test_repository_exception_product_find(self, use_case, product_repository):
        """Test repository exception during product find"""
        # Arrange
        product_repository.find_by_id.side_effect = Exception("Database connection error")
        
        input_data = UpdateProductInputData(
            product_id=10,
            name="Product Name",
            description="Description text here",
            price=1000000,
            stock_quantity=5,
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "lỗi" in output.message.lower()
    
    def test_repository_exception_product_save(self, use_case, product_repository, category_repository, brand_repository):
        """Test repository exception during product save"""
        # Arrange
        existing_product = self.create_mock_product(10, "Product", "Description text here", 1000000, 5, 1, 1)
        category = self.create_mock_category(1, "Cameras")
        brand = self.create_mock_brand(1, "Canon")
        
        product_repository.find_by_id.side_effect = lambda pid: existing_product if pid == 10 else None
        category_repository.find_by_id.side_effect = lambda cid: category if cid == 1 else None
        brand_repository.find_by_id.side_effect = lambda bid: brand if bid == 1 else None
        product_repository.find_by_name.side_effect = lambda name: None
        product_repository.save.side_effect = Exception("Database save error")
        
        input_data = UpdateProductInputData(
            product_id=10,
            name="New Product Name",
            description="Description text here",
            price=2000000,
            stock_quantity=10,
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "lỗi" in output.message.lower()
    
    # ============ OUTPUT STRUCTURE VALIDATION ============
    
    def test_output_data_structure_on_success(self, use_case, product_repository, category_repository, brand_repository):
        """Test output data structure on success"""
        # Arrange
        existing_product = self.create_mock_product(10, "Product", "Description text here", 1000000, 5, 1, 1)
        category = self.create_mock_category(1, "Cameras")
        brand = self.create_mock_brand(1, "Canon")
        
        product_repository.find_by_id.side_effect = lambda pid: existing_product if pid == 10 else None
        category_repository.find_by_id.side_effect = lambda cid: category if cid == 1 else None
        brand_repository.find_by_id.side_effect = lambda bid: brand if bid == 1 else None
        product_repository.find_by_name.side_effect = lambda name: None
        product_repository.save.return_value = existing_product
        
        input_data = UpdateProductInputData(
            product_id=10,
            name="Updated Name",
            description="Updated description text for product",
            price=2000000,
            stock_quantity=10,
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert hasattr(output, 'success')
        assert hasattr(output, 'product_id')
        assert hasattr(output, 'product_name')
        assert hasattr(output, 'message')
        
        assert isinstance(output.success, bool)
        assert isinstance(output.product_id, int)
        assert isinstance(output.product_name, str)
        assert isinstance(output.message, str)
    
    def test_output_data_structure_on_failure(self, use_case, product_repository):
        """Test output data structure on failure"""
        # Arrange
        input_data = UpdateProductInputData(
            product_id=0,
            name="Product",
            description="Description",
            price=1000000,
            stock_quantity=5,
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert hasattr(output, 'message')
        assert isinstance(output.message, str)
        assert len(output.message) > 0
