"""
User Domain Entity - Rich model with business logic
NO framework dependencies!
"""
from datetime import datetime
from typing import Optional
from ..enums import UserRole
from ..value_objects import Email, PhoneNumber
from ..exceptions import InvalidCredentialsException, InsufficientPermissionsException


class User:
    """
    User domain entity with business rules
    
    Business Rules:
    - Email and username must be unique
    - Password must be hashed (never store plain text)
    - Role determines permissions
    - Users can be deactivated but not deleted
    """
    
    def __init__(
        self,
        username: str,
        email: Email,
        password_hash: str,
        full_name: str,
        phone_number: Optional[PhoneNumber] = None,
        address: Optional[str] = None,
        role: UserRole = UserRole.CUSTOMER
    ):
        """
        Create a new user (for registration)
        
        Args:
            username: Unique username
            email: Email value object
            password_hash: Hashed password (NOT plain text!)
            full_name: User's full name
            phone_number: Phone number value object
            address: User's address
            role: User role (default: CUSTOMER)
            
        Raises:
            ValueError: If any validation fails
        """
        if not username or len(username) < 3:
            raise ValueError("Username must be at least 3 characters")
        if not password_hash:
            raise ValueError("Password hash cannot be empty")
        if not full_name or len(full_name) < 2:
            raise ValueError("Full name must be at least 2 characters")
        
        self._id: Optional[int] = None  # Set by repository on save
        self._username = username.strip()
        self._email = email
        self._password_hash = password_hash
        self._full_name = full_name.strip()
        self._phone_number = phone_number
        self._address = address.strip() if address else None
        self._role = role
        self._is_active = True
        self._created_at = datetime.now()
    
    @staticmethod
    def reconstruct(
        user_id: int,
        username: str,
        email: Email,
        password_hash: str,
        full_name: str,
        phone_number: Optional[PhoneNumber],
        address: Optional[str],
        role: UserRole,
        is_active: bool,
        created_at: datetime
    ) -> 'User':
        """
        Reconstruct user from database (no validation)
        Used by repository when loading from database
        """
        user = object.__new__(User)
        user._id = user_id
        user._username = username
        user._email = email
        user._password_hash = password_hash
        user._full_name = full_name
        user._phone_number = phone_number
        user._address = address
        user._role = role
        user._is_active = is_active
        user._created_at = created_at
        return user
    
    # Getters
    @property
    def id(self) -> Optional[int]:
        return self._id
    
    @property
    def username(self) -> str:
        return self._username
    
    @property
    def email(self) -> Email:
        return self._email
    
    @property
    def password_hash(self) -> str:
        return self._password_hash
    
    @property
    def full_name(self) -> str:
        return self._full_name
    
    @property
    def phone_number(self) -> Optional[PhoneNumber]:
        return self._phone_number
    
    @property
    def address(self) -> Optional[str]:
        return self._address
    
    @property
    def role(self) -> UserRole:
        return self._role
    
    @property
    def is_active(self) -> bool:
        return self._is_active
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    # Business methods
    def update_profile(
        self,
        full_name: Optional[str] = None,
        phone_number: Optional[PhoneNumber] = None,
        address: Optional[str] = None
    ):
        """Update user profile information"""
        if full_name:
            if len(full_name) < 2:
                raise ValueError("Full name must be at least 2 characters")
            self._full_name = full_name.strip()
        
        if phone_number:
            self._phone_number = phone_number
        
        if address is not None:  # Allow empty string to clear address
            self._address = address.strip() if address else None
    
    def change_password(self, new_password_hash: str):
        """
        Change user password
        
        Args:
            new_password_hash: New hashed password
            
        Raises:
            ValueError: If password hash is empty
        """
        if not new_password_hash:
            raise ValueError("Password hash cannot be empty")
        self._password_hash = new_password_hash
    
    def deactivate(self):
        """Deactivate user account"""
        if not self._is_active:
            raise ValueError("User is already deactivated")
        self._is_active = False
    
    def activate(self):
        """Activate user account"""
        if self._is_active:
            raise ValueError("User is already active")
        self._is_active = True
    
    def promote_to_admin(self):
        """Promote user to admin role"""
        if self._role == UserRole.ADMIN:
            raise ValueError("User is already an admin")
        self._role = UserRole.ADMIN
    
    def demote_to_customer(self):
        """Demote user to customer role"""
        if self._role == UserRole.CUSTOMER:
            raise ValueError("User is already a customer")
        self._role = UserRole.CUSTOMER
    
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self._role == UserRole.ADMIN
    
    def is_customer(self) -> bool:
        """Check if user is customer"""
        return self._role == UserRole.CUSTOMER
    
    def can_access_admin_panel(self) -> bool:
        """Check if user can access admin panel"""
        return self.is_admin() and self._is_active
    
    def ensure_admin(self):
        """
        Ensure user is admin
        
        Raises:
            InsufficientPermissionsException: If user is not admin
        """
        if not self.is_admin():
            raise InsufficientPermissionsException("ADMIN")
    
    def ensure_active(self):
        """
        Ensure user is active
        
        Raises:
            InvalidCredentialsException: If user is not active
        """
        if not self._is_active:
            raise InvalidCredentialsException()
    
    def __eq__(self, other) -> bool:
        """Check equality based on ID"""
        if not isinstance(other, User):
            return False
        return self._id is not None and self._id == other._id
    
    def __hash__(self) -> int:
        """Hash based on ID"""
        return hash(self._id) if self._id else hash(self._username)
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"User(id={self._id}, username='{self._username}', role={self._role})"
