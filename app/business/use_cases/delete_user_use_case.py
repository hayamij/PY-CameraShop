"""
DeleteUserUseCase - USE CASE 5
Admin can delete (soft delete) users

Business Rules:
- Only admin can delete users
- SOFT DELETE only (is_active=false), NO hard delete
- Cannot self-delete
- User must exist
- If already inactive, error (already deleted)
- Allow deletion regardless of orders/cart (optional check)

Clean Architecture:
- Layer 2: Business Logic (Use Case)
- Dependencies: Domain entities, Repository interface (Port)
- NO infrastructure dependencies
"""
from dataclasses import dataclass
from typing import Optional

from ..ports import IUserRepository
from ...domain.entities import User
from ...domain.exceptions import UserNotFoundException


# ============================================================================
# INPUT DTO
# ============================================================================

@dataclass
class DeleteUserInputData:
    """
    Input data for deleting user by admin
    
    Required fields:
    - user_id: ID of user to delete
    - admin_user_id: ID of admin performing the action
    """
    user_id: int
    admin_user_id: int
    
    def __post_init__(self):
        """Validate input data"""
        if not isinstance(self.user_id, int) or self.user_id <= 0:
            raise ValueError("user_id must be positive integer")
        
        if not isinstance(self.admin_user_id, int) or self.admin_user_id <= 0:
            raise ValueError("admin_user_id must be positive integer")


# ============================================================================
# OUTPUT DTO
# ============================================================================

@dataclass
class DeleteUserOutputData:
    """
    Output data for delete user operation
    
    Success response:
    - success: True
    - user_id: Deleted user ID
    - message: Success message
    
    Error response:
    - success: False
    - user_id: None
    - message: Error description
    """
    success: bool
    user_id: Optional[int]
    message: str


# ============================================================================
# USE CASE INTERACTOR
# ============================================================================

class DeleteUserUseCase:
    """
    Use Case: Admin deletes (soft delete) user
    
    Business rules enforced:
    1. User must exist
    2. Cannot self-delete
    3. Cannot delete already inactive user
    4. Only soft delete (set is_active=false)
    5. Data is retained in database
    """
    
    def __init__(self, user_repository: IUserRepository):
        """
        Initialize use case with dependencies
        
        Args:
            user_repository: Repository interface for user data access
        """
        self._user_repository = user_repository
    
    def execute(self, input_data: DeleteUserInputData) -> DeleteUserOutputData:
        """
        Execute the delete user use case
        
        Args:
            input_data: Validated input data
            
        Returns:
            DeleteUserOutputData with success/error information
        """
        try:
            # Step 1: Fetch the user to delete
            user = self._user_repository.find_by_id(input_data.user_id)
            if not user:
                return DeleteUserOutputData(
                    success=False,
                    user_id=None,
                    message=f"User with ID {input_data.user_id} not found"
                )
            
            # Step 2: Self-deletion protection
            if input_data.user_id == input_data.admin_user_id:
                return DeleteUserOutputData(
                    success=False,
                    user_id=None,
                    message="Cannot delete yourself"
                )
            
            # Step 3: Check if already inactive (already deleted)
            if not user.is_active:
                return DeleteUserOutputData(
                    success=False,
                    user_id=None,
                    message="User is already inactive (already deleted)"
                )
            
            # Step 4: Soft delete - deactivate user
            user.deactivate()
            
            # Step 5: Save deactivated user
            self._user_repository.save(user)
            
            # Step 6: Return success
            return DeleteUserOutputData(
                success=True,
                user_id=user.id,
                message=f"User '{user.username}' deleted successfully (soft delete)"
            )
        
        except ValueError as e:
            # Domain validation errors
            return DeleteUserOutputData(
                success=False,
                user_id=None,
                message=str(e)
            )
        
        except Exception as e:
            # Unexpected errors
            return DeleteUserOutputData(
                success=False,
                user_id=None,
                message=f"Failed to delete user: {str(e)}"
            )
