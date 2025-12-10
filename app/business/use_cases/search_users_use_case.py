"""
SearchUsersUseCase - Admin User Management (USE CASE 2)

Business Logic:
- Admin searches for users by query string
- Searches in: username, email, full_name
- Case-insensitive, partial match
- Minimum 2 characters required
- Returns max 50 results (performance limit)
- NEVER exposes password_hash

Clean Architecture:
- Layer 2: Business Logic (Use Case)
- Dependencies: IUserRepository (Port)
- No framework dependencies
"""
from typing import List
from dataclasses import dataclass

from ...business.ports.user_repository import IUserRepository
from ...domain.entities import User


@dataclass
class SearchUsersInputData:
    """
    Input DTO for SearchUsers use case
    
    Validation:
    - search_query: minimum 2 characters, not empty
    """
    search_query: str
    
    def __post_init__(self):
        """Validate input data"""
        # Strip whitespace
        self.search_query = self.search_query.strip() if self.search_query else ""
        
        # Validate not empty
        if not self.search_query:
            raise ValueError("Search query cannot be empty")
        
        # Validate minimum length
        if len(self.search_query) < 2:
            raise ValueError("Search query must be at least 2 characters")


@dataclass
class UserSearchResultData:
    """
    Individual user result DTO
    
    CRITICAL: NO password_hash field!
    """
    user_id: int
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    phone_number: str = None
    address: str = None


@dataclass
class SearchUsersOutputData:
    """
    Output DTO for SearchUsers use case
    
    Fields:
    - success: Operation status
    - results: List of matching users
    - total_results: Count of results
    - search_query: Original query (for display)
    - error_message: Error details if failed
    """
    success: bool
    results: List[UserSearchResultData]
    total_results: int
    search_query: str
    error_message: str = None


class SearchUsersUseCase:
    """
    Use Case: Admin searches for users
    
    Business Rules:
    1. Only admin can search (enforced at adapter layer)
    2. Query must be >= 2 characters
    3. Search in username, email, full_name (case-insensitive)
    4. Partial match supported
    5. Limit 50 results (performance)
    6. Never expose password_hash
    
    Flow:
    1. Validate input (minimum 2 chars)
    2. Call repository.search_by_query(query, limit=50)
    3. Convert domain entities to DTOs
    4. Return results
    """
    
    def __init__(self, user_repository: IUserRepository):
        """
        Initialize use case with dependencies
        
        Args:
            user_repository: Repository interface (Port)
        """
        self._user_repository = user_repository
    
    def execute(self, input_data: SearchUsersInputData) -> SearchUsersOutputData:
        """
        Execute search users use case
        
        Args:
            input_data: Validated input data
        
        Returns:
            SearchUsersOutputData with results or error
        """
        try:
            # Step 1: Query is already validated in InputData.__post_init__
            search_query = input_data.search_query
            
            # Step 2: Search via repository (limit 50 for performance)
            users = self._user_repository.search_by_query(
                query=search_query,
                limit=50
            )
            
            # Step 3: Convert domain entities to output DTOs
            result_dtos = self._convert_to_result_dtos(users)
            
            # Step 4: Return success output
            return SearchUsersOutputData(
                success=True,
                results=result_dtos,
                total_results=len(result_dtos),
                search_query=search_query
            )
        
        except Exception as e:
            # Handle any repository or unexpected errors
            return SearchUsersOutputData(
                success=False,
                results=[],
                total_results=0,
                search_query=input_data.search_query,
                error_message=f"Error searching users: {str(e)}"
            )
    
    def _convert_to_result_dtos(self, users: List[User]) -> List[UserSearchResultData]:
        """
        Convert domain entities to output DTOs
        
        CRITICAL: NEVER expose password_hash!
        
        Args:
            users: List of User domain entities
        
        Returns:
            List of UserSearchResultData DTOs
        """
        result_dtos = []
        
        for user in users:
            # Extract and sanitize data
            phone_str = user.phone_number.number if user.phone_number else None
            email_str = user.email.address
            
            # Create DTO (NO password_hash!)
            result_dto = UserSearchResultData(
                user_id=user.id,
                username=user.username,
                email=email_str,
                full_name=user.full_name,
                role=user.role.value,
                is_active=user.is_active,
                phone_number=phone_str,
                address=user.address
            )
            
            result_dtos.append(result_dto)
        
        return result_dtos
