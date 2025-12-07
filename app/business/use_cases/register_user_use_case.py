"""
Register User Use Case - Business Logic
"""
from ...domain.entities import User
from ...domain.value_objects import Email, PhoneNumber
from ...domain.enums import UserRole
from ...domain.exceptions import UserAlreadyExistsException, DomainException
from ..ports import IUserRepository


class RegisterUserInputData:
    """Input data for user registration"""
    
    def __init__(
        self,
        username: str,
        email: str,
        password_hash: str,  # Already hashed by adapter
        full_name: str,
        phone_number: str = None,
        address: str = None
    ):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.full_name = full_name
        self.phone_number = phone_number
        self.address = address


class RegisterUserOutputData:
    """Output data for user registration"""
    
    def __init__(self, success: bool, user_id: int = None, error_message: str = None):
        self.success = success
        self.user_id = user_id
        self.error_message = error_message


class RegisterUserUseCase:
    """Use case for user registration"""
    
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
    
    def execute(self, input_data: RegisterUserInputData) -> RegisterUserOutputData:
        """
        Execute user registration
        
        Args:
            input_data: Registration data
            
        Returns:
            RegisterUserOutputData with success status
        """
        try:
            # Create email value object
            email = Email(input_data.email)
            
            # Create phone number value object if provided
            phone_number = None
            if input_data.phone_number:
                phone_number = PhoneNumber(input_data.phone_number)
            
            # Create user domain entity
            user = User(
                username=input_data.username,
                email=email,
                password_hash=input_data.password_hash,
                full_name=input_data.full_name,
                phone_number=phone_number,
                address=input_data.address,
                role=UserRole.CUSTOMER  # Default role
            )
            
            # Save user via repository
            saved_user = self.user_repository.save(user)
            
            return RegisterUserOutputData(
                success=True,
                user_id=saved_user.id
            )
            
        except UserAlreadyExistsException as e:
            return RegisterUserOutputData(
                success=False,
                error_message=e.message
            )
        except ValueError as e:
            return RegisterUserOutputData(
                success=False,
                error_message=str(e)
            )
        except Exception as e:
            return RegisterUserOutputData(
                success=False,
                error_message=f"Registration failed: {str(e)}"
            )
