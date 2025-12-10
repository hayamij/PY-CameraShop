"""
USE CASE 6: CHANGE USER ROLE (Admin promote/demote user)

Business Layer - Use Case Interactor
Clean Architecture: Business Logic Layer

Input: user_id, new_role, admin_user_id
Output: success, user_id, old_role, new_role, message

Business Rules:
1. Only admin can change roles
2. Cannot self-change role (admin_user_id != user_id)
3. User must exist and be active
4. new_role must be ADMIN or CUSTOMER
5. If new_role == old_role, error (no change)
6. Promote: CUSTOMER → ADMIN (User.promote_to_admin())
7. Demote: ADMIN → CUSTOMER (User.demote_to_customer())
8. Optional: Last admin protection (cannot demote last admin)
"""
from dataclasses import dataclass
from typing import Optional

from app.business.ports.user_repository import IUserRepository
from app.domain.enums import UserRole


@dataclass
class ChangeUserRoleInputData:
    """Input data for changing user role"""
    user_id: int
    new_role: str
    admin_user_id: int
    
    def __post_init__(self):
        """Validate input data"""
        # Validate user_id
        if not isinstance(self.user_id, int) or self.user_id <= 0:
            raise ValueError("user_id must be a positive integer")
        
        # Validate admin_user_id
        if not isinstance(self.admin_user_id, int) or self.admin_user_id <= 0:
            raise ValueError("admin_user_id must be a positive integer")
        
        # Validate and normalize new_role
        if not isinstance(self.new_role, str):
            raise ValueError("new_role must be a string")
        
        self.new_role = self.new_role.strip().upper()
        
        if self.new_role not in ("ADMIN", "CUSTOMER"):
            raise ValueError("new_role must be 'ADMIN' or 'CUSTOMER'")


@dataclass
class ChangeUserRoleOutputData:
    """Output data for role change operation"""
    success: bool
    user_id: Optional[int]
    old_role: Optional[str]
    new_role: Optional[str]
    message: str


class ChangeUserRoleUseCase:
    """
    Use Case: Admin changes user role (promote/demote)
    
    Responsibilities:
    - Validate user exists and is active
    - Prevent self-role change
    - Prevent demoting last admin (optional)
    - Call domain methods: promote_to_admin() or demote_to_customer()
    - Save updated user
    """
    
    def __init__(self, user_repository: IUserRepository):
        """
        Initialize use case with dependencies
        
        Args:
            user_repository: Repository for user data access
        """
        self.user_repository = user_repository
    
    def execute(self, input_data: ChangeUserRoleInputData) -> ChangeUserRoleOutputData:
        """
        Execute role change operation
        
        Args:
            input_data: Input data with user_id, new_role, admin_user_id
        
        Returns:
            ChangeUserRoleOutputData with success status and details
        """
        try:
            # Business Rule 2: Cannot self-change role
            if input_data.user_id == input_data.admin_user_id:
                return ChangeUserRoleOutputData(
                    success=False,
                    user_id=None,
                    old_role=None,
                    new_role=None,
                    message="Cannot change your own role"
                )
            
            # Business Rule 3: User must exist
            user = self.user_repository.find_by_id(input_data.user_id)
            if user is None:
                return ChangeUserRoleOutputData(
                    success=False,
                    user_id=None,
                    old_role=None,
                    new_role=None,
                    message=f"User not found with ID: {input_data.user_id}"
                )
            
            # Business Rule 3: User must be active
            if not user.is_active:
                return ChangeUserRoleOutputData(
                    success=False,
                    user_id=None,
                    old_role=None,
                    new_role=None,
                    message="Cannot change role of inactive user"
                )
            
            # Get current role
            old_role_str = user.role.name
            new_role_enum = UserRole[input_data.new_role]
            
            # Business Rule 5: No change if roles are the same
            if user.role == new_role_enum:
                return ChangeUserRoleOutputData(
                    success=False,
                    user_id=None,
                    old_role=None,
                    new_role=None,
                    message=f"User already has role {input_data.new_role}"
                )
            
            # Business Rule 8: Last admin protection (optional)
            if user.role == UserRole.ADMIN and new_role_enum == UserRole.CUSTOMER:
                # Check if this is the last admin
                active_admin_count = self.user_repository.count_by_role(UserRole.ADMIN)
                if active_admin_count <= 1:
                    return ChangeUserRoleOutputData(
                        success=False,
                        user_id=None,
                        old_role=None,
                        new_role=None,
                        message="Cannot demote the last admin in the system"
                    )
            
            # Business Rule 6 & 7: Change role using domain methods
            if new_role_enum == UserRole.ADMIN:
                # Promote: CUSTOMER → ADMIN
                user.promote_to_admin()
                action = "promoted to ADMIN"
            else:
                # Demote: ADMIN → CUSTOMER
                user.demote_to_customer()
                action = "demoted to CUSTOMER"
            
            # Save updated user
            self.user_repository.save(user)
            
            return ChangeUserRoleOutputData(
                success=True,
                user_id=user.id,
                old_role=old_role_str,
                new_role=input_data.new_role,
                message=f"User {user.username} successfully {action}"
            )
            
        except ValueError as e:
            # Domain validation errors
            return ChangeUserRoleOutputData(
                success=False,
                user_id=None,
                old_role=None,
                new_role=None,
                message=str(e)
            )
        except Exception as e:
            # Unexpected errors
            return ChangeUserRoleOutputData(
                success=False,
                user_id=None,
                old_role=None,
                new_role=None,
                message=f"Error changing user role: {str(e)}"
            )
