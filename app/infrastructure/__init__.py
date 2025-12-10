"""
Infrastructure Layer Package
Contains database configuration, ORM models, and framework-specific code
"""
from .config import (
    Base,
    init_database,
    get_session,
    create_scoped_session,
    create_all_tables,
    drop_all_tables,
    get_engine,
    Config,
    get_config
)

from .database.models import (
    UserModel, RoleModel,
    ProductModel, CategoryModel, BrandModel,
    CartModel, CartItemModel,
    OrderModel, OrderItemModel
)

__all__ = [
    # Config
    'Base',
    'init_database',
    'get_session',
    'create_scoped_session',
    'create_all_tables',
    'drop_all_tables',
    'get_engine',
    'Config',
    'get_config',
    # Models
    'UserModel',
    'RoleModel',
    'ProductModel',
    'CategoryModel',
    'BrandModel',
    'CartModel',
    'CartItemModel',
    'OrderModel',
    'OrderItemModel'
]
