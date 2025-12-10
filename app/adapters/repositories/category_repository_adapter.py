"""
Category Repository Adapter - Infrastructure Implementation
Implements ICategoryRepository port from Business layer
"""
from typing import Optional, List
from sqlalchemy.orm import Session

from ...business.ports.category_repository import ICategoryRepository
from ...domain.entities import Category
from ...infrastructure.database.models import CategoryModel


class CategoryRepositoryAdapter(ICategoryRepository):
    """Category Repository Adapter (Infrastructure layer)"""
    
    def __init__(self, session: Session):
        self._session = session
    
    def save(self, category: Category) -> Category:
        """Save category to database"""
        try:
            if category.id is None:
                category_model = self._to_orm_model(category)
                self._session.add(category_model)
            else:
                category_model = self._session.query(CategoryModel).filter_by(category_id=category.id).first()
                if not category_model:
                    category_model = self._to_orm_model(category)
                    self._session.add(category_model)
                else:
                    self._update_model_from_entity(category_model, category)
            
            self._session.commit()
            self._session.refresh(category_model)
            
            return self._to_domain_entity(category_model)
        except Exception as e:
            self._session.rollback()
            raise e
    
    def find_by_id(self, category_id: int) -> Optional[Category]:
        """Find category by ID"""
        category_model = self._session.query(CategoryModel).filter_by(category_id=category_id).first()
        if category_model:
            return self._to_domain_entity(category_model)
        return None
    
    def find_by_name(self, name: str) -> Optional[Category]:
        """Find category by name"""
        category_model = self._session.query(CategoryModel).filter_by(name=name).first()
        if category_model:
            return self._to_domain_entity(category_model)
        return None
    
    def find_all(self, active_only: bool = True) -> List[Category]:
        """Find all categories"""
        query = self._session.query(CategoryModel)
        if active_only:
            query = query.filter(CategoryModel.is_active == True)
        category_models = query.all()
        return [self._to_domain_entity(model) for model in category_models]
    
    def delete(self, category_id: int) -> bool:
        """Delete category"""
        category_model = self._session.query(CategoryModel).filter_by(category_id=category_id).first()
        if category_model:
            self._session.delete(category_model)
            self._session.commit()
            return True
        return False
    
    def exists_by_name(self, name: str) -> bool:
        """Check if category name exists"""
        return self._session.query(CategoryModel).filter_by(name=name).count() > 0
    
    def count(self, active_only: bool = True) -> int:
        """Count total categories"""
        return self._session.query(CategoryModel).count()
    
    def _to_domain_entity(self, model: CategoryModel) -> Category:
        """Convert ORM model to domain entity"""
        return Category.reconstruct(
            category_id=model.category_id,
            name=model.name,
            description=model.description,
            is_active=model.is_active,
            created_at=model.created_at
        )
    
    def _to_orm_model(self, entity: Category) -> CategoryModel:
        """Convert domain entity to ORM model"""
        return CategoryModel(
            category_id=entity.id if entity.id else None,
            name=entity.name,
            description=entity.description,
            created_at=entity.created_at
        )
    
    def _update_model_from_entity(self, model: CategoryModel, entity: Category):
        """Update existing ORM model from domain entity"""
        model.name = entity.name
        model.description = entity.description
