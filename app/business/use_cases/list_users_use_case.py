"""
List Users Use Case - Admin views all users with filters and pagination
Clean Architecture - Business Layer
NO framework dependencies!
"""
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime

from app.business.ports.user_repository import IUserRepository
from app.domain.entities.user import User
from app.domain.enums import UserRole
from app.domain.exceptions import ValidationException


@dataclass
class UserItemOutputData:
    """Single user data for output (NO password_hash!)"""
    user_id: int
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    phone_number: Optional[str]
    address: Optional[str]
    created_at: datetime


@dataclass
class ListUsersInputData:
    """Input data for listing users"""
    page: int = 1
    per_page: int = 20
    role_filter: Optional[str] = None  # 'ADMIN' or 'CUSTOMER'
    active_filter: Optional[bool] = None  # True, False, or None (all)
    search_query: Optional[str] = None  # Search in username, email, full_name
    sort_by: str = 'newest'  # newest, oldest, name_asc, name_desc


@dataclass
class ListUsersOutputData:
    """Output data for user listing"""
    success: bool
    users: List[UserItemOutputData]
    total_users: int
    total_pages: int
    current_page: int
    # Statistics
    total_admins: int = 0
    total_customers: int = 0
    active_users: int = 0
    inactive_users: int = 0
    error_message: Optional[str] = None


class ListUsersUseCase:
    """
    Use case for listing users with filters and pagination (Admin only)
    
    Business Rules:
    - Pagination with defaults (page=1, per_page=20)
    - Filter by role (ADMIN/CUSTOMER)
    - Filter by active status
    - Search by username, email, full_name (case-insensitive)
    - Sort: newest, oldest, name_asc, name_desc
    - NEVER expose password_hash
    - Calculate statistics: admins, customers, active, inactive
    """
    
    def __init__(self, user_repository: IUserRepository):
        """
        Initialize use case with repository dependency
        
        Args:
            user_repository: Repository for user data access
        """
        self.user_repository = user_repository
    
    def execute(self, input_data: ListUsersInputData) -> ListUsersOutputData:
        """
        Execute the list users use case
        
        Args:
            input_data: Input parameters for listing
            
        Returns:
            ListUsersOutputData with users and statistics
        """
        try:
            # Step 1: Validate and normalize input
            validated_input = self._validate_and_normalize_input(input_data)
            
            # Step 2: Build filters
            filters = self._build_filters(validated_input)
            
            # Step 3: Get users from repository
            users, total_count = self.user_repository.find_all_with_filters(
                filters=filters,
                page=validated_input.page,
                per_page=validated_input.per_page,
                sort_by=validated_input.sort_by
            )
            
            # Step 4: Convert to output DTOs (sanitize - NO password_hash!)
            user_items = self._convert_to_output_dtos(users)
            
            # Step 5: Calculate pagination
            total_pages = self._calculate_total_pages(total_count, validated_input.per_page)
            
            # Step 6: Calculate statistics
            statistics = self._calculate_statistics()
            
            return ListUsersOutputData(
                success=True,
                users=user_items,
                total_users=total_count,
                total_pages=total_pages,
                current_page=validated_input.page,
                total_admins=statistics['total_admins'],
                total_customers=statistics['total_customers'],
                active_users=statistics['active_users'],
                inactive_users=statistics['inactive_users']
            )
            
        except ValidationException as e:
            return ListUsersOutputData(
                success=False,
                users=[],
                total_users=0,
                total_pages=0,
                current_page=input_data.page,
                error_message=str(e)
            )
        except Exception as e:
            return ListUsersOutputData(
                success=False,
                users=[],
                total_users=0,
                total_pages=0,
                current_page=input_data.page,
                error_message=f"Error listing users: {str(e)}"
            )
    
    def _validate_and_normalize_input(self, input_data: ListUsersInputData) -> ListUsersInputData:
        """
        Validate and normalize input parameters
        
        Business Rules:
        - page < 1 → default to 1
        - per_page < 1 → default to 20
        - per_page > 100 → cap at 100
        - role_filter must be ADMIN or CUSTOMER (if provided)
        - sort_by must be valid option
        """
        # Normalize page
        page = input_data.page if input_data.page > 0 else 1
        
        # Normalize per_page
        per_page = input_data.per_page
        if per_page < 1:
            per_page = 20
        elif per_page > 100:
            per_page = 100
        
        # Validate role_filter
        if input_data.role_filter:
            role_upper = input_data.role_filter.upper()
            if role_upper not in ['ADMIN', 'CUSTOMER']:
                raise ValidationException(
                    f"Invalid role filter. Must be 'ADMIN' or 'CUSTOMER', got: {input_data.role_filter}"
                )
        
        # Validate sort_by
        valid_sort_options = ['newest', 'oldest', 'name_asc', 'name_desc']
        if input_data.sort_by not in valid_sort_options:
            raise ValidationException(
                f"Invalid sort option. Must be one of: {', '.join(valid_sort_options)}"
            )
        
        # Return normalized input
        return ListUsersInputData(
            page=page,
            per_page=per_page,
            role_filter=input_data.role_filter,
            active_filter=input_data.active_filter,
            search_query=input_data.search_query,
            sort_by=input_data.sort_by
        )
    
    def _build_filters(self, input_data: ListUsersInputData) -> dict:
        """Build filter dictionary from input data"""
        filters = {}
        
        if input_data.role_filter:
            filters['role'] = input_data.role_filter.upper()
        
        if input_data.active_filter is not None:
            filters['is_active'] = input_data.active_filter
        
        if input_data.search_query:
            filters['search_query'] = input_data.search_query.strip()
        
        return filters
    
    def _convert_to_output_dtos(self, users: List[User]) -> List[UserItemOutputData]:
        """
        Convert domain entities to output DTOs
        
        CRITICAL: NEVER expose password_hash!
        """
        user_items = []
        
        for user in users:
            # Sanitize phone_number - convert to string or None
            phone_str = user.phone_number.number if user.phone_number else None
            
            # Sanitize email - convert to string
            email_str = user.email.address
            
            user_item = UserItemOutputData(
                user_id=user.id,
                username=user.username,
                email=email_str,
                full_name=user.full_name,
                role=user.role.value,  # Convert enum to string
                is_active=user.is_active,
                phone_number=phone_str,
                address=user.address,
                created_at=user.created_at
            )
            user_items.append(user_item)
        
        return user_items
    
    def _calculate_total_pages(self, total_count: int, per_page: int) -> int:
        """Calculate total pages"""
        if total_count == 0:
            return 0
        return (total_count + per_page - 1) // per_page  # Ceiling division
    
    def _calculate_statistics(self) -> dict:
        """
        Calculate user statistics
        
        Returns:
            Dictionary with admin count, customer count, active/inactive counts
        """
        total_admins = self.user_repository.count_by_role('ADMIN')
        total_customers = self.user_repository.count_by_role('CUSTOMER')
        active_users = self.user_repository.count_active_users()
        total_users = total_admins + total_customers
        inactive_users = total_users - active_users
        
        return {
            'total_admins': total_admins,
            'total_customers': total_customers,
            'active_users': active_users,
            'inactive_users': inactive_users
        }
