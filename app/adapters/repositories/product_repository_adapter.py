"""
Product Repository Adapter - Infrastructure Implementation
Implements IProductRepository port from Business layer

⚠️  CRITICAL: This adapter MUST follow the port interface EXACTLY
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ...business.ports.product_repository import IProductRepository
from ...domain.entities import Product
from ...domain.value_objects import Money
from ...infrastructure.database.models import ProductModel


class ProductRepositoryAdapter(IProductRepository):
    """
    Product Repository Adapter (Infrastructure layer)
    Converts between domain entities and database models
    """
    
    def __init__(self, session: Session):
        """
        Initialize repository with database session
        
        Args:
            session: SQLAlchemy session
        """
        self._session = session
    
    def save(self, product: Product) -> Product:
        """Save product to database"""
        try:
            if product.id is None:
                # Create new product
                product_model = self._to_orm_model(product)
                self._session.add(product_model)
            else:
                # Update existing product
                product_model = self._session.query(ProductModel).filter_by(product_id=product.id).first()
                if not product_model:
                    # Product doesn't exist, create new
                    product_model = self._to_orm_model(product)
                    self._session.add(product_model)
                else:
                    # Update existing
                    self._update_model_from_entity(product_model, product)
            
            self._session.commit()
            self._session.refresh(product_model)
            
            return self._to_domain_entity(product_model)
            
        except Exception as e:
            self._session.rollback()
            raise e
    
    def find_by_id(self, product_id: int) -> Optional[Product]:
        """Find product by ID"""
        product_model = self._session.query(ProductModel).filter_by(product_id=product_id).first()
        if product_model:
            return self._to_domain_entity(product_model)
        return None
    
    def find_all(self, skip: int = 0, limit: int = 100, visible_only: bool = True) -> List[Product]:
        """Find all products with pagination"""
        query = self._session.query(ProductModel)
        
        if visible_only:
            query = query.filter_by(is_visible=True)
        
        product_models = query.offset(skip).limit(limit).all()
        return [self._to_domain_entity(model) for model in product_models]
    
    def find_by_category(self, category_id: int, skip: int = 0, limit: int = 100) -> List[Product]:
        """Find products by category"""
        product_models = (
            self._session.query(ProductModel)
            .filter_by(category_id=category_id, is_visible=True)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_domain_entity(model) for model in product_models]
    
    def find_by_brand(self, brand_id: int, skip: int = 0, limit: int = 100) -> List[Product]:
        """Find products by brand"""
        product_models = (
            self._session.query(ProductModel)
            .filter_by(brand_id=brand_id, is_visible=True)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_domain_entity(model) for model in product_models]
    
    def search_by_name(self, query: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """Search products by name"""
        product_models = (
            self._session.query(ProductModel)
            .filter(
                ProductModel.name.ilike(f'%{query}%'),
                ProductModel.is_visible == True
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_domain_entity(model) for model in product_models]
    
    def find_by_ids(self, product_ids: List[int]) -> List[Product]:
        """Find multiple products by IDs"""
        product_models = (
            self._session.query(ProductModel)
            .filter(ProductModel.product_id.in_(product_ids))
            .all()
        )
        return [self._to_domain_entity(model) for model in product_models]
    
    def find_by_name(self, name: str) -> Optional[Product]:
        """Find product by exact name"""
        product_model = self._session.query(ProductModel).filter_by(name=name).first()
        if product_model:
            return self._to_domain_entity(product_model)
        return None
    
    def delete(self, product_id: int) -> bool:
        """Delete product"""
        product_model = self._session.query(ProductModel).filter_by(product_id=product_id).first()
        if product_model:
            self._session.delete(product_model)
            self._session.commit()
            return True
        return False
    
    def count(self, visible_only: bool = True) -> int:
        """Count total products"""
        query = self._session.query(ProductModel)
        if visible_only:
            query = query.filter_by(is_visible=True)
        return query.count()
    
    def count_by_category(self, category_id: int) -> int:
        """Count products in category"""
        return (
            self._session.query(ProductModel)
            .filter_by(category_id=category_id, is_visible=True)
            .count()
        )
    
    def count_by_brand(self, brand_id: int) -> int:
        """Count products by brand"""
        return (
            self._session.query(ProductModel)
            .filter_by(brand_id=brand_id, is_visible=True)
            .count()
        )
    
    # ========================================================================
    # CONVERSION METHODS (Domain Entity ↔ ORM Model)
    # ========================================================================
    
    def _to_domain_entity(self, model: ProductModel) -> Product:
        """
        Convert ORM model to domain entity
        Uses Product.reconstruct() to bypass validation
        """
        return Product.reconstruct(
            product_id=model.product_id,
            name=model.name,
            description=model.description,
            price=Money(float(model.price), 'VND'),
            stock_quantity=model.stock_quantity,
            category_id=model.category_id,
            brand_id=model.brand_id,
            image_url=model.image_url,
            is_visible=model.is_visible,
            created_at=model.created_at
        )
    
    def _to_orm_model(self, entity: Product) -> ProductModel:
        """
        Convert domain entity to ORM model (for new entities)
        """
        return ProductModel(
            product_id=entity.id if entity.id else None,
            name=entity.name,
            description=entity.description,
            price=entity.price.amount,
            stock_quantity=entity.stock_quantity,
            category_id=entity.category_id,
            brand_id=entity.brand_id,
            image_url=entity.image_url,
            is_visible=entity.is_visible,
            created_at=entity.created_at
        )
    
    def _update_model_from_entity(self, model: ProductModel, entity: Product):
        """
        Update existing ORM model from domain entity
        """
        model.name = entity.name
        model.description = entity.description
        model.price = entity.price.amount
        model.stock_quantity = entity.stock_quantity
        model.category_id = entity.category_id
        model.brand_id = entity.brand_id
        model.image_url = entity.image_url
        model.is_visible = entity.is_visible
