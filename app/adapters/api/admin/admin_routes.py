"""
Admin Routes Blueprint
Admin dashboard and management
"""
from flask import Blueprint, render_template
from flask_login import login_required
from app.adapters.auth_decorators import admin_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    return render_template('admin/dashboard.html')


@admin_bp.route('/products')
@login_required
@admin_required
def manage_products():
    """Manage products"""
    return render_template('admin/products.html')


@admin_bp.route('/orders')
@login_required
@admin_required
def manage_orders():
    """Manage orders"""
    return render_template('admin/orders.html')


@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """Manage users"""
    return render_template('admin/users.html')
