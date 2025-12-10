"""
UpdateUserByAdminUseCase - USE CASE 4
Admin can update user information with business rules

Business Rules:
- Only admin can update users
- Cannot self-deactivate
- Cannot self-demote from ADMIN
- Username/email must be unique (if changed)
- Validate all fields like Create
- Can change role (ADMIN ↔ CUSTOMER)
- Can activate/deactivate users
- Cannot update password (separate use case)

Clean Architecture:
- Layer 2: Business Logic (Use Case)
- Dependencies: Domain entities, Repository interface (Port)
- NO infrastructure dependencies
"""
from dataclasses import dataclass
from typing import Optional
import re

from ..ports import IUserRepository
from ...domain.entities import User
from ...domain.value_objects import Email, PhoneNumber
from ...domain.enums import UserRole
from ...domain.exceptions import UserNotFoundException, UserAlreadyExistsException


# ============================================================================
# INPUT DTO
# ============================================================================

@dataclass
class UpdateUserInputData:
    """
    Input data for updating user by admin
    
    Required fields:
    - user_id: ID of user to update
    - admin_user_id: ID of admin performing the action
    
    Optional fields (only provided fields will be updated):
    - username: New username
    - email: New email
    - full_name: New full name
    - phone_number: New phone number (or empty string to clear)
    - address: New address (or empty string to clear)
    - role: New role (ADMIN or CUSTOMER)
    - is_active: New active status
    """
    user_id: int
    admin_user_id: int
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    
    def __post_init__(self):
        """Validate input data"""
        # Validate user_id
        if not isinstance(self.user_id, int) or self.user_id <= 0:
            raise ValueError("user_id must be positive integer")
        
        if not isinstance(self.admin_user_id, int) or self.admin_user_id <= 0:
            raise ValueError("admin_user_id must be positive integer")
        
        # Track if phone/address were explicitly set (for clearing logic)
        self._phone_provided = self.phone_number is not None
        self._address_provided = self.address is not None
        self._address_value = self.address  # Store original for clearing
        
        # Validate username if provided
        if self.username is not None:
            self.username = self.username.strip()
            if len(self.username) < 3 or len(self.username) > 50:
                raise ValueError("Username must be 3-50 characters")
            
            # Username: alphanumeric + underscore only
            if not re.match(r'^[a-zA-Z0-9_]+$', self.username):
                raise ValueError("Username must contain only alphanumeric characters and underscores")
        
        # Validate email if provided
        if self.email is not None:
            self.email = Email(self.email.strip())
        
        # Validate full_name if provided
        if self.full_name is not None:
            self.full_name = self.full_name.strip()
            if len(self.full_name) < 2:
                raise ValueError("Full name must be at least 2 characters")
        
        # Validate phone_number if provided
        if self.phone_number is not None:
            self.phone_number = self.phone_number.strip()
            if self.phone_number:  # Non-empty string
                self.phone_number = PhoneNumber(self.phone_number)
            else:  # Empty string means clear phone
                self.phone_number = None
        
        # Validate address if provided
        if self.address is not None:
            self.address = self.address.strip()
            self._address_value = self.address
            # Keep empty string as is for update_profile (it handles clearing)
            # Don't convert to None here!
        
        # Validate role if provided
        if self.role is not None:
            self.role = self.role.strip().upper()
            if self.role not in ["ADMIN", "CUSTOMER"]:
                raise ValueError("Role must be ADMIN or CUSTOMER")
            self.role = UserRole[self.role]


# ============================================================================
# OUTPUT DTO
# ============================================================================

@dataclass
class UpdateUserOutputData:
    """
    Output data for update user operation
    
    Success response:
    - success: True
    - user_id: Updated user ID
    - username: Updated username
    - message: Success message
    
    Error response:
    - success: False
    - user_id: None
    - username: None
    - message: Error description
    
    Security: NEVER expose password_hash
    """
    success: bool
    user_id: Optional[int]
    username: Optional[str]
    message: str


# ============================================================================
# USE CASE INTERACTOR
# ============================================================================

