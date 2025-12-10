"""Cart routes"""
from flask import Blueprint, request, jsonify, session
from app.business.use_cases.view_cart_use_case import ViewCartUseCase
from app.business.use_cases.add_to_cart_use_case import (
    AddToCartUseCase,
    AddToCartInputData
)
from app.business.use_cases.update_cart_item_use_case import (
    UpdateCartItemUseCase,
    UpdateCartItemInputData
)
from app.business.use_cases.remove_cart_item_use_case import (
    RemoveCartItemUseCase,
    RemoveCartItemInputData
)
from app.adapters.api.auth_helpers import login_required


def create_cart_routes(
    view_cart_use_case: ViewCartUseCase,
    add_to_cart_use_case: AddToCartUseCase,
    update_cart_item_use_case: UpdateCartItemUseCase,
    remove_cart_item_use_case: RemoveCartItemUseCase
) -> Blueprint:
    """Create cart routes blueprint"""
    
    cart_bp = Blueprint('cart', __name__, url_prefix='/api/cart')
    
    @cart_bp.route('', methods=['GET'])
    @login_required
    def view_cart():
        """View user's cart"""
        try:
            user_id = session.get('user_id')
            
            # Execute use case
            output_data = view_cart_use_case.execute(user_id)
            
            if not output_data.success:
                return jsonify({
                    'success': False,
                    'error': output_data.error_message
                }), 400
            
            # Convert to response
            return jsonify({
                'success': True,
                'cart': {
                    'cart_id': output_data.cart_id,
                    'items': [
                        {
                            'cart_item_id': item.cart_item_id,
                            'product_id': item.product_id,
                            'product_name': item.product_name,
                            'product_image': item.product_image,
                            'price': float(item.price),
                            'currency': item.currency,
                            'quantity': item.quantity,
                            'subtotal': float(item.subtotal),
                            'stock_available': item.stock_available,
                            'is_available': item.is_available
                        }
                        for item in output_data.items
                    ],
                    'total_items': output_data.total_items,
                    'subtotal': float(output_data.subtotal),
                    'tax': float(output_data.tax),
                    'shipping': float(output_data.shipping),
                    'total': float(output_data.total)
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @cart_bp.route('/add', methods=['POST'])
    @login_required
    def add_to_cart():
        """Add item to cart"""
        try:
            user_id = session.get('user_id')
            data = request.get_json()
            
            # Validate required fields
            if not data or 'product_id' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Product ID is required'
                }), 400
            
            # Create input data
            input_data = AddToCartInputData(
                user_id=user_id,
                product_id=data['product_id'],
                quantity=data.get('quantity', 1)
            )
            
            # Execute use case
            output_data = add_to_cart_use_case.execute(input_data)
            
            if not output_data.success:
                return jsonify({
                    'success': False,
                    'error': output_data.error_message
                }), 400
            
            # Convert to response
            return jsonify({
                'success': True,
                'message': output_data.message,
                'cart_id': output_data.cart_id,
                'cart_item_id': output_data.cart_item_id,
                'total_items': output_data.total_items,
                'cart_total': output_data.cart_total
            }), 201
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @cart_bp.route('/items/<int:cart_item_id>', methods=['PUT'])
    @login_required
    def update_cart_item(cart_item_id: int):
        """Update cart item quantity"""
        try:
            user_id = session.get('user_id')
            data = request.get_json()
            
            # Validate required fields
            if not data or 'quantity' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Quantity is required'
                }), 400
            
            # Create input data
            input_data = UpdateCartItemInputData(
                user_id=user_id,
                cart_item_id=cart_item_id,
                new_quantity=data['quantity']
            )
            
            # Execute use case
            output_data = update_cart_item_use_case.execute(input_data)
            
            if not output_data.success:
                return jsonify({
                    'success': False,
                    'error': output_data.error_message
                }), 400
            
            # Convert to response
            return jsonify({
                'success': True,
                'message': output_data.message,
                'cart_item_id': output_data.cart_item_id,
                'new_quantity': output_data.new_quantity
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @cart_bp.route('/items/<int:cart_item_id>', methods=['DELETE'])
    @login_required
    def remove_cart_item(cart_item_id: int):
        """Remove item from cart"""
        try:
            user_id = session.get('user_id')
            
            # Create input data
            input_data = RemoveCartItemInputData(
                user_id=user_id,
                cart_item_id=cart_item_id
            )
            
            # Execute use case
            output_data = remove_cart_item_use_case.execute(input_data)
            
            if not output_data.success:
                return jsonify({
                    'success': False,
                    'error': output_data.error_message
                }), 400
            
            # Convert to response
            return jsonify({
                'success': True,
                'message': output_data.message
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    return cart_bp
