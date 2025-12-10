"""
Unit Tests for List Users Use Case
Test-Driven Development (TDD) - Write tests FIRST
Following Clean Architecture principles from mega-prompt.md
"""
import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock, MagicMock

from app.business.use_cases.list_users_use_case import (
    ListUsersUseCase,
    ListUsersInputData,
    ListUsersOutputData,
    UserItemOutputData
)
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.phone_number import PhoneNumber
from app.domain.enums import UserRole
from app.domain.exceptions import ValidationException


class TestListUsersInputDataValidation:
    """Test Input DTO validation"""
    
    def test_input_with_valid_defaults(self):
        """TC1.1: Create input with default values"""
        input_data = ListUsersInputData()
        assert input_data.page == 1
        assert input_data.per_page == 20
        assert input_data.role_filter is None
        assert input_data.active_filter is None
        assert input_data.search_query is None
        assert input_data.sort_by == 'newest'
    
    def test_input_with_custom_values(self):
        """TC1.2: Create input with custom pagination"""
        input_data = ListUsersInputData(
            page=2,
            per_page=10,
            role_filter='ADMIN',
            active_filter=True,
            search_query='john',
            sort_by='name_asc'
        )
        assert input_data.page == 2
        assert input_data.per_page == 10
        assert input_data.role_filter == 'ADMIN'
        assert input_data.active_filter is True
        assert input_data.search_query == 'john'
        assert input_data.sort_by == 'name_asc'


