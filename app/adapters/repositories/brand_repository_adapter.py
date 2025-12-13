"""
Brand Repository Adapter - Infrastructure Implementation
Implements IBrandRepository port from Business layer
"""
from typing import Optional, List
from sqlalchemy.orm import Session

from ...business.ports.brand_repository import IBrandRepository
from ...domain.entities import Brand
from ...infrastructure.database.models import BrandModel


class BrandRepositoryAdapter(IBrandRepository):
    """Brand Repository Adapter (Infrastructure layer)"""
    
    def __init__(self, session: Session):
        self._session = session
    
    def save(self, brand: Brand) -> Brand:
        """Save brand to database"""
        try:
            if brand.id is None:
                brand_model = self._to_orm_model(brand)
                self._session.add(brand_model)
            else:
                brand_model = self._session.query(BrandModel).filter_by(brand_id=brand.id).first()
                if not brand_model:
                    brand_model = self._to_orm_model(brand)
                    self._session.add(brand_model)
                else:
                    self._update_model_from_entity(brand_model, brand)
            
            self._session.commit()
            self._session.refresh(brand_model)
            
            return self._to_domain_entity(brand_model)
        except Exception as e:
            self._session.rollback()
            raise e
    
    def find_by_id(self, brand_id: int) -> Optional[Brand]:
        """Find brand by ID"""
        brand_model = self._session.query(BrandModel).filter_by(brand_id=brand_id).first()
        if brand_model:
            return self._to_domain_entity(brand_model)
        return None
    
    def find_by_name(self, name: str) -> Optional[Brand]:
        """Find brand by name"""
        brand_model = self._session.query(BrandModel).filter_by(name=name).first()
        if brand_model:
            return self._to_domain_entity(brand_model)
        return None
    
    def find_all(self, active_only: bool = True) -> List[Brand]:
        """Find all brands"""
        query = self._session.query(BrandModel)
        if active_only:
            query = query.filter(BrandModel.is_active == True)
        brand_models = query.all()
        return [self._to_domain_entity(model) for model in brand_models]
    
    def delete(self, brand_id: int) -> bool:
        """Delete brand"""
        brand_model = self._session.query(BrandModel).filter_by(brand_id=brand_id).first()
        if brand_model:
            self._session.delete(brand_model)
            self._session.commit()
            return True
        return False
    
    def exists_by_name(self, name: str) -> bool:
        """Check if brand name exists"""
        return self._session.query(BrandModel).filter_by(name=name).count() > 0
    
    def count(self, active_only: bool = True) -> int:
        """Count total brands"""
        return self._session.query(BrandModel).count()
    
    def _to_domain_entity(self, model: BrandModel) -> Brand:
        """Convert ORM model to domain entity"""
        return Brand.reconstruct(
            brand_id=model.brand_id,
            name=model.name,
            description=model.description,
            logo_url=model.logo_url,
            is_active=model.is_active,
            created_at=model.created_at
        )
    
    def _to_orm_model(self, entity: Brand) -> BrandModel:
        """Convert domain entity to ORM model"""
        return BrandModel(
            brand_id=entity.id if entity.id else None,
            name=entity.name,
            description=entity.description,
            created_at=entity.created_at
        )
    
    def _update_model_from_entity(self, model: BrandModel, entity: Brand):
        """Update existing ORM model from domain entity"""
        model.name = entity.name
        model.description = entity.description
        model.logo_url = entity.logo_url
        model.is_active = entity.is_active
