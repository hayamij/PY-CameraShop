"""
Product Repository Adapter - Infrastructure implementation
Converts between Domain entities and SQLAlchemy models
"""
from typing import Optional, List
from decimal import Decimal
from ...business.ports import IProductRepository
from ...domain.entities import Product
from ...domain.value_objects import Money
from ...infrastructure.database.models import ProductModel
from ...infrastructure.database.db import db


class ProductRepositoryAdapter(IProductRepository):
    """Adapter implementing product repository using SQLAlchemy"""
    
    def save(self, product: Product) -> Product:
        """Save or update product"""
        db_product = self._to_db_model(product)
        
        if product.id is None:
            # Create new
            db.session.add(db_product)
        else:
            # Update existing
            existing = db.session.query(ProductModel).filter_by(id=product.id).first()
            if existing:
                existing.name = db_product.name
                existing.description = db_product.description
                existing.price = db_product.price
                existing.currency = db_product.currency
                existing.stock_quantity = db_product.stock_quantity
                existing.category_id = db_product.category_id
                existing.brand_id = db_product.brand_id
                existing.image_url = db_product.image_url
                existing.is_visible = db_product.is_visible
        
        db.session.commit()
        
        if product.id is None:
            db.session.refresh(db_product)
        
        return self._to_domain(db_product)
    
    def find_by_id(self, product_id: int) -> Optional[Product]:
        """Find product by ID"""
        db_product = db.session.query(ProductModel).filter_by(id=product_id).first()
        return self._to_domain(db_product) if db_product else None
    
    def find_all(self, skip: int = 0, limit: int = 100, visible_only: bool = True) -> List[Product]:
        """Find all products with pagination"""
        query = db.session.query(ProductModel)
        if visible_only:
            query = query.filter_by(is_visible=True)
        db_products = query.offset(skip).limit(limit).all()
        return [self._to_domain(p) for p in db_products]
    
    def find_by_category(self, category_id: int, skip: int = 0, limit: int = 100) -> List[Product]:
        """Find products by category"""
        db_products = db.session.query(ProductModel)\
            .filter_by(category_id=category_id, is_visible=True)\
            .offset(skip).limit(limit).all()
        return [self._to_domain(p) for p in db_products]
    
    def find_by_brand(self, brand_id: int, skip: int = 0, limit: int = 100) -> List[Product]:
        """Find products by brand"""
        db_products = db.session.query(ProductModel)\
            .filter_by(brand_id=brand_id, is_visible=True)\
            .offset(skip).limit(limit).all()
        return [self._to_domain(p) for p in db_products]
    
    def search_by_name(self, query: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """Search products by name"""
        db_products = db.session.query(ProductModel)\
            .filter(ProductModel.name.ilike(f'%{query}%'))\
            .filter_by(is_visible=True)\
            .offset(skip).limit(limit).all()
        return [self._to_domain(p) for p in db_products]
    
    def find_by_ids(self, product_ids: List[int]) -> List[Product]:
        """Find multiple products by IDs"""
        db_products = db.session.query(ProductModel)\
            .filter(ProductModel.id.in_(product_ids)).all()
        return [self._to_domain(p) for p in db_products]
    
    def delete(self, product_id: int) -> bool:
        """Delete product"""
        db_product = db.session.query(ProductModel).filter_by(id=product_id).first()
        if db_product:
            db.session.delete(db_product)
            db.session.commit()
            return True
        return False
    
    def count(self, visible_only: bool = True) -> int:
        """Count total products"""
        query = db.session.query(ProductModel)
        if visible_only:
            query = query.filter_by(is_visible=True)
        return query.count()
    
    def count_by_category(self, category_id: int) -> int:
        """Count products in category"""
        return db.session.query(ProductModel)\
            .filter_by(category_id=category_id, is_visible=True).count()
    
    def count_by_brand(self, brand_id: int) -> int:
        """Count products by brand"""
        return db.session.query(ProductModel)\
            .filter_by(brand_id=brand_id, is_visible=True).count()
    
    # Conversion methods
    def _to_domain(self, db_product: ProductModel) -> Product:
        """Convert database model to domain entity"""
        return Product.reconstruct(
            product_id=db_product.id,
            name=db_product.name,
            description=db_product.description,
            price=Money(Decimal(str(db_product.price)), db_product.currency),
            stock_quantity=db_product.stock_quantity,
            category_id=db_product.category_id,
            brand_id=db_product.brand_id,
            image_url=db_product.image_url,
            is_visible=db_product.is_visible,
            created_at=db_product.created_at
        )
    
    def _to_db_model(self, product: Product) -> ProductModel:
        """Convert domain entity to database model"""
        return ProductModel(
            id=product.id,
            name=product.name,
            description=product.description,
            price=float(product.price.amount),
            currency=product.price.currency,
            stock_quantity=product.stock_quantity,
            category_id=product.category_id,
            brand_id=product.brand_id,
            image_url=product.image_url,
            is_visible=product.is_visible,
            created_at=product.created_at
        )