class UpdateUserByAdminUseCase:
    """
    Use Case: Admin updates user information
    
    Business rules enforced:
    1. User must exist
    2. Cannot self-deactivate
    3. Cannot self-demote from ADMIN
    4. Username uniqueness (if changed)
    5. Email uniqueness (if changed)
    6. All field validations
    """
    
    def __init__(self, user_repository: IUserRepository):
        """
        Initialize use case with dependencies
        
        Args:
            user_repository: Repository interface for user data access
        """
        self._user_repository = user_repository
    
    def execute(self, input_data: UpdateUserInputData) -> UpdateUserOutputData:
        """
        Execute the update user use case
        
        Args:
            input_data: Validated input data
            
        Returns:
            UpdateUserOutputData with success/error information
        """
        try:
            # Step 1: Fetch the user to update
            user = self._user_repository.find_by_id(input_data.user_id)
            if not user:
                return UpdateUserOutputData(
                    success=False,
                    user_id=None,
                    username=None,
                    message=f"User with ID {input_data.user_id} not found"
                )
            
            # Step 2: Self-action protection checks
            is_self_action = (input_data.user_id == input_data.admin_user_id)
            
            # Check self-deactivation
            if is_self_action and input_data.is_active is not None and not input_data.is_active:
                return UpdateUserOutputData(
                    success=False,
                    user_id=None,
                    username=None,
                    message="Cannot deactivate yourself"
                )
            
            # Check self-demotion
            if is_self_action and input_data.role is not None:
                if user.is_admin() and input_data.role == UserRole.CUSTOMER:
                    return UpdateUserOutputData(
                        success=False,
                        user_id=None,
                        username=None,
                        message="Cannot change your own role"
                    )
            
            # Step 3: Update username if provided
            username_changed = False
            if input_data.username is not None:
                # Check if username changed
                if input_data.username != user.username:
                    # Check uniqueness
                    if self._user_repository.exists_by_username(input_data.username):
                        return UpdateUserOutputData(
                            success=False,
                            user_id=None,
                            username=None,
                            message=f"Username '{input_data.username}' already exists"
                        )
                    username_changed = True
                    # Update username (directly modify private field via reconstruction)
                    user = User.reconstruct(
                        user_id=user.id,
                        username=input_data.username,
                        email=user.email,
                        password_hash=user.password_hash,
                        full_name=user.full_name,
                        phone_number=user.phone_number,
                        address=user.address,
                        role=user.role,
                        is_active=user.is_active,
                        created_at=user.created_at
                    )
            
            # Step 4: Update email if provided
            if input_data.email is not None:
                # Check if email changed
                if input_data.email.address != user.email.address:
                    # Check uniqueness
                    if self._user_repository.exists_by_email(input_data.email):
                        return UpdateUserOutputData(
                            success=False,
                            user_id=None,
                            username=None,
                            message=f"Email '{input_data.email.address}' already exists"
                        )
                    # Update email
                    user = User.reconstruct(
                        user_id=user.id,
                        username=user.username,
                        email=input_data.email,
                        password_hash=user.password_hash,
                        full_name=user.full_name,
                        phone_number=user.phone_number,
                        address=user.address,
                        role=user.role,
                        is_active=user.is_active,
                        created_at=user.created_at
                    )
            
            # Step 5: Update profile fields (full_name, phone, address)
            # Handle full_name update
            if input_data.full_name is not None:
                user.update_profile(full_name=input_data.full_name)
            
            # Handle phone_number - including clearing (empty string → None)
            if input_data._phone_provided:
                if input_data.phone_number is None:
                    # Clear phone by reconstructing user
                    user = User.reconstruct(
                        user_id=user.id,
                        username=user.username,
                        email=user.email,
                        password_hash=user.password_hash,
                        full_name=user.full_name,
                        phone_number=None,
                        address=user.address,
                        role=user.role,
                        is_active=user.is_active,
                        created_at=user.created_at
                    )
                else:
                    # Update phone
                    user.update_profile(phone_number=input_data.phone_number)
            
            # Handle address - including clearing (empty string → None)
            if input_data._address_provided:
                # Pass the address value (can be empty string for clearing)
                user.update_profile(address=input_data._address_value)
            
            # Step 6: Update role if provided
            if input_data.role is not None:
                current_role = user.role
                if input_data.role != current_role:
                    if input_data.role == UserRole.ADMIN:
                        user.promote_to_admin()
                    else:  # CUSTOMER
                        user.demote_to_customer()
            
            # Step 7: Update is_active if provided
            if input_data.is_active is not None:
                if input_data.is_active and not user.is_active:
                    user.activate()
                elif not input_data.is_active and user.is_active:
                    user.deactivate()
            
            # Step 8: Save updated user
            updated_user = self._user_repository.save(user)
            
            # Step 9: Return success
            return UpdateUserOutputData(
                success=True,
                user_id=updated_user.id,
                username=updated_user.username,
                message="User updated successfully"
            )
        
        except ValueError as e:
            # Validation errors from domain
            return UpdateUserOutputData(
                success=False,
                user_id=None,
                username=None,
                message=str(e)
            )
        
        except UserAlreadyExistsException as e:
            # Uniqueness constraint violation
            return UpdateUserOutputData(
                success=False,
                user_id=None,
                username=None,
                message=str(e)
            )
        
        except Exception as e:
            # Unexpected errors
            return UpdateUserOutputData(
                success=False,
                user_id=None,
                username=None,
                message=f"Failed to update user: {str(e)}"
            )
