"""
Authentication Helpers - Decorators for route protection
"""
from functools import wraps
from flask import session, jsonify
from ...domain.enums import UserRole


def login_required(f):
    """
    Decorator to require authentication for a route.
    
    Usage:
        @app.route('/protected')
        @login_required
        def protected_route():
            user_id = session['user_id']
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorator to require admin role for a route.
    
    Usage:
        @app.route('/admin/dashboard')
        @admin_required
        def admin_dashboard():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        if session.get('role') != UserRole.ADMIN.value:
            return jsonify({
                'success': False,
                'error': 'Admin access required'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function


def get_current_user_id():
    """
    Get current authenticated user ID from session.
    
    Returns:
        int: User ID if authenticated
        None: If not authenticated
    """
    return session.get('user_id')


def get_current_user_role():
    """
    Get current authenticated user role from session.
    
    Returns:
        str: User role if authenticated
        None: If not authenticated
    """
    return session.get('role')


def is_authenticated():
    """
    Check if user is currently authenticated.
    
    Returns:
        bool: True if authenticated, False otherwise
    """
    return 'user_id' in session


def is_admin():
    """
    Check if current user is an admin.
    
    Returns:
        bool: True if user is admin, False otherwise
    """
    return session.get('role') == UserRole.ADMIN.value
