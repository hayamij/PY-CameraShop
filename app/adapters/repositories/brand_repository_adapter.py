"""
Brand Repository Adapter - Infrastructure implementation
"""
from typing import Optional, List
from ...business.ports import IBrandRepository
from ...domain.entities import Brand
from ...infrastructure.database.models import BrandModel
from ...infrastructure.database.db import db


class BrandRepositoryAdapter(IBrandRepository):
    """Adapter implementing brand repository using SQLAlchemy"""
    
    def save(self, brand: Brand) -> Brand:
        """Save or update brand"""
        if brand.brand_id:
            # Update existing
            brand_model = BrandModel.query.get(brand.brand_id)
            if brand_model:
                brand_model.name = brand.name
                brand_model.description = brand.description
                brand_model.logo = brand.logo
        else:
            # Create new
            brand_model = self._to_db_model(brand)
            db.session.add(brand_model)
        
        db.session.commit()
        return self._to_domain(brand_model)
    
    def find_by_id(self, brand_id: int) -> Optional[Brand]:
        """Find brand by ID"""
        brand_model = BrandModel.query.get(brand_id)
        if brand_model:
            return self._to_domain(brand_model)
        return None
    
    def find_all(self) -> List[Brand]:
        """Find all brands"""
        brand_models = BrandModel.query.all()
        return [self._to_domain(model) for model in brand_models]
    
    def delete(self, brand_id: int) -> bool:
        """Delete brand by ID"""
        brand_model = BrandModel.query.get(brand_id)
        if brand_model:
            db.session.delete(brand_model)
            db.session.commit()
            return True
        return False
    
    def _to_domain(self, model: BrandModel) -> Brand:
        """Convert database model to domain entity"""
        return Brand.reconstruct(
            brand_id=model.id,
            name=model.name,
            description=model.description,
            logo=model.logo
        )
    
    def _to_db_model(self, brand: Brand) -> BrandModel:
        """Convert domain entity to database model"""
        return BrandModel(
            name=brand.name,
            description=brand.description,
            logo=brand.logo
        )
