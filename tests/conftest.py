"""
Pytest configuration and fixtures

Provides common test fixtures and configuration
"""

import pytest
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def mock_db_session():
    """Mock database session"""
    from unittest.mock import Mock
    session = Mock()
    session.commit = Mock()
    session.rollback = Mock()
    session.close = Mock()
    return session
