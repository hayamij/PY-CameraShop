"""
Brand Domain Entity - Product brand information
NO framework dependencies!
"""
from datetime import datetime
from typing import Optional


class Brand:
    """
    Brand domain entity
    
    Business Rules:
    - Name must be unique
    - Logo URL is optional
    - Brands can be hidden without deletion
    """
    
    def __init__(self, name: str, description: Optional[str] = None, logo_url: Optional[str] = None):
        """
        Create a new brand
        
        Args:
            name: Brand name
            description: Brand description (optional)
            logo_url: Brand logo URL (optional)
            
        Raises:
            ValueError: If validation fails
        """
        if not name or len(name) < 2:
            raise ValueError("Brand name must be at least 2 characters")
        
        self._id: Optional[int] = None
        self._name = name.strip()
        self._description = description.strip() if description else None
        self._logo_url = logo_url
        self._is_active = True
        self._created_at = datetime.now()
    
    @staticmethod
    def reconstruct(
        brand_id: int,
        name: str,
        description: Optional[str],
        logo_url: Optional[str],
        is_active: bool,
        created_at: datetime
    ) -> 'Brand':
        """Reconstruct brand from database (no validation)"""
        brand = object.__new__(Brand)
        brand._id = brand_id
        brand._name = name
        brand._description = description
        brand._logo_url = logo_url
        brand._is_active = is_active
        brand._created_at = created_at
        return brand
    
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
    def logo_url(self) -> Optional[str]:
        return self._logo_url
    
    @property
    def is_active(self) -> bool:
        return self._is_active
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    # Business methods
    def update_details(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        logo_url: Optional[str] = None
    ):
        """Update brand details"""
        if name:
            if len(name) < 2:
                raise ValueError("Brand name must be at least 2 characters")
            self._name = name.strip()
        
        if description is not None:
            self._description = description.strip() if description else None
        
        if logo_url is not None:
            self._logo_url = logo_url
    
    def deactivate(self):
        """Deactivate brand"""
        if not self._is_active:
            raise ValueError("Brand is already inactive")
        self._is_active = False
    
    def activate(self):
        """Activate brand"""
        if self._is_active:
            raise ValueError("Brand is already active")
        self._is_active = True
    
    def __eq__(self, other) -> bool:
        """Check equality based on ID"""
        if not isinstance(other, Brand):
            return False
        return self._id is not None and self._id == other._id
    
    def __hash__(self) -> int:
        """Hash based on ID"""
        return hash(self._id) if self._id else hash(self._name)
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"Brand(id={self._id}, name='{self._name}')"
