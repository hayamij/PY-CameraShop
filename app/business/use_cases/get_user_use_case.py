"""
Get User Use Case - Business Logic
"""
from ...domain.entities import User
from ...domain.exceptions import UserNotFoundException
from ..ports import IUserRepository


class GetUserInputData:
    """Input data for getting user"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id


class GetUserOutputData:
    """Output data for getting user"""
    
    def __init__(
        self,
        success: bool,
        user: User = None,
        error_message: str = None
    ):
        self.success = success
        self.user = user
        self.error_message = error_message


class GetUserUseCase:
    """Use case for getting user by ID"""
    
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
    
    def execute(self, input_data: GetUserInputData) -> GetUserOutputData:
        """
        Execute get user
        
        Args:
            input_data: User ID
            
        Returns:
            GetUserOutputData with user entity
        """
        try:
            user = self.user_repository.find_by_id(input_data.user_id)
            
            if not user:
                raise UserNotFoundException(input_data.user_id)
            
            return GetUserOutputData(
                success=True,
                user=user
            )
            
        except UserNotFoundException as e:
            return GetUserOutputData(
                success=False,
                error_message=e.message
            )
        except Exception as e:
            return GetUserOutputData(
                success=False,
                error_message=f"Failed to get user: {str(e)}"
            )
