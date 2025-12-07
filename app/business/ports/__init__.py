"""Ports - Repository and Service Interfaces"""
from .user_repository import IUserRepository
from .product_repository import IProductRepository
from .order_repository import IOrderRepository
from .cart_repository import ICartRepository
from .category_repository import ICategoryRepository
from .brand_repository import IBrandRepository

__all__ = [
    'IUserRepository',
    'IProductRepository',
    'IOrderRepository',
    'ICartRepository',
    'ICategoryRepository',
    'IBrandRepository'
]
