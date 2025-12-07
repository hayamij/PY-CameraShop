"""
Category Repository Adapter - Infrastructure implementation
"""
from typing import Optional, List
from ...business.ports import ICategoryRepository
from ...domain.entities import Category
from ...infrastructure.database.models import CategoryModel
from ...infrastructure.database.db import db


class CategoryRepositoryAdapter(ICategoryRepository):
    """Adapter implementing category repository using SQLAlchemy"""
    
    def save(self, category: Category) -> Category:
        """Save or update category"""
        if category.category_id:
            # Update existing
            category_model = CategoryModel.query.get(category.category_id)
            if category_model:
                category_model.name = category.name
                category_model.description = category.description
                category_model.slug = category.slug
        else:
            # Create new
            category_model = self._to_db_model(category)
            db.session.add(category_model)
        
        db.session.commit()
        return self._to_domain(category_model)
    
    def find_by_id(self, category_id: int) -> Optional[Category]:
        """Find category by ID"""
        category_model = CategoryModel.query.get(category_id)
        if category_model:
            return self._to_domain(category_model)
        return None
    
    def find_all(self) -> List[Category]:
        """Find all categories"""
        category_models = CategoryModel.query.all()
        return [self._to_domain(model) for model in category_models]
    
    def delete(self, category_id: int) -> bool:
        """Delete category by ID"""
        category_model = CategoryModel.query.get(category_id)
        if category_model:
            db.session.delete(category_model)
            db.session.commit()
            return True
        return False
    
    def _to_domain(self, model: CategoryModel) -> Category:
        """Convert database model to domain entity"""
        return Category.reconstruct(
            category_id=model.id,
            name=model.name,
            description=model.description,
            slug=model.slug
        )
    
    def _to_db_model(self, category: Category) -> CategoryModel:
        """Convert domain entity to database model"""
        return CategoryModel(
            name=category.name,
            description=category.description,
            slug=category.slug
        )
