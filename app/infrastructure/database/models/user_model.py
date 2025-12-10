"""
Infrastructure Layer - User ORM Model
This is NOT a domain entity - it's a database model for SQLAlchemy
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ...config.database import Base


class UserModel(Base):
    """
    User database model (Infrastructure layer)
    Maps to 'users' table in database
    
    ⚠️  This is separate from domain/entities/user.py
    """
    __tablename__ = 'users'
    
    # Primary Key
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # User credentials
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # User information
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)
    address = Column(String, nullable=True)  # TEXT in SQLite
    
    # Role and status
    role_id = Column(Integer, ForeignKey('roles.role_id'), nullable=False, default=2, index=True)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    
    # Relationships
    role = relationship('RoleModel', back_populates='users')
    carts = relationship('CartModel', back_populates='user', cascade='all, delete-orphan')
    orders = relationship('OrderModel', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<UserModel(id={self.user_id}, username='{self.username}', email='{self.email}')>"


class RoleModel(Base):
    """
    Role database model
    Maps to 'roles' table in database
    """
    __tablename__ = 'roles'
    
    role_id = Column(Integer, primary_key=True)
    role_name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    
    # Relationships
    users = relationship('UserModel', back_populates='role')
    
    def __repr__(self):
        return f"<RoleModel(id={self.role_id}, name='{self.role_name}')>"
