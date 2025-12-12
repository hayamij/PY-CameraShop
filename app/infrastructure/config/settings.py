"""
Infrastructure Layer - Application Settings
Configuration management for different environments
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file (critical for reloader subprocess)
load_dotenv()


class Config:
    """Base configuration"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # SQL Server Database settings
    SQL_SERVER = os.getenv('SQL_SERVER', 'localhost')
    SQL_DATABASE = os.getenv('SQL_DATABASE', 'CameraShopDB')
    SQL_USERNAME = os.getenv('SQL_USERNAME', 'fuongtuan')
    SQL_PASSWORD = os.getenv('SQL_PASSWORD', 'toilabanhmochi')
    SQL_DRIVER = os.getenv('SQL_DRIVER', 'ODBC Driver 17 for SQL Server')
    
    # Build connection string for SQL Server
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'mssql+pyodbc://{SQL_USERNAME}:{SQL_PASSWORD}@{SQL_SERVER}/{SQL_DATABASE}?driver={SQL_DRIVER.replace(" ", "+")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'pool_size': 10,
        'max_overflow': 20
    }
    
    # Base directory for file paths
    BASE_DIR = Path(__file__).parent.parent.parent.parent.resolve()
    
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
