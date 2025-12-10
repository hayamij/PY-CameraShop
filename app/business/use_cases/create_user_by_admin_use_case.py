"""
CreateUserByAdminUseCase - Admin User Management (USE CASE 3)

Business Logic:
- Admin creates new user with specified role
- Username must be unique (3-50 chars, alphanumeric + underscore)
- Email must be unique and valid
- Password hashed before saving (minimum 8 chars)
- Phone number optional but validated if provided
- New user is_active=true by default
- NEVER exposes password_hash in output

Clean Architecture:
- Layer 2: Business Logic (Use Case)
- Dependencies: IUserRepository (Port), PasswordHashingService (Infrastructure)
- No framework dependencies in business logic
"""
import re
from typing import Optional
from dataclasses import dataclass

from ...business.ports.user_repository import IUserRepository
from ...domain.entities import User
from ...domain.enums import UserRole
from ...domain.value_objects import Email, PhoneNumber
from ...domain.exceptions import UserAlreadyExistsException


@dataclass
class CreateUserInputData:
    """
    Input DTO for CreateUser use case
    
    Validation:
    - username: 3-50 chars, alphanumeric + underscore
    - email: valid format
    - password: minimum 8 chars
    - full_name: minimum 2 chars
    - phone_number: optional, Vietnamese format if provided
    - address: optional
    - role: ADMIN or CUSTOMER
    """
    username: str
    email: str
    password: str
    full_name: str
    role: str
    phone_number: Optional[str] = None
    address: Optional[str] = None
    
    def __post_init__(self):
        """Validate input data"""
        # Validate username
        self.username = self.username.strip() if self.username else ""
        if not self.username:
            raise ValueError("Username cannot be empty")
        if len(self.username) < 3 or len(self.username) > 50:
            raise ValueError("Username must be between 3 and 50 characters")
        if not re.match(r'^[a-zA-Z0-9_]+$', self.username):
            raise ValueError("Username can only contain letters, numbers, and underscores")
        
        # Validate email
        self.email = self.email.strip() if self.email else ""
        if not self.email:
            raise ValueError("Email cannot be empty")
        
        # Validate password
        if not self.password:
            raise ValueError("Password cannot be empty")
        if len(self.password) < 8:
            raise ValueError("Password must be at least 8 characters")
        
        # Validate full_name
        self.full_name = self.full_name.strip() if self.full_name else ""
        if not self.full_name:
            raise ValueError("Full name cannot be empty")
        if len(self.full_name) < 2:
            raise ValueError("Full name must be at least 2 characters")
        
        # Normalize phone_number (strip if provided)
        if self.phone_number:
            self.phone_number = self.phone_number.strip()
            if not self.phone_number:
                self.phone_number = None
        
        # Normalize address (strip if provided)
        if self.address:
            self.address = self.address.strip()
            if not self.address:
                self.address = None
        
        # Validate and normalize role
        self.role = self.role.strip().upper() if self.role else ""
        if not self.role:
            raise ValueError("Role cannot be empty")
        if self.role not in ["ADMIN", "CUSTOMER"]:
            raise ValueError("Role must be either ADMIN or CUSTOMER")


@dataclass
class CreateUserOutputData:
    """
    Output DTO for CreateUser use case
    
    CRITICAL: NO password_hash field!
    """
    success: bool
    user_id: Optional[int] = None
    username: Optional[str] = None
    message: str = None
    error_message: Optional[str] = None


class CreateUserByAdminUseCase:
    """
    Use Case: Admin creates a new user
    
    Business Rules:
    1. Only admin can create users (enforced at adapter layer)
    2. Username must be unique, 3-50 chars, alphanumeric + underscore
    3. Email must be unique and valid
    4. Password minimum 8 chars, hashed before save
    5. Full name minimum 2 chars
    6. Phone number optional, validated if provided
    7. Role: ADMIN or CUSTOMER
    8. New user is_active=true by default
    9. Never expose password_hash
    
    Flow:
    1. Validate input (username, email, password, etc.)
    2. Check username uniqueness
    3. Check email uniqueness
    4. Hash password (via PasswordHashingService)
    5. Create User entity (domain validation)
    6. Save to repository
    7. Return sanitized output
    """
    
    def __init__(self, user_repository: IUserRepository, password_service):
        """
        Initialize use case with dependencies
        
        Args:
            user_repository: Repository interface (Port)
            password_service: PasswordHashingService (Infrastructure)
        """
        self._user_repository = user_repository
        self._password_service = password_service
    
    def execute(self, input_data: CreateUserInputData) -> CreateUserOutputData:
        """
        Execute create user use case
        
        Args:
            input_data: Validated input data
        
        Returns:
            CreateUserOutputData with success/error
        """
        try:
            # Step 1: Input already validated in InputData.__post_init__
            
            # Step 2: Check username uniqueness
            if self._user_repository.exists_by_username(input_data.username):
                return CreateUserOutputData(
                    success=False,
                    error_message=f"Username '{input_data.username}' already exists"
                )
            
            # Step 3: Check email uniqueness (create Email value object first to validate format)
            try:
                email_vo = Email(input_data.email)
            except ValueError as e:
                return CreateUserOutputData(
                    success=False,
                    error_message=f"Invalid email format: {str(e)}"
                )
            
            if self._user_repository.exists_by_email(email_vo):
                return CreateUserOutputData(
                    success=False,
                    error_message=f"Email '{input_data.email}' already exists"
                )
            
            # Step 4: Hash password (Infrastructure layer concern)
            password_hash = self._password_service.hash_password(input_data.password)
            
            # Step 5: Create phone number value object if provided
            phone_vo = None
            if input_data.phone_number:
                try:
                    phone_vo = PhoneNumber(input_data.phone_number)
                except ValueError as e:
                    return CreateUserOutputData(
                        success=False,
                        error_message=f"Invalid phone number format: {str(e)}"
                    )
            
            # Step 6: Map role string to UserRole enum
            role_enum = UserRole.ADMIN if input_data.role == "ADMIN" else UserRole.CUSTOMER
            
            # Step 7: Create User entity (domain validation happens here)
            try:
                new_user = User(
                    username=input_data.username,
                    email=email_vo,
                    password_hash=password_hash,
                    full_name=input_data.full_name,
                    phone_number=phone_vo,
                    address=input_data.address,
                    role=role_enum
                )
            except ValueError as e:
                return CreateUserOutputData(
                    success=False,
                    error_message=f"Validation error: {str(e)}"
                )
            
            # Step 8: Save to repository
            saved_user = self._user_repository.save(new_user)
            
            # Step 9: Return success output (NO password_hash!)
            return CreateUserOutputData(
                success=True,
                user_id=saved_user.id,
                username=saved_user.username,
                message=f"User '{saved_user.username}' successfully created"
            )
        
        except UserAlreadyExistsException as e:
            return CreateUserOutputData(
                success=False,
                error_message=str(e)
            )
        except Exception as e:
            # Handle any unexpected errors
            return CreateUserOutputData(
                success=False,
                error_message=f"Error creating user: {str(e)}"
            )
