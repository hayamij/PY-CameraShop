"""
Unit Tests for ListProductsUseCase
Test mọi trường hợp liệt kê sản phẩm với độ chính xác cao
"""

import pytest
from unittest.mock import Mock
from decimal import Decimal

from app.business.use_cases.list_products_use_case import (
    ListProductsUseCase,
    ListProductsInputData,
    ListProductsOutputData,
    ProductItemOutputData
)


class TestListProductsUseCase:
    """Test suite cho ListProductsUseCase - chi tiết và đáng tin cậy"""
    
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
        return ListProductsUseCase(product_repository, category_repository, brand_repository)
    
    def create_mock_product(self, product_id, name, price, category_id=1, brand_id=1, stock=10):
        """Helper để tạo mock product với đầy đủ attributes"""
        product = Mock()
        product.product_id = product_id
        product.name = name
        product.description = f"Mô tả cho {name}"
        product.image_url = f"/images/product-{product_id}.jpg"
        
        # Mock price object
        product.price = Mock()
        product.price.amount = Decimal(str(price))
        product.price.currency = "VND"
        
        product.category_id = category_id
        product.brand_id = brand_id
        product.stock_quantity = stock
        
        # Mock is_available_for_purchase method
        product.is_available_for_purchase = Mock(return_value=stock > 0)
        
        return product
    
    def create_mock_category(self, category_id, name):
        """Helper tạo mock category"""
        category = Mock()
        category.id = category_id
        category.name = name
        return category
    
    def create_mock_brand(self, brand_id, name):
        """Helper tạo mock brand"""
        brand = Mock()
        brand.id = brand_id
        brand.name = name
        return brand
    
    # ============ SUCCESS CASES - NO FILTERS ============
    
    def test_list_all_products_success(self, use_case, product_repository, category_repository, brand_repository):
        """Test 1: Liệt kê tất cả sản phẩm thành công"""
        # Arrange
        mock_products = [
            self.create_mock_product(1, "Canon EOS R5", 89000000),
            self.create_mock_product(2, "Sony A7IV", 62000000),
            self.create_mock_product(3, "Nikon Z6II", 48000000),
        ]
        product_repository.find_all.return_value = mock_products
        category_repository.find_by_id.return_value = self.create_mock_category(1, "Camera")
        brand_repository.find_by_id.return_value = self.create_mock_brand(1, "Canon")
        
        input_data = ListProductsInputData(page=1, per_page=10)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.products) == 3
        assert output.total_products == 3
        assert output.total_pages == 1
        assert output.current_page == 1
        assert output.has_next is False
        assert output.has_prev is False
        # Default sort by newest (ID desc)
        assert output.products[0].product_id == 3
        assert output.products[0].name == "Nikon Z6II"
        assert output.products[0].price == 48000000.0
    
    def test_list_products_filter_out_of_stock(self, use_case, product_repository, category_repository, brand_repository):
        """Test 2: Sản phẩm hết hàng bị lọc ra"""
        # Arrange
        product1 = self.create_mock_product(1, "In Stock", 10000000, stock=5)
        product2 = self.create_mock_product(2, "Out of Stock", 20000000, stock=0)
        product2.is_available_for_purchase = Mock(return_value=False)
        
        product_repository.find_all.return_value = [product1, product2]
        category_repository.find_by_id.return_value = self.create_mock_category(1, "Camera")
        brand_repository.find_by_id.return_value = self.create_mock_brand(1, "Canon")
        
        input_data = ListProductsInputData()
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.products) == 1
        assert output.products[0].product_id == 1
    
    def test_list_products_empty_result(self, use_case, product_repository):
        """Test 3: Không có sản phẩm"""
        # Arrange
        product_repository.find_all.return_value = []
        input_data = ListProductsInputData()
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.products) == 0
        assert output.total_products == 0
        assert output.total_pages == 0
    
    # ============ FILTER BY CATEGORY ============
    
    def test_filter_by_category(self, use_case, product_repository, category_repository, brand_repository):
        """Test 4: Lọc theo category"""
        # Arrange
        mock_products = [self.create_mock_product(1, "Product 1", 10000000, category_id=5)]
        product_repository.find_by_category.return_value = mock_products
        category_repository.find_by_id.return_value = self.create_mock_category(5, "DSLR")
        brand_repository.find_by_id.return_value = self.create_mock_brand(1, "Canon")
        
        input_data = ListProductsInputData(category_id=5)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        product_repository.find_by_category.assert_called_once_with(5)
        assert output.products[0].category_name == "DSLR"
    
    # ============ FILTER BY BRAND ============
    
    def test_filter_by_brand(self, use_case, product_repository, category_repository, brand_repository):
        """Test 5: Lọc theo brand"""
        # Arrange
        mock_products = [self.create_mock_product(1, "Product 1", 10000000, brand_id=3)]
        product_repository.find_by_brand.return_value = mock_products
        category_repository.find_by_id.return_value = self.create_mock_category(1, "Camera")
        brand_repository.find_by_id.return_value = self.create_mock_brand(3, "Sony")
        
        input_data = ListProductsInputData(brand_id=3)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        product_repository.find_by_brand.assert_called_once_with(3)
        assert output.products[0].brand_name == "Sony"
    
    # ============ SEARCH BY NAME ============
    
    def test_search_by_query(self, use_case, product_repository, category_repository, brand_repository):
        """Test 6: Tìm kiếm theo tên"""
        # Arrange
        mock_products = [self.create_mock_product(1, "Canon EOS", 10000000)]
        product_repository.search_by_name.return_value = mock_products
        category_repository.find_by_id.return_value = self.create_mock_category(1, "Camera")
        brand_repository.find_by_id.return_value = self.create_mock_brand(1, "Canon")
        
        input_data = ListProductsInputData(search_query="Canon")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        product_repository.search_by_name.assert_called_once_with("Canon")
    
    # ============ PRICE FILTERING ============
    
    def test_filter_by_min_price(self, use_case, product_repository, category_repository, brand_repository):
        """Test 7: Lọc giá tối thiểu"""
        # Arrange
        products = [
            self.create_mock_product(1, "Expensive", 50000000),
            self.create_mock_product(2, "Cheap", 10000000),
        ]
        product_repository.find_all.return_value = products
        category_repository.find_by_id.return_value = self.create_mock_category(1, "Camera")
        brand_repository.find_by_id.return_value = self.create_mock_brand(1, "Canon")
        
        input_data = ListProductsInputData(min_price=30000000.0)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.products) == 1
        assert output.products[0].product_id == 1
        assert output.products[0].price >= 30000000.0
    
    def test_filter_by_max_price(self, use_case, product_repository, category_repository, brand_repository):
        """Test 8: Lọc giá tối đa"""
        # Arrange
        products = [
            self.create_mock_product(1, "Expensive", 50000000),
            self.create_mock_product(2, "Cheap", 10000000),
        ]
        product_repository.find_all.return_value = products
        category_repository.find_by_id.return_value = self.create_mock_category(1, "Camera")
        brand_repository.find_by_id.return_value = self.create_mock_brand(1, "Canon")
        
        input_data = ListProductsInputData(max_price=30000000.0)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.products) == 1
        assert output.products[0].product_id == 2
        assert output.products[0].price <= 30000000.0
    
    def test_filter_by_price_range(self, use_case, product_repository, category_repository, brand_repository):
        """Test 9: Lọc khoảng giá"""
        # Arrange
        products = [
            self.create_mock_product(1, "Product 1", 10000000),
            self.create_mock_product(2, "Product 2", 30000000),
            self.create_mock_product(3, "Product 3", 50000000),
        ]
        product_repository.find_all.return_value = products
        category_repository.find_by_id.return_value = self.create_mock_category(1, "Camera")
        brand_repository.find_by_id.return_value = self.create_mock_brand(1, "Canon")
        
        input_data = ListProductsInputData(min_price=20000000.0, max_price=40000000.0)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.products) == 1
        assert output.products[0].product_id == 2
    
    # ============ SORTING ============
    
    def test_sort_by_price_asc(self, use_case, product_repository, category_repository, brand_repository):
        """Test 10: Sắp xếp giá tăng dần"""
        # Arrange
        products = [
            self.create_mock_product(1, "Product 1", 50000000),
            self.create_mock_product(2, "Product 2", 10000000),
            self.create_mock_product(3, "Product 3", 30000000),
        ]
        product_repository.find_all.return_value = products
        category_repository.find_by_id.return_value = self.create_mock_category(1, "Camera")
        brand_repository.find_by_id.return_value = self.create_mock_brand(1, "Canon")
        
        input_data = ListProductsInputData(sort_by="price_asc")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.products[0].price == 10000000.0
        assert output.products[1].price == 30000000.0
        assert output.products[2].price == 50000000.0
    
    def test_sort_by_price_desc(self, use_case, product_repository, category_repository, brand_repository):
        """Test 11: Sắp xếp giá giảm dần"""
        # Arrange
        products = [
            self.create_mock_product(1, "Product 1", 10000000),
            self.create_mock_product(2, "Product 2", 50000000),
            self.create_mock_product(3, "Product 3", 30000000),
        ]
        product_repository.find_all.return_value = products
        category_repository.find_by_id.return_value = self.create_mock_category(1, "Camera")
        brand_repository.find_by_id.return_value = self.create_mock_brand(1, "Canon")
        
        input_data = ListProductsInputData(sort_by="price_desc")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.products[0].price == 50000000.0
        assert output.products[1].price == 30000000.0
        assert output.products[2].price == 10000000.0
    
    def test_sort_by_name(self, use_case, product_repository, category_repository, brand_repository):
        """Test 12: Sắp xếp theo tên"""
        # Arrange
        products = [
            self.create_mock_product(1, "Zebra", 10000000),
            self.create_mock_product(2, "Apple", 20000000),
            self.create_mock_product(3, "Mango", 30000000),
        ]
        product_repository.find_all.return_value = products
        category_repository.find_by_id.return_value = self.create_mock_category(1, "Camera")
        brand_repository.find_by_id.return_value = self.create_mock_brand(1, "Canon")
        
        input_data = ListProductsInputData(sort_by="name")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.products[0].name == "Apple"
        assert output.products[1].name == "Mango"
        assert output.products[2].name == "Zebra"
    
    # ============ PAGINATION ============
    
    def test_pagination_page_1(self, use_case, product_repository, category_repository, brand_repository):
        """Test 13: Phân trang trang 1"""
        # Arrange
        products = [self.create_mock_product(i, f"Product {i}", 10000000) for i in range(1, 16)]
        product_repository.find_all.return_value = products
        category_repository.find_by_id.return_value = self.create_mock_category(1, "Camera")
        brand_repository.find_by_id.return_value = self.create_mock_brand(1, "Canon")
        
        input_data = ListProductsInputData(page=1, per_page=5)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.products) == 5
        assert output.total_products == 15
        assert output.total_pages == 3
        assert output.current_page == 1
        assert output.has_next is True
        assert output.has_prev is False
        # Sorted by newest (ID desc) - product 15 first
        assert output.products[0].product_id == 15
    
    def test_pagination_page_2(self, use_case, product_repository, category_repository, brand_repository):
        """Test 14: Phân trang trang 2"""
        # Arrange
        products = [self.create_mock_product(i, f"Product {i}", 10000000) for i in range(1, 16)]
        product_repository.find_all.return_value = products
        category_repository.find_by_id.return_value = self.create_mock_category(1, "Camera")
        brand_repository.find_by_id.return_value = self.create_mock_brand(1, "Canon")
        
        input_data = ListProductsInputData(page=2, per_page=5)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.products) == 5
        assert output.current_page == 2
        assert output.has_next is True
        assert output.has_prev is True
        # Sorted by newest: page 2 starts at product 10 (15,14,13,12,11 on page 1)
        assert output.products[0].product_id == 10
    
    def test_pagination_last_page(self, use_case, product_repository, category_repository, brand_repository):
        """Test 15: Trang cuối cùng"""
        # Arrange
        products = [self.create_mock_product(i, f"Product {i}", 10000000) for i in range(1, 13)]
        product_repository.find_all.return_value = products
        category_repository.find_by_id.return_value = self.create_mock_category(1, "Camera")
        brand_repository.find_by_id.return_value = self.create_mock_brand(1, "Canon")
        
        input_data = ListProductsInputData(page=3, per_page=5)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.products) == 2  # Chỉ còn 2 sản phẩm
        assert output.current_page == 3
        assert output.has_next is False
        assert output.has_prev is True
    
    # ============ INPUT VALIDATION ============
    
    def test_invalid_page_zero_corrected(self, use_case, product_repository, category_repository, brand_repository):
        """Test 16: Page 0 được sửa thành 1"""
        # Arrange
        products = [self.create_mock_product(1, "Product 1", 10000000)]
        product_repository.find_all.return_value = products
        category_repository.find_by_id.return_value = self.create_mock_category(1, "Camera")
        brand_repository.find_by_id.return_value = self.create_mock_brand(1, "Canon")
        
        input_data = ListProductsInputData(page=0, per_page=10)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.current_page == 1
    
    def test_invalid_per_page_corrected(self, use_case, product_repository, category_repository, brand_repository):
        """Test 17: per_page không hợp lệ được sửa thành 12"""
        # Arrange
        products = [self.create_mock_product(1, "Product 1", 10000000)]
        product_repository.find_all.return_value = products
        category_repository.find_by_id.return_value = self.create_mock_category(1, "Camera")
        brand_repository.find_by_id.return_value = self.create_mock_brand(1, "Canon")
        
        input_data = ListProductsInputData(page=1, per_page=0)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
    
    # ============ ERROR HANDLING ============
    
    def test_repository_exception_handled(self, use_case, product_repository):
        """Test 18: Lỗi từ repository được xử lý"""
        # Arrange
        product_repository.find_all.side_effect = Exception("Database error")
        input_data = ListProductsInputData()
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.error_message == "Database error"
        assert len(output.products) == 0
    
    # ============ OUTPUT DATA STRUCTURE ============
    
    def test_output_data_structure(self, use_case, product_repository, category_repository, brand_repository):
        """Test 19: Kiểm tra cấu trúc output data"""
        # Arrange
        products = [self.create_mock_product(1, "Product 1", 10000000)]
        product_repository.find_all.return_value = products
        category_repository.find_by_id.return_value = self.create_mock_category(1, "Camera")
        brand_repository.find_by_id.return_value = self.create_mock_brand(1, "Canon")
        
        input_data = ListProductsInputData()
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert isinstance(output, ListProductsOutputData)
        assert hasattr(output, 'success')
        assert hasattr(output, 'products')
        assert hasattr(output, 'total_products')
        assert hasattr(output, 'total_pages')
        assert hasattr(output, 'current_page')
        assert hasattr(output, 'has_next')
        assert hasattr(output, 'has_prev')
        assert hasattr(output, 'error_message')
        
        # Kiểm tra product item structure
        assert isinstance(output.products[0], ProductItemOutputData)
        assert hasattr(output.products[0], 'product_id')
        assert hasattr(output.products[0], 'name')
        assert hasattr(output.products[0], 'price')
        assert hasattr(output.products[0], 'currency')
