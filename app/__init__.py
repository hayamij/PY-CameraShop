"""
Flask Camera Shop Application
Clean Architecture Implementation
"""

__version__ = "1.0.0"

from .infrastructure.factory import create_app

__all__ = ['create_app']
