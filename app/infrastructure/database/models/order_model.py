"""
Infrastructure Layer - Order ORM Model
This is NOT a domain entity - it's a database model for SQLAlchemy
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ...config.database import Base


class OrderModel(Base):
    """
    Order database model (Infrastructure layer)
    Maps to 'orders' table in database
    
    ⚠️  This is separate from domain/entities/order.py
    """
    __tablename__ = 'orders'
    
    # Primary Key
    order_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False, index=True)
    
    # Order details
    total_amount = Column(Numeric(18, 2), nullable=False)
    order_status = Column(String(50), nullable=False, default='CHO_XAC_NHAN', index=True)
    payment_method = Column(String(50), nullable=False)
    
    # Shipping information
    shipping_address = Column(String, nullable=False)  # TEXT in SQLite
    phone_number = Column(String(20), nullable=False)
    notes = Column(String, nullable=True)  # TEXT in SQLite
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.now, index=True)
    
    # Relationships
    user = relationship('UserModel', back_populates='orders')
    items = relationship('OrderItemModel', back_populates='order', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<OrderModel(id={self.order_id}, user_id={self.user_id}, status='{self.order_status}', total={self.total_amount})>"


class OrderItemModel(Base):
    """
    Order Item database model
    Maps to 'order_items' table in database
    """
    __tablename__ = 'order_items'
    
    # Primary Key
    order_item_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    order_id = Column(Integer, ForeignKey('orders.order_id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False, index=True)
    
    # Item data (captured at order time)
    product_name = Column(String(255), nullable=False)  # Captured product name
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(18, 2), nullable=False)  # Captured price at order time
    
    # Relationships
    order = relationship('OrderModel', back_populates='items')
    product = relationship('ProductModel', back_populates='order_items')
    
    def __repr__(self):
        return f"<OrderItemModel(id={self.order_item_id}, product='{self.product_name}', qty={self.quantity}, price={self.unit_price})>"
