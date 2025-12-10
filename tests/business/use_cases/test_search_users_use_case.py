"""
Unit Tests for SearchUsersUseCase (Admin User Management - USE CASE 2)

Test Coverage: TC2.1 - TC2.16
Business Rules:
- Chỉ admin mới được search
- Search query minimum 2 characters
- Search trong: username, email, full_name
- Case-insensitive, partial match
- Limit 50 results (performance)
- NEVER expose password_hash
"""
import pytest
from unittest.mock import Mock
from app.business.use_cases.search_users_use_case import (
    SearchUsersUseCase,
    SearchUsersInputData,
    SearchUsersOutputData,
    UserSearchResultData
)
from app.domain.entities import User
from app.domain.enums import UserRole
from app.domain.value_objects import Email, PhoneNumber


class TestSearchUsersInputDataValidation:
    """Test Input DTO validation"""
    
    def test_input_with_valid_query(self):
        """TC2.1: Input với query hợp lệ (>= 2 chars)"""
        input_data = SearchUsersInputData(search_query="ab")
        
        assert input_data.search_query == "ab"
    
    def test_input_with_empty_query_raises_error(self):
        """TC2.3: Query rỗng - validation error"""
        with pytest.raises(ValueError, match="Search query cannot be empty"):
            SearchUsersInputData(search_query="")
    
    def test_input_with_query_less_than_2_chars_raises_error(self):
        """TC2.2: Query < 2 chars - validation error"""
        with pytest.raises(ValueError, match="Search query must be at least 2 characters"):
            SearchUsersInputData(search_query="a")
    
    def test_input_with_whitespace_only_raises_error(self):
        """TC2.3 variant: Query chỉ có khoảng trắng"""
        with pytest.raises(ValueError, match="Search query cannot be empty"):
            SearchUsersInputData(search_query="   ")


@pytest.fixture
def mock_user_repository():
    """Mock IUserRepository"""
    return Mock()


@pytest.fixture
def use_case(mock_user_repository):
    """SearchUsersUseCase instance"""
    return SearchUsersUseCase(user_repository=mock_user_repository)


@pytest.fixture
def sample_users():
    """Sample users for testing"""
    return [
        User.reconstruct(
            user_id=1,
            username="john_doe",
            email=Email("john@example.com"),
            password_hash="hashed_password_1",
            full_name="John Doe",
            phone_number=PhoneNumber("0912345678"),
            address="123 Street",
            role=UserRole.CUSTOMER,
            is_active=True,
            created_at=None
        ),
        User.reconstruct(
            user_id=2,
            username="jane_admin",
            email=Email("jane@admin.com"),
            password_hash="hashed_password_2",
            full_name="Jane Smith",
            phone_number=PhoneNumber("0923456789"),
            address="456 Avenue",
            role=UserRole.ADMIN,
            is_active=True,
            created_at=None
        ),
        User.reconstruct(
            user_id=3,
            username="JOHNDOE2",
            email=Email("johndoe2@test.com"),
            password_hash="hashed_password_3",
            full_name="John Doe Junior",
            phone_number=PhoneNumber("0934567890"),
            address=None,
            role=UserRole.CUSTOMER,
            is_active=True,
            created_at=None
        )
    ]


