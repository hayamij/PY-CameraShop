"""
Unit Tests for GetProductDetailUseCase
Test mọi trường hợp lấy chi tiết sản phẩm
"""

import pytest
from unittest.mock import Mock
from decimal import Decimal

from app.business.use_cases.get_product_detail_use_case import (
    GetProductDetailUseCase,
    GetProductDetailInputData,
    GetProductDetailOutputData
)


class TestGetProductDetailUseCase:
    """Test suite cho GetProductDetailUseCase với đầy đủ các trường hợp"""
    
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
        """Khởi tạo use case"""
        return GetProductDetailUseCase(product_repository, category_repository, brand_repository)
    
    # ============ SUCCESS CASES ============
    
    def test_get_product_detail_success(self, use_case, product_repository, category_repository, brand_repository):
        """Test 1: Lấy chi tiết sản phẩm thành công"""
        # Arrange
        mock_product = Mock()
        mock_product.product_id = 1  # product_id, not id
        mock_product.name = "Canon EOS R5"
        mock_product.description = "Máy ảnh mirrorless full-frame"
        mock_product.price = Mock()
        mock_product.price.amount = Decimal("89000000")
        mock_product.price.currency = "VND"
        mock_product.category_id = 1
        mock_product.brand_id = 1
        mock_product.image_url = "/images/canon-eos-r5.jpg"
        mock_product.stock_quantity = 10
        mock_product.is_visible = True  # is_visible, not is_hidden
        mock_product.is_available_for_purchase = Mock(return_value=True)
        product_repository.find_by_id.return_value = mock_product
        
        # Mock category and brand
        mock_category = Mock()
        mock_category.name = "Mirrorless Camera"
        category_repository.find_by_id.return_value = mock_category
        
        mock_brand = Mock()
        mock_brand.name = "Canon"
        brand_repository.find_by_id.return_value = mock_brand
        
        input_data = GetProductDetailInputData(product_id=1)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.product_id == 1
        assert output.name == "Canon EOS R5"
        assert output.description == "Máy ảnh mirrorless full-frame"
        assert output.price == 89000000.0  # price is float
        assert output.currency == "VND"
        assert output.category_id == 1
        assert output.category_name == "Mirrorless Camera"
        assert output.brand_id == 1
        assert output.brand_name == "Canon"
        assert output.image_url == "/images/canon-eos-r5.jpg"
        assert output.stock_quantity == 10
        assert output.is_visible is True  # is_visible, not is_hidden
        assert output.is_available is True
        assert output.error_message is None
    
    def test_get_product_detail_with_all_fields(self, use_case, product_repository, category_repository, brand_repository):
        """Test 2: Sản phẩm có đầy đủ tất cả các field"""
        # Arrange
        mock_product = Mock()
        mock_product.product_id = 2
        mock_product.name = "Sony A7IV"
        mock_product.description = "Camera full-frame với khả năng quay video 4K"
        mock_product.price = Mock()
        mock_product.price.amount = Decimal("62000000")
        mock_product.price.currency = "VND"
        mock_product.category_id = 1
        mock_product.brand_id = 2
        mock_product.image_url = "/images/sony-a7iv.jpg"
        mock_product.stock_quantity = 5
        mock_product.is_visible = True
        mock_product.is_available_for_purchase = Mock(return_value=True)
        product_repository.find_by_id.return_value = mock_product
        
        category_repository.find_by_id.return_value = Mock(name="Camera")
        brand_repository.find_by_id.return_value = Mock(name="Sony")
        
        input_data = GetProductDetailInputData(product_id=2)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.product_id is not None
        assert output.name is not None
        assert output.description is not None
        assert output.price is not None
        assert output.currency is not None
        assert output.category_id is not None
        assert output.category_name is not None
        assert output.brand_id is not None
        assert output.brand_name is not None
        assert output.image_url is not None
        assert output.stock_quantity is not None
        assert output.is_visible is not None
        assert output.is_available is not None
    
    def test_get_product_detail_without_image(self, use_case, product_repository):
        """Test 3: Sản phẩm không có image"""
        # Arrange
        mock_product = Mock()
        mock_product.id = 3
        mock_product.name = "Nikon Z6II"
        mock_product.description = "Mirrorless camera"
        mock_product.price.amount = Decimal("48000000")
        mock_product.price.currency = "VND"
        mock_product.category_id = 1
        mock_product.brand_id = 3
        mock_product.image_url = None
        mock_product.stock_quantity = 8
        mock_product.is_hidden = False
        product_repository.find_by_id.return_value = mock_product
        
        input_data = GetProductDetailInputData(product_id=3)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.image_url is None
    
    def test_get_product_detail_with_long_description(self, use_case, product_repository):
        """Test 4: Sản phẩm có mô tả dài"""
        # Arrange
        long_description = "Máy ảnh Canon EOS R5 là dòng máy ảnh mirrorless full-frame hàng đầu " * 10
        mock_product = Mock()
        mock_product.id = 4
        mock_product.name = "Canon EOS R5"
        mock_product.description = long_description
        mock_product.price.amount = Decimal("89000000")
        mock_product.price.currency = "VND"
        mock_product.category_id = 1
        mock_product.brand_id = 1
        mock_product.image_url = "/images/canon-eos-r5.jpg"
        mock_product.stock_quantity = 10
        mock_product.is_hidden = False
        product_repository.find_by_id.return_value = mock_product
        
        input_data = GetProductDetailInputData(product_id=4)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.description) > 100
    
    # ============ HIDDEN PRODUCTS ============
    
    def test_get_product_detail_hidden_product(self, use_case, product_repository, category_repository, brand_repository):
        """Test 5: Lấy chi tiết sản phẩm hidden (vẫn trả về nếu truy cập trực tiếp)"""
        # Arrange
        mock_product = Mock()
        mock_product.product_id = 5
        mock_product.name = "Hidden Product"
        mock_product.description = "This product is hidden"
        mock_product.price = Mock()
        mock_product.price.amount = Decimal("50000000")
        mock_product.price.currency = "VND"
        mock_product.category_id = 1
        mock_product.brand_id = 1
        mock_product.image_url = "/images/hidden.jpg"
        mock_product.stock_quantity = 0
        mock_product.is_visible = False  # is_visible=False means hidden
        mock_product.is_available_for_purchase = Mock(return_value=False)
        product_repository.find_by_id.return_value = mock_product
        
        category_repository.find_by_id.return_value = Mock(name="Camera")
        brand_repository.find_by_id.return_value = Mock(name="Canon")
        
        input_data = GetProductDetailInputData(product_id=5)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.is_visible is False  # is_visible, not is_hidden
        assert output.is_available is False
    
    # ============ STOCK QUANTITY ============
    
    def test_get_product_detail_out_of_stock(self, use_case, product_repository):
        """Test 6: Sản phẩm hết hàng (stock = 0)"""
        # Arrange
        mock_product = Mock()
        mock_product.id = 6
        mock_product.name = "Out of Stock Product"
        mock_product.description = "This product is out of stock"
        mock_product.price.amount = Decimal("30000000")
        mock_product.price.currency = "VND"
        mock_product.category_id = 1
        mock_product.brand_id = 1
        mock_product.image_url = "/images/product.jpg"
        mock_product.stock_quantity = 0
        mock_product.is_hidden = False
        product_repository.find_by_id.return_value = mock_product
        
        input_data = GetProductDetailInputData(product_id=6)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.stock_quantity == 0
    
    def test_get_product_detail_low_stock(self, use_case, product_repository):
        """Test 7: Sản phẩm sắp hết hàng (stock < 5)"""
        # Arrange
        mock_product = Mock()
        mock_product.id = 7
        mock_product.name = "Low Stock Product"
        mock_product.description = "Only a few left"
        mock_product.price.amount = Decimal("40000000")
        mock_product.price.currency = "VND"
        mock_product.category_id = 1
        mock_product.brand_id = 1
        mock_product.image_url = "/images/product.jpg"
        mock_product.stock_quantity = 3
        mock_product.is_hidden = False
        product_repository.find_by_id.return_value = mock_product
        
        input_data = GetProductDetailInputData(product_id=7)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.stock_quantity == 3
    
    # ============ NOT FOUND CASES ============
    
    def test_get_product_detail_not_found(self, use_case, product_repository):
        """Test 8: Sản phẩm không tồn tại - trả về None từ repository"""
        # Arrange
        product_repository.find_by_id.return_value = None
        
        input_data = GetProductDetailInputData(product_id=999)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.error_message is not None
        # Error message should be string from ProductNotFoundException
        assert isinstance(output.error_message, str)
        assert "Product with ID" in str(output.error_message) or "not found" in str(output.error_message).lower()
        assert output.product_id is None
        assert output.name is None
    
    def test_get_product_detail_invalid_id_zero(self, use_case, product_repository):
        """Test 9: Product ID = 0"""
        # Arrange
        product_repository.find_by_id.return_value = None
        
        input_data = GetProductDetailInputData(product_id=0)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.error_message is not None
    
    def test_get_product_detail_invalid_id_negative(self, use_case, product_repository):
        """Test 10: Product ID âm"""
        # Arrange
        product_repository.find_by_id.return_value = None
        
        input_data = GetProductDetailInputData(product_id=-1)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
    
    # ============ REPOSITORY INTERACTION ============
    
    def test_get_product_detail_repository_called_with_correct_id(self, use_case, product_repository):
        """Test 11: Repository được gọi với đúng ID"""
        # Arrange
        mock_product = Mock()
        mock_product.id = 11
        mock_product.name = "Test Product"
        mock_product.description = "Test"
        mock_product.price.amount = Decimal("10000000")
        mock_product.price.currency = "VND"
        mock_product.category_id = 1
        mock_product.brand_id = 1
        mock_product.image_url = "/images/test.jpg"
        mock_product.stock_quantity = 10
        mock_product.is_hidden = False
        product_repository.find_by_id.return_value = mock_product
        
        input_data = GetProductDetailInputData(product_id=11)
        
        # Act
        use_case.execute(input_data)
        
        # Assert
        product_repository.find_by_id.assert_called_once_with(11)
    
    def test_get_product_detail_repository_exception(self, use_case, product_repository):
        """Test 12: Lỗi từ repository"""
        # Arrange
        product_repository.find_by_id.side_effect = Exception("Database error")
        
        input_data = GetProductDetailInputData(product_id=1)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.error_message is not None
    
    # ============ PRICE VALIDATION ============
    
    def test_get_product_detail_price_decimal_format(self, use_case, product_repository, category_repository, brand_repository):
        """Test 13: Giá sản phẩm được convert sang float"""
        # Arrange
        mock_product = Mock()
        mock_product.product_id = 13
        mock_product.name = "Price Test"
        mock_product.description = "Test decimal price"
        mock_product.price = Mock()
        mock_product.price.amount = Decimal("89000000.50")
        mock_product.price.currency = "VND"
        mock_product.category_id = 1
        mock_product.brand_id = 1
        mock_product.image_url = "/images/test.jpg"
        mock_product.stock_quantity = 10
        mock_product.is_visible = True
        mock_product.is_available_for_purchase = Mock(return_value=True)
        product_repository.find_by_id.return_value = mock_product
        
        category_repository.find_by_id.return_value = Mock(name="Camera")
        brand_repository.find_by_id.return_value = Mock(name="Canon")
        
        input_data = GetProductDetailInputData(product_id=13)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert isinstance(output.price, float)  # price is converted to float
        assert output.price == 89000000.50
    
    def test_get_product_detail_currency_vnd(self, use_case, product_repository):
        """Test 14: Currency là VND"""
        # Arrange
        mock_product = Mock()
        mock_product.id = 14
        mock_product.name = "Currency Test"
        mock_product.description = "Test currency"
        mock_product.price.amount = Decimal("50000000")
        mock_product.price.currency = "VND"
        mock_product.category_id = 1
        mock_product.brand_id = 1
        mock_product.image_url = "/images/test.jpg"
        mock_product.stock_quantity = 10
        mock_product.is_hidden = False
        product_repository.find_by_id.return_value = mock_product
        
        input_data = GetProductDetailInputData(product_id=14)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.currency == "VND"
    
    # ============ OUTPUT VALIDATION ============
    
    def test_get_product_detail_output_data_structure(self, use_case, product_repository, category_repository, brand_repository):
        """Test 15: Kiểm tra cấu trúc output data"""
        # Arrange
        mock_product = Mock()
        mock_product.product_id = 15
        mock_product.name = "Structure Test"
        mock_product.description = "Test structure"
        mock_product.price = Mock()
        mock_product.price.amount = Decimal("60000000")
        mock_product.price.currency = "VND"
        mock_product.category_id = 1
        mock_product.brand_id = 1
        mock_product.image_url = "/images/test.jpg"
        mock_product.stock_quantity = 10
        mock_product.is_visible = True
        mock_product.is_available_for_purchase = Mock(return_value=True)
        product_repository.find_by_id.return_value = mock_product
        
        category_repository.find_by_id.return_value = Mock(name="Camera")
        brand_repository.find_by_id.return_value = Mock(name="Canon")
        
        input_data = GetProductDetailInputData(product_id=15)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert isinstance(output, GetProductDetailOutputData)
        assert hasattr(output, 'success')
        assert hasattr(output, 'product_id')
        assert hasattr(output, 'name')
        assert hasattr(output, 'description')
        assert hasattr(output, 'price')
        assert hasattr(output, 'currency')
        assert hasattr(output, 'category_id')
        assert hasattr(output, 'category_name')
        assert hasattr(output, 'brand_id')
        assert hasattr(output, 'brand_name')
        assert hasattr(output, 'image_url')
        assert hasattr(output, 'stock_quantity')
        assert hasattr(output, 'is_visible')  # is_visible, not is_hidden
        assert hasattr(output, 'is_available')
        assert hasattr(output, 'error_message')
    
    def test_get_product_detail_success_no_error_message(self, use_case, product_repository):
        """Test 16: Success case không có error message"""
        # Arrange
        mock_product = Mock()
        mock_product.id = 16
        mock_product.name = "Success Test"
        mock_product.description = "Test success"
        mock_product.price.amount = Decimal("70000000")
        mock_product.price.currency = "VND"
        mock_product.category_id = 1
        mock_product.brand_id = 1
        mock_product.image_url = "/images/test.jpg"
        mock_product.stock_quantity = 10
        mock_product.is_hidden = False
        product_repository.find_by_id.return_value = mock_product
        
        input_data = GetProductDetailInputData(product_id=16)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.error_message is None
    
    def test_get_product_detail_failure_has_error_message(self, use_case, product_repository):
        """Test 17: Khi failure, phải có error message"""
        # Arrange
        product_repository.find_by_id.return_value = None
        
        input_data = GetProductDetailInputData(product_id=999)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.error_message is not None
        # Error message should be string
        assert isinstance(output.error_message, str)
        assert len(output.error_message) > 0
    
    # ============ EDGE CASES ============
    
    def test_get_product_detail_unicode_name(self, use_case, product_repository):
        """Test 18: Tên sản phẩm có ký tự Unicode (tiếng Việt)"""
        # Arrange
        mock_product = Mock()
        mock_product.id = 18
        mock_product.name = "Máy Ảnh Canon EOS R5 - Chính Hãng"
        mock_product.description = "Máy ảnh mirrorless full-frame với độ phân giải cao"
        mock_product.price.amount = Decimal("89000000")
        mock_product.price.currency = "VND"
        mock_product.category_id = 1
        mock_product.brand_id = 1
        mock_product.image_url = "/images/canon-eos-r5.jpg"
        mock_product.stock_quantity = 10
        mock_product.is_hidden = False
        product_repository.find_by_id.return_value = mock_product
        
        input_data = GetProductDetailInputData(product_id=18)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert "Máy Ảnh" in output.name
        assert "độ phân giải" in output.description
    
    def test_get_product_detail_special_characters_in_description(self, use_case, product_repository):
        """Test 19: Mô tả có ký tự đặc biệt"""
        # Arrange
        mock_product = Mock()
        mock_product.id = 19
        mock_product.name = "Special Product"
        mock_product.description = "Product with specs: 45MP, ISO 100-51200, 20fps (RAW+JPEG), 8K@30fps"
        mock_product.price.amount = Decimal("80000000")
        mock_product.price.currency = "VND"
        mock_product.category_id = 1
        mock_product.brand_id = 1
        mock_product.image_url = "/images/special.jpg"
        mock_product.stock_quantity = 10
        mock_product.is_hidden = False
        product_repository.find_by_id.return_value = mock_product
        
        input_data = GetProductDetailInputData(product_id=19)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert "@" in output.description
        assert "(" in output.description
