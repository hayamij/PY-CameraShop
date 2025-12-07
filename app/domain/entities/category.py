"""
Category Domain Entity - Product categorization
NO framework dependencies!
"""
from datetime import datetime
from typing import Optional


class Category:
    """
    Category domain entity
    
    Business Rules:
    - Name must be unique
    - Description is optional
    - Categories can be hidden without deletion
    """
    
    def __init__(self, name: str, description: Optional[str] = None):
        """
        Create a new category
        
        Args:
            name: Category name
            description: Category description (optional)
            
        Raises:
            ValueError: If validation fails
        """
        if not name or len(name) < 2:
            raise ValueError("Category name must be at least 2 characters")
        
        self._id: Optional[int] = None
        self._name = name.strip()
        self._description = description.strip() if description else None
        self._is_active = True
        self._created_at = datetime.now()
    
    @staticmethod
    def reconstruct(
        category_id: int,
        name: str,
        description: Optional[str],
        is_active: bool,
        created_at: datetime
    ) -> 'Category':
        """Reconstruct category from database (no validation)"""
        category = object.__new__(Category)
        category._id = category_id
        category._name = name
        category._description = description
        category._is_active = is_active
        category._created_at = created_at
        return category
    
    # Getters
    @property
    def id(self) -> Optional[int]:
        return self._id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> Optional[str]:
        return self._description
    
    @property
    def is_active(self) -> bool:
        return self._is_active
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    # Business methods
    def update_details(self, name: Optional[str] = None, description: Optional[str] = None):
        """Update category details"""
        if name:
            if len(name) < 2:
                raise ValueError("Category name must be at least 2 characters")
            self._name = name.strip()
        
        if description is not None:
            self._description = description.strip() if description else None
    
    def deactivate(self):
        """Deactivate category"""
        if not self._is_active:
            raise ValueError("Category is already inactive")
        self._is_active = False
    
    def activate(self):
        """Activate category"""
        if self._is_active:
            raise ValueError("Category is already active")
        self._is_active = True
    
    def __eq__(self, other) -> bool:
        """Check equality based on ID"""
        if not isinstance(other, Category):
            return False
        return self._id is not None and self._id == other._id
    
    def __hash__(self) -> int:
        """Hash based on ID"""
        return hash(self._id) if self._id else hash(self._name)
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"Category(id={self._id}, name='{self._name}')"
