"""
Checkout Routes

Handles the multi-step checkout process:
- Step 1: Review cart
- Step 2: Enter shipping information
- Step 3: Select payment method
- Step 4: Confirm and place order
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app.business.use_cases import (
    ViewCartUseCase,
    PlaceOrderUseCase, PlaceOrderInputData
)
from app.adapters.repositories.cart_repository_adapter import CartRepositoryAdapter
from app.adapters.repositories.order_repository_adapter import OrderRepositoryAdapter
from app.adapters.repositories.product_repository_adapter import ProductRepositoryAdapter
from app.infrastructure.database.db import db


checkout_bp = Blueprint('checkout', __name__, url_prefix='/checkout')


@checkout_bp.route('/cart', methods=['GET'])
@login_required
def review_cart():
    """Step 1: Review cart before checkout"""
    try:
        cart_repo = CartRepositoryAdapter(db.session)
        use_case = ViewCartUseCase(cart_repo)
        
        output = use_case.execute(current_user.id)
        
        if not output.items:
            flash('Giỏ hàng của bạn đang trống', 'warning')
            return redirect(url_for('products.list_products'))
        
        return render_template(
            'checkout/review_cart.html',
            cart_items=output.items,
            total_amount=output.total_amount
        )
    
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
        return redirect(url_for('cart.view_cart'))


@checkout_bp.route('/shipping', methods=['GET', 'POST'])
@login_required
def shipping_info():
    """Step 2: Enter shipping information"""
    if request.method == 'GET':
        # Get cart to display summary
        cart_repo = CartRepositoryAdapter(db.session)
        use_case = ViewCartUseCase(cart_repo)
        output = use_case.execute(current_user.id)
        
        if not output.items:
            flash('Giỏ hàng của bạn đang trống', 'warning')
            return redirect(url_for('products.list_products'))
        
        # Pre-fill with user info if available
        return render_template(
            'checkout/shipping.html',
            user=current_user,
            total_amount=output.total_amount
        )
    
    # POST - Save shipping info to session
    shipping_address = request.form.get('shipping_address', '').strip()
    phone_number = request.form.get('phone_number', '').strip()
    notes = request.form.get('notes', '').strip()
    
    if not shipping_address or len(shipping_address) < 10:
        flash('Địa chỉ giao hàng phải có ít nhất 10 ký tự', 'error')
        return redirect(url_for('checkout.shipping_info'))
    
    if not phone_number or len(phone_number) < 10:
        flash('Số điện thoại phải có ít nhất 10 số', 'error')
        return redirect(url_for('checkout.shipping_info'))
    
    # Store in session
    session['shipping_address'] = shipping_address
    session['phone_number'] = phone_number
    session['notes'] = notes
    
    return redirect(url_for('checkout.payment_method'))


@checkout_bp.route('/payment', methods=['GET', 'POST'])
@login_required
def payment_method():
    """Step 3: Select payment method"""
    # Check if shipping info exists
    if 'shipping_address' not in session:
        flash('Vui lòng nhập thông tin giao hàng trước', 'warning')
        return redirect(url_for('checkout.shipping_info'))
    
    if request.method == 'GET':
        # Get cart for summary
        cart_repo = CartRepositoryAdapter(db.session)
        use_case = ViewCartUseCase(cart_repo)
        output = use_case.execute(current_user.id)
        
        return render_template(
            'checkout/payment.html',
            total_amount=output.total_amount,
            shipping_address=session.get('shipping_address'),
            phone_number=session.get('phone_number')
        )
    
    # POST - Save payment method to session
    payment_method = request.form.get('payment_method', '').strip()
    
    if not payment_method or payment_method not in ['COD', 'BANK_TRANSFER']:
        flash('Vui lòng chọn phương thức thanh toán', 'error')
        return redirect(url_for('checkout.payment_method'))
    
    session['payment_method'] = payment_method
    
    return redirect(url_for('checkout.confirm'))


@checkout_bp.route('/confirm', methods=['GET', 'POST'])
@login_required
def confirm():
    """Step 4: Confirm order and place it"""
    # Check if all info exists
    if not all(key in session for key in ['shipping_address', 'phone_number', 'payment_method']):
        flash('Vui lòng hoàn tất các bước trước', 'warning')
        return redirect(url_for('checkout.review_cart'))
    
    if request.method == 'GET':
        # Get cart for final review
        cart_repo = CartRepositoryAdapter(db.session)
        use_case = ViewCartUseCase(cart_repo)
        output = use_case.execute(current_user.id)
        
        if not output.items:
            flash('Giỏ hàng của bạn đang trống', 'warning')
            return redirect(url_for('products.list_products'))
        
        return render_template(
            'checkout/confirm.html',
            cart_items=output.items,
            total_amount=output.total_amount,
            shipping_address=session.get('shipping_address'),
            phone_number=session.get('phone_number'),
            payment_method=session.get('payment_method'),
            notes=session.get('notes', '')
        )
    
    # POST - Place order
    try:
        # Create use case
        order_repo = OrderRepositoryAdapter(db.session)
        cart_repo = CartRepositoryAdapter(db.session)
        product_repo = ProductRepositoryAdapter(db.session)
        
        use_case = PlaceOrderUseCase(order_repo, cart_repo, product_repo)
        
        # Execute
        input_data = PlaceOrderInputData(
            user_id=current_user.id,
            shipping_address=session.get('shipping_address'),
            phone_number=session.get('phone_number'),
            payment_method=session.get('payment_method'),
            notes=session.get('notes', '')
        )
        
        output = use_case.execute(input_data)
        
        # Clear session data
        session.pop('shipping_address', None)
        session.pop('phone_number', None)
        session.pop('payment_method', None)
        session.pop('notes', None)
        
        flash(output.message, 'success')
        return redirect(url_for('orders.order_success', order_id=output.order_id))
    
    except Exception as e:
        flash(f'Lỗi khi đặt hàng: {str(e)}', 'error')
        return redirect(url_for('checkout.confirm'))
