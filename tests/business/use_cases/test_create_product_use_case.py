"""
Test suite for CreateProductUseCase

Test Coverage:
- Success cases: Create product with valid data
- Validation cases: Invalid name, description, price, stock, category, brand
- Duplicate cases: Product name already exists
- Not found cases: Category/Brand doesn't exist
- Repository exception cases
- Output structure validation
"""

import pytest
from unittest.mock import Mock
from decimal import Decimal

from app.business.use_cases.create_product_use_case import (
    CreateProductUseCase,
    CreateProductInputData,
    CreateProductOutputData
)
from app.domain.entities.product import Product
from app.domain.value_objects.money import Money
from app.domain.exceptions import (
    ValidationException,
    CategoryNotFoundException,
    BrandNotFoundException
)


class TestCreateProductUseCase:
    """Test cases for CreateProductUseCase"""
    
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
        return CreateProductUseCase(product_repository, category_repository, brand_repository)
    
    # ============ HELPER METHODS ============
    
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
    
    def create_mock_product(self, product_id, name):
        """Create mock product"""
        product = Mock()
        product.id = product_id
        product.name = name
        return product
    
    # ============ SUCCESS CASES ============
    
    def test_create_product_success(self, use_case, product_repository, category_repository, brand_repository):
        """Test successfully creating a product"""
        # Arrange
        category = self.create_mock_category(1, "Cameras")
        brand = self.create_mock_brand(1, "Canon")
        saved_product = self.create_mock_product(10, "Canon EOS R5")
        
        category_repository.find_by_id.side_effect = lambda cid: category if cid == 1 else None
        brand_repository.find_by_id.side_effect = lambda bid: brand if bid == 1 else None
        product_repository.find_by_name.side_effect = lambda name: None
        product_repository.save.return_value = saved_product
        
        input_data = CreateProductInputData(
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
        assert output.product_name == "Canon EOS R5"
        assert "thành công" in output.message.lower()
        
        # Verify repository calls
        category_repository.find_by_id.assert_called_once_with(1)
        brand_repository.find_by_id.assert_called_once_with(1)
        product_repository.find_by_name.assert_called_once_with("Canon EOS R5")
        product_repository.save.assert_called_once()
    
    def test_create_product_with_minimal_data(self, use_case, product_repository, category_repository, brand_repository):
        """Test creating product with minimal required fields"""
        # Arrange
        category = self.create_mock_category(1, "Cameras")
        brand = self.create_mock_brand(1, "Sony")
        saved_product = self.create_mock_product(11, "Sony A7")
        
        category_repository.find_by_id.side_effect = lambda cid: category if cid == 1 else None
        brand_repository.find_by_id.side_effect = lambda bid: brand if bid == 1 else None
        product_repository.find_by_name.side_effect = lambda name: None
        product_repository.save.return_value = saved_product
        
        input_data = CreateProductInputData(
            name="Sony A7",
            description="Full-frame mirrorless camera",
            price=45000000,
            stock_quantity=5,
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.product_id == 11
    
    def test_create_product_with_zero_stock(self, use_case, product_repository, category_repository, brand_repository):
        """Test creating product with zero initial stock"""
        # Arrange
        category = self.create_mock_category(1, "Cameras")
        brand = self.create_mock_brand(1, "Nikon")
        saved_product = self.create_mock_product(12, "Nikon Z9")
        
        category_repository.find_by_id.side_effect = lambda cid: category if cid == 1 else None
        brand_repository.find_by_id.side_effect = lambda bid: brand if bid == 1 else None
        product_repository.find_by_name.side_effect = lambda name: None
        product_repository.save.return_value = saved_product
        
        input_data = CreateProductInputData(
            name="Nikon Z9",
            description="Professional flagship mirrorless camera",
            price=120000000,
            stock_quantity=0,
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
    
    def test_create_product_hidden_initially(self, use_case, product_repository, category_repository, brand_repository):
        """Test creating product as hidden"""
        # Arrange
        category = self.create_mock_category(1, "Cameras")
        brand = self.create_mock_brand(1, "Fujifilm")
        saved_product = self.create_mock_product(13, "Fujifilm X-T5")
        
        category_repository.find_by_id.side_effect = lambda cid: category if cid == 1 else None
        brand_repository.find_by_id.side_effect = lambda bid: brand if bid == 1 else None
        product_repository.find_by_name.side_effect = lambda name: None
        product_repository.save.return_value = saved_product
        
        input_data = CreateProductInputData(
            name="Fujifilm X-T5",
            description="APS-C mirrorless camera with film simulations",
            price=38000000,
            stock_quantity=8,
            category_id=1,
            brand_id=1,
            is_visible=False
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
    
    def test_create_product_with_large_stock(self, use_case, product_repository, category_repository, brand_repository):
        """Test creating product with large stock quantity"""
        # Arrange
        category = self.create_mock_category(2, "Accessories")
        brand = self.create_mock_brand(2, "Sandisk")
        saved_product = self.create_mock_product(14, "SD Card 64GB")
        
        category_repository.find_by_id.side_effect = lambda cid: category if cid == 2 else None
        brand_repository.find_by_id.side_effect = lambda bid: brand if bid == 2 else None
        product_repository.find_by_name.side_effect = lambda name: None
        product_repository.save.return_value = saved_product
        
        input_data = CreateProductInputData(
            name="SD Card 64GB",
            description="High-speed SD card for cameras",
            price=500000,
            stock_quantity=1000,
            category_id=2,
            brand_id=2
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
    
    # ============ VALIDATION CASES - NAME ============
    
    def test_create_product_with_empty_name_fails(self, use_case, product_repository):
        """Test creating product with empty name"""
        # Arrange
        input_data = CreateProductInputData(
            name="",
            description="Test description",
            price=1000000,
            stock_quantity=10,
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "tên" in output.message.lower()
        product_repository.save.assert_not_called()
    
    def test_create_product_with_short_name_fails(self, use_case, product_repository):
        """Test creating product with name too short"""
        # Arrange
        input_data = CreateProductInputData(
            name="AB",
            description="Test description",
            price=1000000,
            stock_quantity=10,
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "tên" in output.message.lower() and "3" in output.message
        product_repository.save.assert_not_called()
    
    def test_create_product_with_whitespace_only_name_fails(self, use_case, product_repository):
        """Test creating product with whitespace-only name"""
        # Arrange
        input_data = CreateProductInputData(
            name="   ",
            description="Test description",
            price=1000000,
            stock_quantity=10,
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "tên" in output.message.lower()
        product_repository.save.assert_not_called()
    
    # ============ VALIDATION CASES - DESCRIPTION ============
    
    def test_create_product_with_empty_description_fails(self, use_case, product_repository):
        """Test creating product with empty description"""
        # Arrange
        input_data = CreateProductInputData(
            name="Test Product",
            description="",
            price=1000000,
            stock_quantity=10,
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "mô tả" in output.message.lower()
        product_repository.save.assert_not_called()
    
    def test_create_product_with_short_description_fails(self, use_case, product_repository):
        """Test creating product with description too short"""
        # Arrange
        input_data = CreateProductInputData(
            name="Test Product",
            description="Short",
            price=1000000,
            stock_quantity=10,
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "mô tả" in output.message.lower() and "10" in output.message
        product_repository.save.assert_not_called()
    
    def test_create_product_with_whitespace_only_description_fails(self, use_case, product_repository):
        """Test creating product with whitespace-only description"""
        # Arrange
        input_data = CreateProductInputData(
            name="Test Product",
            description="          ",
            price=1000000,
            stock_quantity=10,
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "mô tả" in output.message.lower()
        product_repository.save.assert_not_called()
    
    # ============ VALIDATION CASES - PRICE ============
    
    def test_create_product_with_zero_price_fails(self, use_case, product_repository):
        """Test creating product with zero price"""
        # Arrange
        input_data = CreateProductInputData(
            name="Test Product",
            description="Test description for product",
            price=0,
            stock_quantity=10,
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "giá" in output.message.lower()
        product_repository.save.assert_not_called()
    
    def test_create_product_with_negative_price_fails(self, use_case, product_repository):
        """Test creating product with negative price"""
        # Arrange
        input_data = CreateProductInputData(
            name="Test Product",
            description="Test description for product",
            price=-1000000,
            stock_quantity=10,
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "giá" in output.message.lower()
        product_repository.save.assert_not_called()
    
    # ============ VALIDATION CASES - STOCK ============
    
    def test_create_product_with_negative_stock_fails(self, use_case, product_repository):
        """Test creating product with negative stock"""
        # Arrange
        input_data = CreateProductInputData(
            name="Test Product",
            description="Test description for product",
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
        product_repository.save.assert_not_called()
    
    # ============ VALIDATION CASES - CATEGORY/BRAND ============
    
    def test_create_product_with_invalid_category_id_zero_fails(self, use_case, product_repository):
        """Test creating product with invalid category ID (zero)"""
        # Arrange
        input_data = CreateProductInputData(
            name="Test Product",
            description="Test description for product",
            price=1000000,
            stock_quantity=10,
            category_id=0,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "danh mục" in output.message.lower()
        product_repository.save.assert_not_called()
    
    def test_create_product_with_negative_category_id_fails(self, use_case, product_repository):
        """Test creating product with negative category ID"""
        # Arrange
        input_data = CreateProductInputData(
            name="Test Product",
            description="Test description for product",
            price=1000000,
            stock_quantity=10,
            category_id=-1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "danh mục" in output.message.lower()
        product_repository.save.assert_not_called()
    
    def test_create_product_with_invalid_brand_id_zero_fails(self, use_case, product_repository):
        """Test creating product with invalid brand ID (zero)"""
        # Arrange
        input_data = CreateProductInputData(
            name="Test Product",
            description="Test description for product",
            price=1000000,
            stock_quantity=10,
            category_id=1,
            brand_id=0
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "thương hiệu" in output.message.lower()
        product_repository.save.assert_not_called()
    
    def test_create_product_with_negative_brand_id_fails(self, use_case, product_repository):
        """Test creating product with negative brand ID"""
        # Arrange
        input_data = CreateProductInputData(
            name="Test Product",
            description="Test description for product",
            price=1000000,
            stock_quantity=10,
            category_id=1,
            brand_id=-1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "thương hiệu" in output.message.lower()
        product_repository.save.assert_not_called()
    
    # ============ DUPLICATE CASES ============
    
    def test_create_product_with_duplicate_name_fails(self, use_case, product_repository, category_repository, brand_repository):
        """Test creating product with duplicate name"""
        # Arrange
        category = self.create_mock_category(1, "Cameras")
        brand = self.create_mock_brand(1, "Canon")
        existing_product = self.create_mock_product(5, "Canon EOS R5")
        
        category_repository.find_by_id.side_effect = lambda cid: category if cid == 1 else None
        brand_repository.find_by_id.side_effect = lambda bid: brand if bid == 1 else None
        product_repository.find_by_name.side_effect = lambda name: existing_product if name == "Canon EOS R5" else None
        
        input_data = CreateProductInputData(
            name="Canon EOS R5",
            description="Another Canon EOS R5 product",
            price=89900000,
            stock_quantity=10,
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "đã tồn tại" in output.message.lower()
        product_repository.save.assert_not_called()
    
    # ============ NOT FOUND CASES ============
    
    def test_create_product_with_nonexistent_category_fails(self, use_case, product_repository, category_repository, brand_repository):
        """Test creating product with non-existent category"""
        # Arrange
        brand = self.create_mock_brand(1, "Canon")
        
        category_repository.find_by_id.side_effect = lambda cid: None
        brand_repository.find_by_id.side_effect = lambda bid: brand if bid == 1 else None
        product_repository.find_by_name.side_effect = lambda name: None
        
        input_data = CreateProductInputData(
            name="Test Product",
            description="Test description for product",
            price=1000000,
            stock_quantity=10,
            category_id=999,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "not found" in output.message.lower() or "không tìm thấy" in output.message.lower()
        product_repository.save.assert_not_called()
    
    def test_create_product_with_nonexistent_brand_fails(self, use_case, product_repository, category_repository, brand_repository):
        """Test creating product with non-existent brand"""
        # Arrange
        category = self.create_mock_category(1, "Cameras")
        
        category_repository.find_by_id.side_effect = lambda cid: category if cid == 1 else None
        brand_repository.find_by_id.side_effect = lambda bid: None
        product_repository.find_by_name.side_effect = lambda name: None
        
        input_data = CreateProductInputData(
            name="Test Product",
            description="Test description for product",
            price=1000000,
            stock_quantity=10,
            category_id=1,
            brand_id=999
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "not found" in output.message.lower() or "không tìm thấy" in output.message.lower()
        product_repository.save.assert_not_called()
    
    # ============ REPOSITORY EXCEPTION CASES ============
    
    def test_repository_exception_category_find(self, use_case, category_repository):
        """Test repository exception during category find"""
        # Arrange
        category_repository.find_by_id.side_effect = Exception("Database connection error")
        
        input_data = CreateProductInputData(
            name="Test Product",
            description="Test description for product",
            price=1000000,
            stock_quantity=10,
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "lỗi" in output.message.lower()
    
    def test_repository_exception_brand_find(self, use_case, category_repository, brand_repository):
        """Test repository exception during brand find"""
        # Arrange
        category = self.create_mock_category(1, "Cameras")
        
        category_repository.find_by_id.side_effect = lambda cid: category if cid == 1 else None
        brand_repository.find_by_id.side_effect = Exception("Database connection error")
        
        input_data = CreateProductInputData(
            name="Test Product",
            description="Test description for product",
            price=1000000,
            stock_quantity=10,
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
        category = self.create_mock_category(1, "Cameras")
        brand = self.create_mock_brand(1, "Canon")
        
        category_repository.find_by_id.side_effect = lambda cid: category if cid == 1 else None
        brand_repository.find_by_id.side_effect = lambda bid: brand if bid == 1 else None
        product_repository.find_by_name.side_effect = lambda name: None
        product_repository.save.side_effect = Exception("Database save error")
        
        input_data = CreateProductInputData(
            name="Test Product",
            description="Test description for product",
            price=1000000,
            stock_quantity=10,
            category_id=1,
            brand_id=1
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert "lỗi" in output.message.lower()
    
    def test_repository_exception_duplicate_check(self, use_case, category_repository, brand_repository, product_repository):
        """Test repository exception during duplicate name check"""
        # Arrange
        category = self.create_mock_category(1, "Cameras")
        brand = self.create_mock_brand(1, "Canon")
        
        category_repository.find_by_id.side_effect = lambda cid: category if cid == 1 else None
        brand_repository.find_by_id.side_effect = lambda bid: brand if bid == 1 else None
        product_repository.find_by_name.side_effect = Exception("Database query error")
        
        input_data = CreateProductInputData(
            name="Test Product",
            description="Test description for product",
            price=1000000,
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
        category = self.create_mock_category(1, "Cameras")
        brand = self.create_mock_brand(1, "Canon")
        saved_product = self.create_mock_product(10, "Canon EOS R5")
        
        category_repository.find_by_id.side_effect = lambda cid: category if cid == 1 else None
        brand_repository.find_by_id.side_effect = lambda bid: brand if bid == 1 else None
        product_repository.find_by_name.side_effect = lambda name: None
        product_repository.save.return_value = saved_product
        
        input_data = CreateProductInputData(
            name="Canon EOS R5",
            description="Professional mirrorless camera",
            price=89900000,
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
        input_data = CreateProductInputData(
            name="",
            description="Test",
            price=1000000,
            stock_quantity=10,
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
