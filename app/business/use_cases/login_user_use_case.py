"""
Login User Use Case - Business Logic
"""
from ...domain.entities import User
from ...domain.value_objects import Email
from ...domain.exceptions import InvalidCredentialsException
from ..ports import IUserRepository


class LoginUserInputData:
    """Input data for user login"""
    
    def __init__(self, username_or_email: str, password_hash: str):
        """
        Args:
            username_or_email: Username or email address
            password_hash: Hashed password (for comparison)
        """
        self.username_or_email = username_or_email
        self.password_hash = password_hash


class LoginUserOutputData:
    """Output data for user login"""
    
    def __init__(
        self,
        success: bool,
        user_id: int = None,
        username: str = None,
        role: str = None,
        error_message: str = None
    ):
        self.success = success
        self.user_id = user_id
        self.username = username
        self.role = role
        self.error_message = error_message


class LoginUserUseCase:
    """Use case for user login"""
    
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
    
    def execute(self, input_data: LoginUserInputData) -> LoginUserOutputData:
        """
        Execute user login
        
        Args:
            input_data: Login credentials
            
        Returns:
            LoginUserOutputData with success status and user info
        """
        try:
            # Try to find user by username first
            user = self.user_repository.find_by_username(input_data.username_or_email)
            
            # If not found, try email
            if not user:
                try:
                    email = Email(input_data.username_or_email)
                    user = self.user_repository.find_by_email(email)
                except ValueError:
                    # Not a valid email, user not found
                    pass
            
            # User not found
            if not user:
                return LoginUserOutputData(
                    success=False,
                    error_message="Invalid username or email"
                )
            
            # Check if user is active
            try:
                user.ensure_active()
            except InvalidCredentialsException as e:
                return LoginUserOutputData(
                    success=False,
                    error_message="Account is deactivated"
                )
            
            # Password verification will be done in the adapter layer
            # (Infrastructure) where we have access to bcrypt
            # Here we just return user info for verification
            
            return LoginUserOutputData(
                success=True,
                user_id=user.id,
                username=user.username,
                role=user.role.value
            )
            
        except Exception as e:
            return LoginUserOutputData(
                success=False,
                error_message=f"Login failed: {str(e)}"
            )
