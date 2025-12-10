"""
Infrastructure Layer - Product ORM Model
This is NOT a domain entity - it's a database model for SQLAlchemy
"""
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ...config.database import Base


class ProductModel(Base):
    """
    Product database model (Infrastructure layer)
    Maps to 'products' table in database
    
    ⚠️  This is separate from domain/entities/product.py
    """
    __tablename__ = 'products'
    
    # Primary Key
    product_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Product information
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)  # TEXT in SQLite
    price = Column(Numeric(18, 2), nullable=False, index=True)
    stock_quantity = Column(Integer, nullable=False, default=0)
    
    # Foreign Keys
    category_id = Column(Integer, ForeignKey('categories.category_id'), nullable=False, index=True)
    brand_id = Column(Integer, ForeignKey('brands.brand_id'), nullable=False, index=True)
    
    # Media
    image_url = Column(String(500), nullable=True)
    
    # Visibility
    is_visible = Column(Boolean, nullable=False, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    
    # Relationships
    category = relationship('CategoryModel', back_populates='products')
    brand = relationship('BrandModel', back_populates='products')
    cart_items = relationship('CartItemModel', back_populates='product')
    order_items = relationship('OrderItemModel', back_populates='product')
    
    def __repr__(self):
        return f"<ProductModel(id={self.product_id}, name='{self.name}', price={self.price})>"


class CategoryModel(Base):
    """
    Category database model
    Maps to 'categories' table in database
    """
    __tablename__ = 'categories'
    
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    
    # Relationships
    products = relationship('ProductModel', back_populates='category')
    
    def __repr__(self):
        return f"<CategoryModel(id={self.category_id}, name='{self.name}')>"


class BrandModel(Base):
    """
    Brand database model
    Maps to 'brands' table in database
    """
    __tablename__ = 'brands'
    
    brand_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    
    # Relationships
    products = relationship('ProductModel', back_populates='brand')
    
    def __repr__(self):
        return f"<BrandModel(id={self.brand_id}, name='{self.name}')>"
