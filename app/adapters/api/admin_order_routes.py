"""
Admin Order Routes - Order management for administrators
Clean Architecture - Adapters Layer
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime

from app.business.use_cases import (
    ListOrdersUseCase,
    ListOrdersInputData,
    GetOrderDetailUseCase,
    UpdateOrderStatusUseCase,
    UpdateOrderStatusInputData
)
from app.adapters.repositories import OrderRepositoryAdapter, UserRepositoryAdapter, ProductRepositoryAdapter
from app.infrastructure.database import db


# Create blueprint
admin_orders_bp = Blueprint('admin_orders', __name__, url_prefix='/admin/orders')


# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login to access this page', 'error')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin():
            flash('You do not have permission to access this page', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_orders_bp.route('/')
@login_required
@admin_required
def list_orders():
    """
    Admin: List all orders with filters and pagination
    Supports filters: status, customer_id, date_range, search
    """
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', None)
    customer_id = request.args.get('customer_id', None, type=int)
    search_query = request.args.get('search', None)
    sort_by = request.args.get('sort', 'newest')
    
    # Date range filters
    start_date = None
    end_date = None
    if request.args.get('start_date'):
        try:
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
        except ValueError:
            pass
    
    if request.args.get('end_date'):
        try:
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d')
        except ValueError:
            pass
    
    # Create repositories
    order_repo = OrderRepositoryAdapter()
    user_repo = UserRepositoryAdapter()
    
    # Create use case
    list_orders_use_case = ListOrdersUseCase(order_repo, user_repo)
    
    # Create input data
    input_data = ListOrdersInputData(
        page=page,
        per_page=per_page,
        status=status,
        customer_id=customer_id,
        start_date=start_date,
        end_date=end_date,
        search_query=search_query,
        sort_by=sort_by
    )
    
    # Execute use case
    output = list_orders_use_case.execute(input_data)
    
    if not output.success:
        flash(output.message, 'error')
    
    # Render template
    return render_template(
        'admin/orders/list.html',
        output=output,
        current_page=page,
        per_page=per_page,
        status_filter=status,
        customer_id_filter=customer_id,
        search_query=search_query,
        sort_by=sort_by,
        start_date=request.args.get('start_date', ''),
        end_date=request.args.get('end_date', '')
    )


@admin_orders_bp.route('/<int:order_id>')
@login_required
@admin_required
def order_detail(order_id):
    """
    Admin: View detailed information for a specific order
    """
    # Create repositories
    order_repo = OrderRepositoryAdapter()
    user_repo = UserRepositoryAdapter()
    product_repo = ProductRepositoryAdapter()
    
    # Create use case
    get_order_detail_use_case = GetOrderDetailUseCase(order_repo, user_repo, product_repo)
    
    # Execute use case
    output = get_order_detail_use_case.execute(order_id)
    
    if not output.success:
        flash(output.message, 'error')
        return redirect(url_for('admin_orders.list_orders'))
    
    # Render template
    return render_template(
        'admin/orders/detail.html',
        output=output
    )


@admin_orders_bp.route('/<int:order_id>/update-status', methods=['POST'])
@login_required
@admin_required
def update_status(order_id):
    """
    Admin: Update order status
    Supports AJAX requests
    """
    # Get new status from form
    new_status = request.form.get('status')
    admin_notes = request.form.get('notes', '')
    
    if not new_status:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Status is required'}), 400
        flash('Status is required', 'error')
        return redirect(url_for('admin_orders.order_detail', order_id=order_id))
    
    # Create repository
    order_repo = OrderRepositoryAdapter()
    
    # Create use case
    update_status_use_case = UpdateOrderStatusUseCase(order_repo)
    
    # Create input data
    input_data = UpdateOrderStatusInputData(
        order_id=order_id,
        new_status=new_status,
        admin_notes=admin_notes
    )
    
    # Execute use case
    output = update_status_use_case.execute(input_data)
    
    # Handle AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if output.success:
            return jsonify({
                'success': True,
                'message': output.message,
                'old_status': output.old_status,
                'new_status': output.new_status
            })
        else:
            return jsonify({
                'success': False,
                'message': output.message
            }), 400
    
    # Handle regular form submission
    if output.success:
        flash(output.message, 'success')
    else:
        flash(output.message, 'error')
    
    return redirect(url_for('admin_orders.order_detail', order_id=order_id))


@admin_orders_bp.route('/statistics')
@login_required
@admin_required
def statistics():
    """
    Admin: View order statistics and analytics
    """
    # Create repository
    order_repo = OrderRepositoryAdapter()
    
    # Get statistics (all orders)
    stats = order_repo.get_order_statistics()
    
    # Get monthly revenue data (for charts)
    # This will be implemented with Plotly in the next phase
    
    return render_template(
        'admin/orders/statistics.html',
        stats=stats
    )


@admin_orders_bp.route('/export')
@login_required
@admin_required
def export_orders():
    """
    Admin: Export orders to Excel/PDF
    This will be implemented in Phase 7 (Data Export)
    """
    flash('Export functionality will be available soon', 'info')
    return redirect(url_for('admin_orders.list_orders'))
