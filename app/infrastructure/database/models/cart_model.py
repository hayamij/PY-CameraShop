"""
Infrastructure Layer - Cart ORM Model
This is NOT a domain entity - it's a database model for SQLAlchemy
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ...config.database import Base


class CartModel(Base):
    """
    Cart database model (Infrastructure layer)
    Maps to 'carts' table in database
    
    ⚠️  This is separate from domain/entities/cart.py
    """
    __tablename__ = 'carts'
    
    # Primary Key
    cart_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key (One cart per user)
    user_id = Column(Integer, ForeignKey('users.user_id'), unique=True, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    user = relationship('UserModel', back_populates='carts')
    items = relationship('CartItemModel', back_populates='cart', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<CartModel(id={self.cart_id}, user_id={self.user_id}, items={len(self.items)})>"


class CartItemModel(Base):
    """
    Cart Item database model
    Maps to 'cart_items' table in database
    """
    __tablename__ = 'cart_items'
    
    # Primary Key
    cart_item_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    cart_id = Column(Integer, ForeignKey('carts.cart_id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False, index=True)
    
    # Item data
    quantity = Column(Integer, nullable=False)
    
    # Relationships
    cart = relationship('CartModel', back_populates='items')
    product = relationship('ProductModel', back_populates='cart_items')
    
    def __repr__(self):
        return f"<CartItemModel(id={self.cart_item_id}, product_id={self.product_id}, qty={self.quantity})>"
