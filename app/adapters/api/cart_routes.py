"""Cart Routes - Shopping cart operations"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.infrastructure.database import db
from app.adapters.repositories import (
    CartRepositoryAdapter,
    ProductRepositoryAdapter
)
from app.business.use_cases import (
    AddToCartUseCase,
    AddToCartInputData,
    ViewCartUseCase,
    UpdateCartItemUseCase,
    UpdateCartItemInputData,
    RemoveCartItemUseCase,
    RemoveCartItemInputData
)

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')


@cart_bp.route('/', methods=['GET'])
@login_required
def view_cart():
    """View shopping cart"""
    # Initialize repositories
    cart_repo = CartRepositoryAdapter(db.session)
    product_repo = ProductRepositoryAdapter(db.session)
    
    # Create use case and execute
    use_case = ViewCartUseCase(cart_repo, product_repo)
    output_data = use_case.execute(current_user.id)
    
    if not output_data.success:
        flash(output_data.error_message, 'danger')
    
    return render_template(
        'cart/view.html',
        cart=output_data
    )


@cart_bp.route('/add', methods=['POST'])
@login_required
def add_to_cart():
    """Add item to cart"""
    # Get form data
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', type=int, default=1)
    
    # Initialize repositories
    cart_repo = CartRepositoryAdapter(db.session)
    product_repo = ProductRepositoryAdapter(db.session)
    
    # Create use case and execute
    use_case = AddToCartUseCase(cart_repo, product_repo)
    input_data = AddToCartInputData(
        user_id=current_user.id,
        product_id=product_id,
        quantity=quantity
    )
    
    output_data = use_case.execute(input_data)
    
    # Handle AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if output_data.success:
            return jsonify({
                'success': True,
                'message': output_data.message,
                'cart_count': output_data.total_items
            })
        else:
            return jsonify({
                'success': False,
                'message': output_data.error_message
            }), 400
    
    # Handle regular form submission
    if output_data.success:
        flash(output_data.message, 'success')
    else:
        flash(output_data.error_message, 'danger')
    
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/update/<int:cart_item_id>', methods=['POST'])
@login_required
def update_cart_item(cart_item_id):
    """Update cart item quantity"""
    new_quantity = request.form.get('quantity', type=int)
    
    # Initialize repositories
    cart_repo = CartRepositoryAdapter(db.session)
    product_repo = ProductRepositoryAdapter(db.session)
    
    # Create use case and execute
    use_case = UpdateCartItemUseCase(cart_repo, product_repo)
    input_data = UpdateCartItemInputData(
        user_id=current_user.id,
        cart_item_id=cart_item_id,
        new_quantity=new_quantity
    )
    
    output_data = use_case.execute(input_data)
    
    # Handle AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if output_data.success:
            return jsonify({
                'success': True,
                'message': output_data.message
            })
        else:
            return jsonify({
                'success': False,
                'message': output_data.error_message
            }), 400
    
    # Handle regular form submission
    if output_data.success:
        flash(output_data.message, 'success')
    else:
        flash(output_data.error_message, 'danger')
    
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/remove/<int:cart_item_id>', methods=['POST'])
@login_required
def remove_cart_item(cart_item_id):
    """Remove item from cart"""
    # Initialize repository
    cart_repo = CartRepositoryAdapter(db.session)
    
    # Create use case and execute
    use_case = RemoveCartItemUseCase(cart_repo)
    input_data = RemoveCartItemInputData(
        user_id=current_user.id,
        cart_item_id=cart_item_id
    )
    
    output_data = use_case.execute(input_data)
    
    # Handle AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if output_data.success:
            return jsonify({
                'success': True,
                'message': output_data.message
            })
        else:
            return jsonify({
                'success': False,
                'message': output_data.error_message
            }), 400
    
    # Handle regular form submission
    if output_data.success:
        flash(output_data.message, 'success')
    else:
        flash(output_data.error_message, 'danger')
    
    return redirect(url_for('cart.view_cart'))