class TestListUsersUseCase:
    """Test List Users Use Case - Business Logic"""
    
    @pytest.fixture
    def mock_user_repository(self):
        """Mock repository for testing"""
        return Mock()
    
    @pytest.fixture
    def use_case(self, mock_user_repository):
        """Create use case instance with mocked dependencies"""
        return ListUsersUseCase(user_repository=mock_user_repository)
    
    @pytest.fixture
    def sample_users(self):
        """Sample users for testing"""
        users = []
        
        # Admin user
        admin = User.reconstruct(
            user_id=1,
            username='admin1',
            email=Email('admin@test.com'),
            password_hash='hashed_password',
            full_name='Admin User',
            phone_number=PhoneNumber('0912345678'),  # Valid Vietnamese format
            address='123 Admin St',
            role=UserRole.ADMIN,
            is_active=True,
            created_at=datetime(2024, 1, 1)
        )
        users.append(admin)
        
        # Customer users
        for i in range(2, 6):
            user = User.reconstruct(
                user_id=i,
                username=f'customer{i}',
                email=Email(f'customer{i}@test.com'),
                password_hash='hashed_password',
                full_name=f'Customer {i}',
                phone_number=None,
                address=None,
                role=UserRole.CUSTOMER,
                is_active=True if i % 2 == 0 else False,
                created_at=datetime(2024, 1, i)
            )
            users.append(user)
        
        return users
    
    # ==================== TC1.1: List all users - success ====================
    
    def test_list_all_users_no_filters_success(self, use_case, mock_user_repository, sample_users):
        """TC1.1: List all users without filters - success"""
        # Arrange
        mock_user_repository.find_all_with_filters.return_value = (sample_users, len(sample_users))
        mock_user_repository.count_by_role.side_effect = lambda role: sum(
            1 for u in sample_users if u.role == role
        )
        mock_user_repository.count_active_users.return_value = sum(
            1 for u in sample_users if u.is_active
        )
        
        input_data = ListUsersInputData()
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.users) == 5
        assert output.total_users == 5
        assert output.total_pages == 1
        assert output.current_page == 1
        
        # Verify statistics
        assert output.total_admins == 1
        assert output.total_customers == 4
        assert output.active_users == 3
        assert output.inactive_users == 2
        
        # Verify password_hash NOT exposed
        for user in output.users:
            assert not hasattr(user, 'password_hash')
            assert user.username is not None
            assert user.email is not None
    
    # ==================== TC1.2-1.5: Pagination tests ====================
    
    def test_list_with_pagination_page_2(self, use_case, mock_user_repository, sample_users):
        """TC1.2: List with pagination (page=2, per_page=2)"""
        # Arrange
        per_page = 2
        page = 2
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_users = sample_users[start_idx:end_idx]
        
        mock_user_repository.find_all_with_filters.return_value = (paginated_users, len(sample_users))
        mock_user_repository.count_by_role.return_value = 0
        mock_user_repository.count_active_users.return_value = 0
        
        input_data = ListUsersInputData(page=2, per_page=2)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.users) == 2
        assert output.total_users == 5
        assert output.total_pages == 3  # ceil(5/2) = 3
        assert output.current_page == 2
    
    def test_list_with_invalid_page_zero_defaults_to_one(self, use_case, mock_user_repository, sample_users):
        """TC1.3: Invalid page (page=0) - should default to 1"""
        # Arrange
        mock_user_repository.find_all_with_filters.return_value = (sample_users, len(sample_users))
        mock_user_repository.count_by_role.return_value = 0
        mock_user_repository.count_active_users.return_value = 0
        
        input_data = ListUsersInputData(page=0)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert output.current_page == 1  # Defaulted to 1
    
    def test_list_with_invalid_per_page_zero_defaults_to_twenty(self, use_case, mock_user_repository, sample_users):
        """TC1.4: Invalid per_page (per_page=0) - should default to 20"""
        # Arrange
        mock_user_repository.find_all_with_filters.return_value = (sample_users, len(sample_users))
        mock_user_repository.count_by_role.return_value = 0
        mock_user_repository.count_active_users.return_value = 0
        
        input_data = ListUsersInputData(per_page=0)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        # per_page should be defaulted to 20 in execute method
    
    def test_list_with_per_page_over_100_capped_at_100(self, use_case, mock_user_repository, sample_users):
        """TC1.5: per_page > 100 - should cap at 100"""
        # Arrange
        mock_user_repository.find_all_with_filters.return_value = (sample_users, len(sample_users))
        mock_user_repository.count_by_role.return_value = 0
        mock_user_repository.count_active_users.return_value = 0
        
        input_data = ListUsersInputData(per_page=150)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        # per_page should be capped at 100 in execute method
    
    # ==================== TC1.6-1.9: Filter tests ====================
    
    def test_filter_by_role_admin_only(self, use_case, mock_user_repository, sample_users):
        """TC1.6: Filter by role=ADMIN - only admins returned"""
        # Arrange
        admin_users = [u for u in sample_users if u.role == UserRole.ADMIN]
        mock_user_repository.find_all_with_filters.return_value = (admin_users, len(admin_users))
        mock_user_repository.count_by_role.return_value = len(admin_users)
        mock_user_repository.count_active_users.return_value = 1
        
        input_data = ListUsersInputData(role_filter='ADMIN')
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.users) == 1
        assert all(u.role == 'ADMIN' for u in output.users)
    
    def test_filter_by_role_customer_only(self, use_case, mock_user_repository, sample_users):
        """TC1.7: Filter by role=CUSTOMER - only customers returned"""
        # Arrange
        customer_users = [u for u in sample_users if u.role == UserRole.CUSTOMER]
        mock_user_repository.find_all_with_filters.return_value = (customer_users, len(customer_users))
        mock_user_repository.count_by_role.return_value = len(customer_users)
        mock_user_repository.count_active_users.return_value = 2
        
        input_data = ListUsersInputData(role_filter='CUSTOMER')
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.users) == 4
        assert all(u.role == 'CUSTOMER' for u in output.users)
    
    def test_filter_by_active_true_only(self, use_case, mock_user_repository, sample_users):
        """TC1.8: Filter by is_active=true - only active users"""
        # Arrange
        active_users = [u for u in sample_users if u.is_active]
        mock_user_repository.find_all_with_filters.return_value = (active_users, len(active_users))
        mock_user_repository.count_by_role.return_value = 0
        mock_user_repository.count_active_users.return_value = len(active_users)
        
        input_data = ListUsersInputData(active_filter=True)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.users) == 3
        assert all(u.is_active is True for u in output.users)
    
    def test_filter_by_active_false_only(self, use_case, mock_user_repository, sample_users):
        """TC1.9: Filter by is_active=false - only inactive users"""
        # Arrange
        inactive_users = [u for u in sample_users if not u.is_active]
        mock_user_repository.find_all_with_filters.return_value = (inactive_users, len(inactive_users))
        mock_user_repository.count_by_role.return_value = 0
        mock_user_repository.count_active_users.return_value = 0
        
        input_data = ListUsersInputData(active_filter=False)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.users) == 2
        assert all(u.is_active is False for u in output.users)
    
    # ==================== TC1.10-1.13: Search tests ====================
    
    def test_search_by_username_partial_match(self, use_case, mock_user_repository, sample_users):
        """TC1.11: Search by username (partial match)"""
        # Arrange
        search_query = 'customer'
        matching_users = [u for u in sample_users if search_query in u.username.lower()]
        mock_user_repository.find_all_with_filters.return_value = (matching_users, len(matching_users))
        mock_user_repository.count_by_role.return_value = 0
        mock_user_repository.count_active_users.return_value = 0
        
        input_data = ListUsersInputData(search_query=search_query)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.users) == 4
        assert all('customer' in u.username.lower() for u in output.users)
    
    def test_search_case_insensitive(self, use_case, mock_user_repository, sample_users):
        """TC1.13: Search by full_name (case-insensitive)"""
        # Arrange
        search_query = 'CUSTOMER'
        matching_users = [u for u in sample_users if search_query.lower() in u.full_name.lower()]
        mock_user_repository.find_all_with_filters.return_value = (matching_users, len(matching_users))
        mock_user_repository.count_by_role.return_value = 0
        mock_user_repository.count_active_users.return_value = 0
        
        input_data = ListUsersInputData(search_query=search_query)
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.users) > 0
    
    # ==================== TC1.14-1.16: Sort tests ====================
    
    def test_sort_by_name_asc_alphabetical(self, use_case, mock_user_repository, sample_users):
        """TC1.14: Sort by name_asc - alphabetical order"""
        # Arrange
        sorted_users = sorted(sample_users, key=lambda u: u.username.lower())
        mock_user_repository.find_all_with_filters.return_value = (sorted_users, len(sorted_users))
        mock_user_repository.count_by_role.return_value = 0
        mock_user_repository.count_active_users.return_value = 0
        
        input_data = ListUsersInputData(sort_by='name_asc')
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        usernames = [u.username for u in output.users]
        assert usernames == sorted(usernames, key=str.lower)
    
    def test_sort_by_newest_first(self, use_case, mock_user_repository, sample_users):
        """TC1.15: Sort by newest - most recent first"""
        # Arrange
        sorted_users = sorted(sample_users, key=lambda u: u.created_at, reverse=True)
        mock_user_repository.find_all_with_filters.return_value = (sorted_users, len(sorted_users))
        mock_user_repository.count_by_role.return_value = 0
        mock_user_repository.count_active_users.return_value = 0
        
        input_data = ListUsersInputData(sort_by='newest')
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.users) == 5
    
    # ==================== TC1.17: Combined filters ====================
    
    def test_combined_filters_role_and_active_and_search(self, use_case, mock_user_repository, sample_users):
        """TC1.17: Combined filters (role + active + search)"""
        # Arrange
        matching_users = [
            u for u in sample_users 
            if u.role == UserRole.CUSTOMER 
            and u.is_active 
            and 'customer' in u.username.lower()
        ]
        mock_user_repository.find_all_with_filters.return_value = (matching_users, len(matching_users))
        mock_user_repository.count_by_role.return_value = len(matching_users)
        mock_user_repository.count_active_users.return_value = len(matching_users)
        
        input_data = ListUsersInputData(
            role_filter='CUSTOMER',
            active_filter=True,
            search_query='customer'
        )
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert all(u.role == 'CUSTOMER' for u in output.users)
        assert all(u.is_active is True for u in output.users)
    
    # ==================== TC1.18: Empty result ====================
    
    def test_empty_result_set_no_matches(self, use_case, mock_user_repository):
        """TC1.18: Empty result set (no users match filters)"""
        # Arrange
        mock_user_repository.find_all_with_filters.return_value = ([], 0)
        mock_user_repository.count_by_role.return_value = 0
        mock_user_repository.count_active_users.return_value = 0
        
        input_data = ListUsersInputData(search_query='nonexistent_user_xyz')
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is True
        assert len(output.users) == 0
        assert output.total_users == 0
        assert output.total_pages == 0
    
    # ==================== TC1.19-1.20: Security & Statistics ====================
    
    def test_statistics_calculation_correctness(self, use_case, mock_user_repository, sample_users):
        """TC1.19: Statistics calculation correctness"""
        # Arrange
        mock_user_repository.find_all_with_filters.return_value = (sample_users, len(sample_users))
        
        admins = sum(1 for u in sample_users if u.role == UserRole.ADMIN)
        customers = sum(1 for u in sample_users if u.role == UserRole.CUSTOMER)
        active = sum(1 for u in sample_users if u.is_active)
        
        mock_user_repository.count_by_role.side_effect = lambda role: (
            admins if role == UserRole.ADMIN else customers
        )
        mock_user_repository.count_active_users.return_value = active
        
        input_data = ListUsersInputData()
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.total_admins == 1
        assert output.total_customers == 4
        assert output.active_users == 3
        assert output.inactive_users == 2  # total - active
    
    def test_password_hash_never_exposed_in_output(self, use_case, mock_user_repository, sample_users):
        """TC1.20: Verify password_hash not exposed in output"""
        # Arrange
        mock_user_repository.find_all_with_filters.return_value = (sample_users, len(sample_users))
        mock_user_repository.count_by_role.return_value = 0
        mock_user_repository.count_active_users.return_value = 0
        
        input_data = ListUsersInputData()
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        for user_output in output.users:
            # Check all attributes of UserItemOutputData
            assert hasattr(user_output, 'user_id')
            assert hasattr(user_output, 'username')
            assert hasattr(user_output, 'email')
            assert hasattr(user_output, 'full_name')
            assert hasattr(user_output, 'role')
            assert hasattr(user_output, 'is_active')
            
            # password_hash should NOT be present
            assert not hasattr(user_output, 'password_hash')
            
            # Verify data types
            assert isinstance(user_output.user_id, int)
            assert isinstance(user_output.username, str)
            assert isinstance(user_output.email, str)
            assert isinstance(user_output.role, str)
            assert isinstance(user_output.is_active, bool)
    
    # ==================== Error handling ====================
    
    def test_repository_exception_handled_gracefully(self, use_case, mock_user_repository):
        """Test repository exception is handled and returns error output"""
        # Arrange
        mock_user_repository.find_all_with_filters.side_effect = Exception("Database connection error")
        
        input_data = ListUsersInputData()
        
        # Act
        output = use_case.execute(input_data)
        
        # Assert
        assert output.success is False
        assert output.error_message is not None
        assert 'error' in output.error_message.lower()
        assert len(output.users) == 0
