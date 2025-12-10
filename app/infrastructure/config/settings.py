"""
Infrastructure Layer - Application Settings
Configuration management for different environments
"""
import os
from pathlib import Path


class Config:
    """Base configuration"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database settings - MUST use absolute path
    BASE_DIR = Path(__file__).parent.parent.parent.parent.resolve()
    INSTANCE_DIR = BASE_DIR / 'instance'
    # Ensure absolute path for database
    DB_PATH = INSTANCE_DIR / 'camerashop.db'
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{DB_PATH.as_posix()}'  # Use forward slashes for SQLAlchemy
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings
    UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Session settings
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    
    # Security settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Pagination
    DEFAULT_PAGE_SIZE = 12
    MAX_PAGE_SIZE = 100


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # In-memory database for tests


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Override with environment variables in production
    SECRET_KEY = os.getenv('SECRET_KEY')  # MUST be set in production
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')  # MUST be set in production
    
    # Production security settings
    SESSION_COOKIE_SECURE = True  # HTTPS only


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """
    Get configuration for specified environment
    
    Args:
        env: Environment name (development, testing, production)
        
    Returns:
        Configuration class
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    
    return config.get(env, config['default'])
