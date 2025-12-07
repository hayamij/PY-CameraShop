"""
User Repository Adapter - Infrastructure implementation
Converts between Domain entities and SQLAlchemy models
"""
from typing import Optional, List
from decimal import Decimal
from ...business.ports import IUserRepository
from ...domain.entities import User
from ...domain.value_objects import Email, PhoneNumber
from ...domain.enums import UserRole
from ...domain.exceptions import UserAlreadyExistsException
from ...infrastructure.database.models import UserModel
from ...infrastructure.database.db import db


class UserRepositoryAdapter(IUserRepository):
    """Adapter implementing user repository using SQLAlchemy"""
    
    def save(self, user: User) -> User:
        """Save or update user"""
        # Check for duplicates
        if user.id is None:  # New user
            if self.exists_by_username(user.username):
                raise UserAlreadyExistsException(f"username '{user.username}'")
            if self.exists_by_email(user.email):
                raise UserAlreadyExistsException(f"email '{user.email.address}'")
        
        # Convert domain entity to database model
        db_user = self._to_db_model(user)
        
        if user.id is None:
            # Create new
            db.session.add(db_user)
        else:
            # Update existing
            existing = db.session.query(UserModel).filter_by(id=user.id).first()
            if existing:
                existing.username = db_user.username
                existing.email = db_user.email
                existing.password_hash = db_user.password_hash
                existing.full_name = db_user.full_name
                existing.phone_number = db_user.phone_number
                existing.address = db_user.address
                existing.role = db_user.role
                existing.is_active = db_user.is_active
        
        db.session.commit()
        
        # Reload to get ID
        if user.id is None:
            db.session.refresh(db_user)
        
        return self._to_domain(db_user)
    
    def find_by_id(self, user_id: int) -> Optional[User]:
        """Find user by ID"""
        db_user = db.session.query(UserModel).filter_by(id=user_id).first()
        return self._to_domain(db_user) if db_user else None
    
    def find_by_username(self, username: str) -> Optional[User]:
        """Find user by username"""
        db_user = db.session.query(UserModel).filter_by(username=username).first()
        return self._to_domain(db_user) if db_user else None
    
    def find_by_email(self, email: Email) -> Optional[User]:
        """Find user by email"""
        db_user = db.session.query(UserModel).filter_by(email=email.address).first()
        return self._to_domain(db_user) if db_user else None
    
    def find_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Find all users with pagination"""
        db_users = db.session.query(UserModel).offset(skip).limit(limit).all()
        return [self._to_domain(db_user) for db_user in db_users]
    
    def find_by_role(self, role: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Find users by role"""
        db_users = db.session.query(UserModel).filter_by(role=role).offset(skip).limit(limit).all()
        return [self._to_domain(db_user) for db_user in db_users]
    
    def delete(self, user_id: int) -> bool:
        """Delete user"""
        db_user = db.session.query(UserModel).filter_by(id=user_id).first()
        if db_user:
            db.session.delete(db_user)
            db.session.commit()
            return True
        return False
    
    def exists_by_username(self, username: str) -> bool:
        """Check if username exists"""
        return db.session.query(UserModel).filter_by(username=username).first() is not None
    
    def exists_by_email(self, email: Email) -> bool:
        """Check if email exists"""
        return db.session.query(UserModel).filter_by(email=email.address).first() is not None
    
    def count(self) -> int:
        """Count total users"""
        return db.session.query(UserModel).count()
    
    # Conversion methods
    def _to_domain(self, db_user: UserModel) -> User:
        """Convert database model to domain entity"""
        return User.reconstruct(
            user_id=db_user.id,
            username=db_user.username,
            email=Email(db_user.email),
            password_hash=db_user.password_hash,
            full_name=db_user.full_name,
            phone_number=PhoneNumber(db_user.phone_number) if db_user.phone_number else None,
            address=db_user.address,
            role=UserRole(db_user.role),
            is_active=db_user.is_active,
            created_at=db_user.created_at
        )
    
    def _to_db_model(self, user: User) -> UserModel:
        """Convert domain entity to database model"""
        return UserModel(
            id=user.id,
            username=user.username,
            email=user.email.address,
            password_hash=user.password_hash,
            full_name=user.full_name,
            phone_number=user.phone_number.number if user.phone_number else None,
            address=user.address,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at
        )
