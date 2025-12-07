"""
Customer Order Routes

Handles customer-facing order operations:
- View my orders
- View order detail
- Cancel order
- Order success page
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.business.use_cases import (
    GetMyOrdersUseCase, GetMyOrdersInputData,
    GetOrderDetailUseCase,
    CancelOrderUseCase, CancelOrderInputData
)
from app.adapters.repositories.order_repository_adapter import OrderRepositoryAdapter
from app.adapters.repositories.product_repository_adapter import ProductRepositoryAdapter
from app.infrastructure.database.db import db


order_bp = Blueprint('orders', __name__, url_prefix='/orders')


@order_bp.route('/my-orders', methods=['GET'])
@login_required
def my_orders():
    """View customer's orders"""
    try:
        order_repo = OrderRepositoryAdapter(db.session)
        use_case = GetMyOrdersUseCase(order_repo)
        
        # Get status filter from query params
        status_filter = request.args.get('status')
        
        input_data = GetMyOrdersInputData(
            user_id=current_user.id,
            status_filter=status_filter
        )
        
        output = use_case.execute(input_data)
        
        return render_template(
            'orders/my_orders.html',
            orders=output.orders,
            total_orders=output.total_orders,
            status_filter=status_filter
        )
    
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
        return redirect(url_for('main.index'))


@order_bp.route('/<int:order_id>', methods=['GET'])
@login_required
def order_detail(order_id):
    """View order detail"""
    try:
        order_repo = OrderRepositoryAdapter(db.session)
        use_case = GetOrderDetailUseCase(order_repo)
        
        output = use_case.execute(order_id)
        
        # Verify order belongs to current user (unless admin)
        if not current_user.is_admin():
            # Get full order to check user_id
            order = order_repo.find_by_id(order_id)
            if order and order.user_id != current_user.id:
                flash('Bạn không có quyền xem đơn hàng này', 'error')
                return redirect(url_for('order_bp.my_orders'))
        
        return render_template(
            'orders/order_detail.html',
            order=output
        )
    
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
        return redirect(url_for('order_bp.my_orders'))


@order_bp.route('/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    """Cancel a pending order"""
    try:
        order_repo = OrderRepositoryAdapter(db.session)
        product_repo = ProductRepositoryAdapter(db.session)
        use_case = CancelOrderUseCase(order_repo, product_repo)
        
        input_data = CancelOrderInputData(
            order_id=order_id,
            user_id=current_user.id
        )
        
        output = use_case.execute(input_data)
        
        flash(output.message, 'success')
    
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
    
    return redirect(url_for('order_bp.order_detail', order_id=order_id))


@order_bp.route('/success/<int:order_id>', methods=['GET'])
@login_required
def order_success(order_id):
    """Order success page"""
    try:
        order_repo = OrderRepositoryAdapter(db.session)
        use_case = GetOrderDetailUseCase(order_repo)
        
        output = use_case.execute(order_id)
        
        # Verify order belongs to current user
        order = order_repo.find_by_id(order_id)
        if order and order.user_id != current_user.id:
            flash('Bạn không có quyền xem đơn hàng này', 'error')
            return redirect(url_for('order_bp.my_orders'))
        
        return render_template(
            'orders/order_success.html',
            order=output
        )
    
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
        return redirect(url_for('order_bp.my_orders'))
