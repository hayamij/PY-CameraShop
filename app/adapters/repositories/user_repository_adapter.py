"""
User Repository Adapter - Infrastructure Implementation
Implements IUserRepository port from Business layer

⚠️  CRITICAL: This adapter MUST follow the port interface EXACTLY
No modifications to business layer contracts!
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ...business.ports.user_repository import IUserRepository
from ...domain.entities import User
from ...domain.enums import UserRole
from ...domain.value_objects import Email, PhoneNumber
from ...domain.exceptions import UserAlreadyExistsException
from ...infrastructure.database.models import UserModel


class UserRepositoryAdapter(IUserRepository):
    """
    User Repository Adapter (Infrastructure layer)
    Converts between domain entities and database models
    """
    
    def __init__(self, session: Session):
        """
        Initialize repository with database session
        
        Args:
            session: SQLAlchemy session (scoped session for request lifecycle)
        """
        self._session = session
    
    def save(self, user: User) -> User:
        """Save user to database"""
        try:
            if user.id is None:
                # Create new user
                user_model = self._to_orm_model(user)
                self._session.add(user_model)
            else:
                # Update existing user
                user_model = self._session.query(UserModel).filter_by(user_id=user.id).first()
                if not user_model:
                    # User doesn't exist, create new
                    user_model = self._to_orm_model(user)
                    self._session.add(user_model)
                else:
                    # Update existing
                    self._update_model_from_entity(user_model, user)
            
            self._session.commit()
            self._session.refresh(user_model)
            
            return self._to_domain_entity(user_model)
            
        except IntegrityError as e:
            self._session.rollback()
            error_msg = str(e.orig).lower()
            if 'username' in error_msg:
                raise UserAlreadyExistsException(f"Username '{user.username}' already exists")
            elif 'email' in error_msg:
                raise UserAlreadyExistsException(f"Email '{user.email.address}' already exists")
            else:
                raise UserAlreadyExistsException("User with this username or email already exists")
        except Exception as e:
            self._session.rollback()
            raise e
    
    def find_by_id(self, user_id: int) -> Optional[User]:
        """Find user by ID"""
        user_model = self._session.query(UserModel).filter_by(user_id=user_id).first()
        if user_model:
            return self._to_domain_entity(user_model)
        return None
    
    def find_by_username(self, username: str) -> Optional[User]:
        """Find user by username"""
        user_model = self._session.query(UserModel).filter_by(username=username).first()
        if user_model:
            return self._to_domain_entity(user_model)
        return None
    
    def find_by_email(self, email: Email) -> Optional[User]:
        """Find user by email"""
        user_model = self._session.query(UserModel).filter_by(email=email.address).first()
        if user_model:
            return self._to_domain_entity(user_model)
        return None
    
    def find_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Find all users with pagination"""
        user_models = self._session.query(UserModel).offset(skip).limit(limit).all()
        return [self._to_domain_entity(model) for model in user_models]
    
    def find_by_role(self, role: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Find users by role"""
        # Map role string to role_id
        role_map = {'ADMIN': 1, 'CUSTOMER': 2}
        role_id = role_map.get(role.upper(), 2)
        
        user_models = self._session.query(UserModel).filter_by(role_id=role_id).offset(skip).limit(limit).all()
        return [self._to_domain_entity(model) for model in user_models]
    
    def delete(self, user_id: int) -> bool:
        """Delete user"""
        user_model = self._session.query(UserModel).filter_by(user_id=user_id).first()
        if user_model:
            self._session.delete(user_model)
            self._session.commit()
            return True
        return False
    
    def exists_by_username(self, username: str) -> bool:
        """Check if username exists"""
        count = self._session.query(UserModel).filter_by(username=username).count()
        return count > 0
    
    def exists_by_email(self, email: Email) -> bool:
        """Check if email exists"""
        count = self._session.query(UserModel).filter_by(email=email.address).count()
        return count > 0
    
    def count(self) -> int:
        """Count total users"""
        return self._session.query(UserModel).count()
    
    # ========================================================================
    # NEW METHODS FOR ADMIN USER MANAGEMENT (USE CASE 1: ListUsers)
    # ========================================================================
    
    def find_all_with_filters(
        self,
        filters: dict,
        page: int = 1,
        per_page: int = 20,
        sort_by: str = 'created_at_desc'
    ) -> tuple[List[User], int]:
        """
        Find users with filters, pagination, and sorting
        
        Args:
            filters: Dict with keys: role (str), is_active (bool), search_query (str)
            page: Page number (1-indexed)
            per_page: Items per page
            sort_by: Sort option (name_asc, name_desc, created_at_asc, created_at_desc)
        
        Returns:
            Tuple of (list of User entities, total count)
        """
        # Build base query
        query = self._session.query(UserModel)
        
        # Apply filters
        if 'role' in filters:
            role_map = {'ADMIN': 1, 'CUSTOMER': 2}
            role_id = role_map.get(filters['role'].upper(), 2)
            query = query.filter(UserModel.role_id == role_id)
        
        if 'is_active' in filters:
            query = query.filter(UserModel.is_active == filters['is_active'])
        
        if 'search_query' in filters and filters['search_query']:
            search_term = f"%{filters['search_query']}%"
            query = query.filter(
                (UserModel.username.ilike(search_term)) |
                (UserModel.full_name.ilike(search_term)) |
                (UserModel.email.ilike(search_term))
            )
        
        # Get total count BEFORE pagination
        total_count = query.count()
        
        # Apply sorting
        sort_map = {
            'name_asc': UserModel.full_name.asc(),
            'name_desc': UserModel.full_name.desc(),
            'created_at_asc': UserModel.created_at.asc(),
            'created_at_desc': UserModel.created_at.desc()
        }
        order_by = sort_map.get(sort_by, UserModel.created_at.desc())
        query = query.order_by(order_by)
        
        # Apply pagination
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        
        # Execute query
        user_models = query.all()
        users = [self._to_domain_entity(model) for model in user_models]
        
        return users, total_count
    
    def search_by_query(self, query: str, limit: int = 50) -> List[User]:
        """
        Search users by query string (matches username, full_name, email)
        
        Args:
            query: Search query string
            limit: Max results to return
        
        Returns:
            List of User entities matching the query
        """
        search_term = f"%{query}%"
        user_models = self._session.query(UserModel).filter(
            (UserModel.username.ilike(search_term)) |
            (UserModel.full_name.ilike(search_term)) |
            (UserModel.email.ilike(search_term))
        ).limit(limit).all()
        
        return [self._to_domain_entity(model) for model in user_models]
    
    def count_by_role(self, role: str) -> int:
        """
        Count users by role
        
        Args:
            role: Role name (ADMIN or CUSTOMER)
        
        Returns:
            Number of users with specified role
        """
        role_map = {'ADMIN': 1, 'CUSTOMER': 2}
        role_id = role_map.get(role.upper(), 2)
        
        return self._session.query(UserModel).filter(
            UserModel.role_id == role_id
        ).count()
    
    def count_active_users(self) -> int:
        """
        Count active users
        
        Returns:
            Number of active users
        """
        return self._session.query(UserModel).filter(
            UserModel.is_active == True
        ).count()
    
    # ========================================================================
    # CONVERSION METHODS (Domain Entity ↔ ORM Model)
    # ========================================================================
    
    def _to_domain_entity(self, model: UserModel) -> User:
        """
        Convert ORM model to domain entity
        Uses User.reconstruct() to bypass validation
        """
        return User.reconstruct(
            user_id=model.user_id,
            username=model.username,
            email=Email(model.email),
            password_hash=model.password_hash,
            full_name=model.full_name,
            phone_number=PhoneNumber(model.phone_number) if model.phone_number else None,
            address=model.address,
            role=UserRole.ADMIN if model.role_id == 1 else UserRole.CUSTOMER,
            is_active=model.is_active,
            created_at=model.created_at
        )
    
    def _to_orm_model(self, entity: User) -> UserModel:
        """
        Convert domain entity to ORM model (for new entities)
        """
        # Map role enum to role_id
        role_id = 1 if entity.role == UserRole.ADMIN else 2
        
        return UserModel(
            user_id=entity.id if entity.id else None,
            username=entity.username,
            email=entity.email.address,
            password_hash=entity.password_hash,
            full_name=entity.full_name,
            phone_number=entity.phone_number.number if entity.phone_number else None,
            address=entity.address,
            role_id=role_id,
            is_active=entity.is_active,
            created_at=entity.created_at
        )
    
    def _update_model_from_entity(self, model: UserModel, entity: User):
        """
        Update existing ORM model from domain entity
        """
        model.username = entity.username
        model.email = entity.email.address
        model.password_hash = entity.password_hash
        model.full_name = entity.full_name
        model.phone_number = entity.phone_number.number if entity.phone_number else None
        model.address = entity.address
        model.role_id = 1 if entity.role == UserRole.ADMIN else 2
        model.is_active = entity.is_active