class TestSearchUsersUseCase:
    """Test SearchUsersUseCase business logic"""
    
    def test_search_with_valid_query_success(self, use_case, mock_user_repository, sample_users):
        """TC2.1: Search với query hợp lệ - success"""
        # Arrange
        mock_user_repository.search_by_query.return_value = sample_users[:2]
        
        input_data = SearchUsersInputData(search_query="john")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.results) == 2
        assert output.total_results == 2
        assert output.search_query == "john"
        mock_user_repository.search_by_query.assert_called_once_with(query="john", limit=50)
    
    def test_search_by_username_exact_match(self, use_case, mock_user_repository, sample_users):
        """TC2.4: Search by username exact match - found"""
        # Arrange
        mock_user_repository.search_by_query.return_value = [sample_users[0]]
        
        input_data = SearchUsersInputData(search_query="john_doe")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.results) == 1
        assert output.results[0].username == "john_doe"
    
    def test_search_by_username_partial_match(self, use_case, mock_user_repository, sample_users):
        """TC2.5: Search by username partial match - found"""
        # Arrange
        mock_user_repository.search_by_query.return_value = [sample_users[0], sample_users[2]]
        
        input_data = SearchUsersInputData(search_query="john")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.results) == 2
        # Verify both johns found
        usernames = [r.username for r in output.results]
        assert "john_doe" in usernames
        assert "JOHNDOE2" in usernames
    
    def test_search_by_email_exact_match(self, use_case, mock_user_repository, sample_users):
        """TC2.6: Search by email exact match - found"""
        # Arrange
        mock_user_repository.search_by_query.return_value = [sample_users[1]]
        
        input_data = SearchUsersInputData(search_query="jane@admin.com")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.results) == 1
        assert output.results[0].email == "jane@admin.com"
    
    def test_search_by_email_partial_match(self, use_case, mock_user_repository, sample_users):
        """TC2.7: Search by email partial match - found"""
        # Arrange
        mock_user_repository.search_by_query.return_value = [sample_users[0], sample_users[2]]
        
        input_data = SearchUsersInputData(search_query="john")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.results) == 2
    
    def test_search_by_full_name_partial_match(self, use_case, mock_user_repository, sample_users):
        """TC2.8: Search by full_name partial match - found"""
        # Arrange
        mock_user_repository.search_by_query.return_value = [sample_users[1]]
        
        input_data = SearchUsersInputData(search_query="Smith")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.results) == 1
        assert "Smith" in output.results[0].full_name
    
    def test_search_case_insensitive_uppercase_query(self, use_case, mock_user_repository, sample_users):
        """TC2.9: Case-insensitive search - UPPERCASE query"""
        # Arrange
        mock_user_repository.search_by_query.return_value = [sample_users[0]]
        
        input_data = SearchUsersInputData(search_query="JOHN")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.results) == 1
        # Query được normalized to lowercase
        mock_user_repository.search_by_query.assert_called_once_with(query="JOHN", limit=50)
    
    def test_search_case_insensitive_lowercase_query(self, use_case, mock_user_repository, sample_users):
        """TC2.10: Case-insensitive search - lowercase query"""
        # Arrange
        mock_user_repository.search_by_query.return_value = [sample_users[2]]
        
        input_data = SearchUsersInputData(search_query="johndoe2")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.results) == 1
    
    def test_search_no_results_empty_array(self, use_case, mock_user_repository):
        """TC2.11: Search không tìm thấy - empty array"""
        # Arrange
        mock_user_repository.search_by_query.return_value = []
        
        input_data = SearchUsersInputData(search_query="nonexistent")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.results) == 0
        assert output.total_results == 0
        assert output.search_query == "nonexistent"
    
    def test_search_with_special_characters_handled(self, use_case, mock_user_repository):
        """TC2.12: Search với special characters - handled safely"""
        # Arrange
        mock_user_repository.search_by_query.return_value = []
        
        # Special chars that might cause SQL injection
        input_data = SearchUsersInputData(search_query="john'; DROP TABLE users;--")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        # Verify query passed as-is to repository (sanitization happens there)
        mock_user_repository.search_by_query.assert_called_once()
    
    def test_search_returns_max_50_results(self, use_case, mock_user_repository):
        """TC2.13: Search returns max 50 results (performance limit)"""
        # Arrange
        # Simulate repository returning exactly 50 users
        many_users = []
        for i in range(50):
            many_users.append(
                User.reconstruct(
                    user_id=i,
                    username=f"user{i}",
                    email=Email(f"user{i}@test.com"),
                    password_hash="hashed",
                    full_name=f"User {i}",
                    phone_number=None,
                    address=None,
                    role=UserRole.CUSTOMER,
                    is_active=True,
                    created_at=None
                )
            )
        mock_user_repository.search_by_query.return_value = many_users
        
        input_data = SearchUsersInputData(search_query="user")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.results) == 50
        assert output.total_results == 50
        # Verify limit parameter
        mock_user_repository.search_by_query.assert_called_once_with(query="user", limit=50)
    
    def test_password_hash_never_exposed_in_results(self, use_case, mock_user_repository, sample_users):
        """TC2.14: Verify password_hash NEVER in results"""
        # Arrange
        mock_user_repository.search_by_query.return_value = sample_users
        
        input_data = SearchUsersInputData(search_query="john")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        for result in output.results:
            # Check DTO has no password_hash attribute
            assert not hasattr(result, 'password_hash')
            # Convert to dict and verify
            result_dict = {
                'user_id': result.user_id,
                'username': result.username,
                'email': result.email,
                'full_name': result.full_name,
                'role': result.role,
                'is_active': result.is_active
            }
            assert 'password_hash' not in result_dict
    
    def test_search_multiple_words_in_full_name(self, use_case, mock_user_repository, sample_users):
        """TC2.15: Search multiple words in full_name"""
        # Arrange
        mock_user_repository.search_by_query.return_value = [sample_users[2]]
        
        input_data = SearchUsersInputData(search_query="Doe Junior")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.results) == 1
        assert "Junior" in output.results[0].full_name
    
    def test_repository_exception_handled_gracefully(self, use_case, mock_user_repository):
        """TC2.16: Repository exception - graceful error handling"""
        # Arrange
        mock_user_repository.search_by_query.side_effect = Exception("Database connection failed")
        
        input_data = SearchUsersInputData(search_query="john")
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert len(output.results) == 0
        assert output.total_results == 0
        assert "Error searching users" in output.error_message
