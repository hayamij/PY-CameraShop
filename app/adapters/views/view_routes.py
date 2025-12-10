"""Frontend view routes - Server-side rendering"""
from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from app.adapters.api.auth_helpers import login_required

# Create blueprint
view_bp = Blueprint('views', __name__)


@view_bp.route('/')
def index():
    """Home page - redirect to products if logged in"""
    if session.get('user_id'):
        # Already logged in, redirect based on role
        if session.get('role') == 'ADMIN':
            return redirect(url_for('views.admin_dashboard'))
        return redirect(url_for('views.products'))
    return render_template('index.html')


@view_bp.route('/products')
def products():
    """Product listing page"""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category_id', type=int)
    brand_id = request.args.get('brand_id', type=int)
    search = request.args.get('search', '')
    
    return render_template(
        'products/list.html',
        page=page,
        category_id=category_id,
        brand_id=brand_id,
        search=search
    )


@view_bp.route('/products/<int:product_id>')
def product_detail(product_id):
    """Product detail page"""
    return render_template('products/detail.html', product_id=product_id)


@view_bp.route('/cart')
@login_required
def cart():
    """Shopping cart page"""
    return render_template('cart/view.html')


@view_bp.route('/checkout')
@login_required
def checkout():
    """Checkout page"""
    return render_template('cart/checkout.html')


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
    return render_template('orders/my_orders.html')


@view_bp.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    """Order detail page"""
    return render_template('orders/detail.html', order_id=order_id)


@view_bp.route('/admin')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    # Check if user is admin
    if session.get('role') != 'ADMIN':
        flash('Bạn không có quyền truy cập trang này', 'error')
        return redirect(url_for('views.index'))
    
    return render_template('admin/dashboard/index.html')


@view_bp.route('/admin/products')
@login_required
def admin_products():
    """Admin product management"""
    if session.get('role') != 'ADMIN':
        flash('Bạn không có quyền truy cập trang này', 'error')
        return redirect(url_for('views.index'))
    
    return render_template('admin/products/list.html')


@view_bp.route('/admin/orders')
@login_required
def admin_orders():
    """Admin order management"""
    if session.get('role') != 'ADMIN':
        flash('Bạn không có quyền truy cập trang này', 'error')
        return redirect(url_for('views.index'))
    
    return render_template('admin/orders/list.html')


@view_bp.route('/admin/categories')
@login_required
def admin_categories():
    """Admin category management"""
    if session.get('role') != 'ADMIN':
        flash('Bạn không có quyền truy cập trang này', 'error')
        return redirect(url_for('views.index'))
    
    return render_template('admin/categories/list.html')


@view_bp.route('/admin/brands')
@login_required
def admin_brands():
    """Admin brand management"""
    if session.get('role') != 'ADMIN':
        flash('Bạn không có quyền truy cập trang này', 'error')
        return redirect(url_for('views.index'))
    
    return render_template('admin/brands/list.html')
