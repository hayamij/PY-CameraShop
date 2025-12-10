"""
Infrastructure Layer - Database Configuration
Manages database connection and session lifecycle
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
import os

# Create declarative base for ORM models
Base = declarative_base()

# Global session factory
_session_factory = None
_engine = None


def init_database(app=None, db_url=None):
    """
    Initialize database connection
    
    Args:
        app: Flask app instance (optional, for getting config)
        db_url: Database URL (optional, overrides app config)
    """
    global _session_factory, _engine
    
    # Determine database URL
    if db_url is None:
        if app:
            db_url = app.config.get('SQLALCHEMY_DATABASE_URI')
        else:
            # Default to absolute path
            from pathlib import Path
            base_dir = Path(__file__).parent.parent.parent.parent
            db_path = base_dir / 'instance' / 'camerashop.db'
            db_url = f'sqlite:///{db_path}'
    
    # Debug: Print database URL
    print(f"🔧 Initializing database: {db_url}")
    
    # Create engine
    _engine = create_engine(
        db_url,
        echo=False,  # Set to True for SQL query logging
        pool_pre_ping=True,  # Verify connections before using
        connect_args={'check_same_thread': False} if 'sqlite' in db_url else {}
    )
    
    # Create session factory
    _session_factory = sessionmaker(bind=_engine)
    
    return _engine


def get_session():
    """
    Get a new database session
    
    Returns:
        SQLAlchemy Session instance
    """
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _session_factory()


def create_scoped_session():
    """
    Create a thread-safe scoped session
    
    Returns:
        Scoped session for use in web applications
    """
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return scoped_session(_session_factory)


def create_all_tables():
    """
    Create all tables defined in models
    """
    if _engine is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    Base.metadata.create_all(_engine)


def drop_all_tables():
    """
    Drop all tables (use with caution!)
    """
    if _engine is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    Base.metadata.drop_all(_engine)


def get_engine():
    """
    Get the database engine
    
    Returns:
        SQLAlchemy Engine instance
    """
    return _engine
