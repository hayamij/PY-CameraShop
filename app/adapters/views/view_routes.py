"""Frontend view routes - Server-side rendering"""
from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from app.adapters.api.auth_helpers import login_required

# Create blueprint
view_bp = Blueprint('views', __name__)


@view_bp.route('/')
def index():
    """Home page"""
    return render_template('customer/index.html')


@view_bp.route('/products')
def products():
    """Product listing page"""
    return render_template('customer/products.html')


@view_bp.route('/products/<int:product_id>')
def product_detail(product_id):
    """Product detail page"""
    return render_template('customer/product-detail.html', product_id=product_id)


@view_bp.route('/cart')
@login_required
def cart():
    """Shopping cart page"""
    return render_template('customer/cart.html')


@view_bp.route('/checkout')
@login_required
def checkout():
    """Checkout page"""
    return render_template('customer/checkout.html')


@view_bp.route('/login')
def login():
    """Login page"""
    if session.get('user_id'):
        return redirect(url_for('views.index'))
    return render_template('auth/login.html')


@view_bp.route('/register')
def register():
    """Register page"""
    if session.get('user_id'):
        return redirect(url_for('views.index'))
    return render_template('auth/register.html')


@view_bp.route('/orders')
@login_required
def my_orders():
    """My orders page"""
    return render_template('customer/orders.html')


@view_bp.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    """Order detail page"""
    return render_template('customer/order-detail.html', order_id=order_id)


@view_bp.route('/admin')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    # Check if user is admin
    if session.get('role') != 'ADMIN':
        flash('Bạn không có quyền truy cập trang này', 'error')
        return redirect(url_for('views.index'))
    
    return render_template('admin/dashboard.html')


@view_bp.route('/admin/users')
@login_required
def admin_users():
    """Admin user management"""
    if session.get('role') != 'ADMIN':
        flash('Bạn không có quyền truy cập trang này', 'error')
        return redirect(url_for('views.index'))
    
    return render_template('admin/users.html')


@view_bp.route('/admin/products')
@login_required
def admin_products():
    """Admin product management"""
    if session.get('role') != 'ADMIN':
        flash('Bạn không có quyền truy cập trang này', 'error')
        return redirect(url_for('views.index'))
    
    return render_template('admin/products.html')


@view_bp.route('/admin/orders')
@login_required
def admin_orders():
    """Admin order management"""
    if session.get('role') != 'ADMIN':
        flash('Bạn không có quyền truy cập trang này', 'error')
        return redirect(url_for('views.index'))
    
    return render_template('admin/orders.html')


@view_bp.route('/admin/categories')
@login_required
def admin_categories():
    """Admin category management"""
    if session.get('role') != 'ADMIN':
        flash('Bạn không có quyền truy cập trang này', 'error')
        return redirect(url_for('views.index'))
    
    return render_template('admin/categories.html')


@view_bp.route('/admin/brands')
@login_required
def admin_brands():
    """Admin brand management"""
    if session.get('role') != 'ADMIN':
        flash('Bạn không có quyền truy cập trang này', 'error')
        return redirect(url_for('views.index'))
    
    return render_template('admin/brands.html')
