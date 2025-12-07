# Unit Tests for Business Layer Use Cases

## Overview
Comprehensive unit tests cho các use cases trong Business Layer, theo nguyên tắc Clean Architecture.

## Test Coverage

### ✅ RegisterUserUseCase (5 tests)
- ✅ `test_register_user_success` - Đăng ký user thành công
- ✅ `test_register_user_invalid_email` - Email không hợp lệ
- ✅ `test_register_user_with_phone` - Đăng ký với số điện thoại
- ✅ `test_register_user_invalid_phone` - Số điện thoại không hợp lệ
- ✅ `test_register_user_duplicate` - User đã tồn tại

### ✅ LoginUserUseCase (4 tests)
- ✅ `test_login_with_username_success` - Đăng nhập bằng username
- ✅ `test_login_with_email_success` - Đăng nhập bằng email
- ✅ `test_login_user_not_found` - User không tồn tại
- ✅ `test_login_inactive_user` - User bị deactivate

### ✅ GetUserUseCase (2 tests)
- ✅ `test_get_user_success` - Lấy thông tin user thành công
- ✅ `test_get_user_not_found` - User không tồn tại

### ✅ ListProductsUseCase (5 tests)
- ✅ `test_list_all_products` - Liệt kê tất cả products
- ✅ `test_list_by_category` - Lọc theo category
- ✅ `test_list_by_brand` - Lọc theo brand
- ✅ `test_search_products` - Tìm kiếm products
- ✅ `test_list_empty_result` - Không có products

### ✅ GetProductDetailUseCase (3 tests)
- ✅ `test_get_product_success` - Lấy chi tiết product thành công
- ✅ `test_get_product_not_found` - Product không tồn tại
- ✅ `test_get_product_invalid_id` - Product ID không hợp lệ

## Test Statistics
- **Total Tests**: 19
- **Passed**: 19 (100%)
- **Failed**: 0
- **Coverage**: 5 use cases đầu tiên

## Testing Approach

### Mocking Strategy
- Sử dụng `unittest.mock.Mock` để tạo mock objects
- Tránh tạo thực entities để tránh các vấn đề về readonly properties
- Mock repositories để isolate business logic testing

### Test Structure
```python
class TestUseCaseName:
    @pytest.fixture
    def repository_mock(self):
        return Mock()
    
    @pytest.fixture
    def use_case(self, repository_mock):
        return UseCase(repository_mock)
    
    def test_scenario_name(self, use_case, repository_mock):
        # Arrange
        # Act
        # Assert
```

### Assertions
- Kiểm tra `output.success` status
- Kiểm tra `output.error_message` khi có lỗi
- Verify repository method calls với `assert_called_once()`
- Kiểm tra output data structure

## Running Tests

### Run all use case tests
```bash
python -m pytest tests/business/use_cases/ -v
```

### Run specific test class
```bash
python -m pytest tests/business/use_cases/test_all_use_cases.py::TestRegisterUserUseCase -v
```

### Run with coverage
```bash
python -m pytest tests/business/use_cases/ --cov=app.business.use_cases --cov-report=html
```

### Run with detailed output
```bash
python -m pytest tests/business/use_cases/ -v --tb=short
```

## Test Principles

### Clean Architecture Compliance
- ✅ Tests chỉ phụ thuộc vào Business Layer
- ✅ Mock repositories thay vì infrastructure
- ✅ Không test framework-specific code
- ✅ Focus on business logic validation

### Test Isolation
- Mỗi test độc lập, không phụ thuộc lẫn nhau
- Sử dụng fixtures để setup clean state
- Mock tất cả dependencies

### Comprehensive Coverage
- Test happy path (success scenarios)
- Test error cases (validation failures)
- Test edge cases (empty results, invalid inputs)
- Test business rule violations

## Future Work
- [ ] Tests cho các use cases còn lại (AddToCart, PlaceOrder, etc.)
- [ ] Integration tests với database thực
- [ ] Performance tests cho pagination
- [ ] Tests cho các edge cases phức tạp hơn

## Dependencies
- `pytest>=7.4.3` - Testing framework
- `pytest-flask>=1.3.0` - Flask extensions for pytest
- `werkzeug` - Password hashing utilities
