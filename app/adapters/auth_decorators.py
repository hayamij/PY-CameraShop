"""
Authorization Utilities
Decorators for role-based access control
"""
from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user


def admin_required(f):
    """
    Decorator to require admin role
    
    Usage:
        @admin_required
        def admin_dashboard():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Vui lòng đăng nhập để truy cập trang này', 'warning')
            return redirect(url_for('auth.login'))
        
        if current_user.role != 'ADMIN':
            flash('Bạn không có quyền truy cập trang này', 'danger')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def customer_required(f):
    """
    Decorator to require customer role (or admin)
    
    Usage:
        @customer_required
        def my_orders():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Vui lòng đăng nhập để truy cập trang này', 'warning')
            return redirect(url_for('auth.login'))
        
        if current_user.role not in ['CUSTOMER', 'ADMIN']:
            flash('Bạn không có quyền truy cập trang này', 'danger')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """
    Decorator to require specific roles
    
    Usage:
        @role_required('ADMIN', 'MANAGER')
        def dashboard():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Vui lòng đăng nhập để truy cập trang này', 'warning')
                return redirect(url_for('auth.login'))
            
            if current_user.role not in roles:
                flash('Bạn không có quyền truy cập trang này', 'danger')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
