"""Order routes"""
from flask import Blueprint, request, jsonify, session
from app.business.use_cases.place_order_use_case import (
    PlaceOrderUseCase,
    PlaceOrderInputData
)
from app.business.use_cases.get_my_orders_use_case import (
    GetMyOrdersUseCase,
    GetMyOrdersInputData
)
from app.business.use_cases.get_order_detail_use_case import GetOrderDetailUseCase
from app.business.use_cases.cancel_order_use_case import (
    CancelOrderUseCase,
    CancelOrderInputData
)
from app.adapters.api.auth_helpers import login_required
from app.domain.exceptions import ValidationException, OrderNotFoundException


def create_order_routes(
    place_order_use_case: PlaceOrderUseCase,
    get_my_orders_use_case: GetMyOrdersUseCase,
    get_order_detail_use_case: GetOrderDetailUseCase,
    cancel_order_use_case: CancelOrderUseCase
) -> Blueprint:
    """Create order routes blueprint"""
    
    order_bp = Blueprint('orders', __name__, url_prefix='/api/orders')
    
    @order_bp.route('', methods=['POST'])
    @login_required
    def place_order():
        """Place a new order from cart"""
        try:
            user_id = session.get('user_id')
            data = request.get_json(silent=True)  # Use silent=True to avoid 415 errors
            
            # Validate required fields
            if not data or 'shipping_address' not in data or 'phone_number' not in data or 'payment_method' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Shipping address, phone number, and payment method are required'
                }), 400
            
            # Create input data
            input_data = PlaceOrderInputData(
                user_id=user_id,
                shipping_address=data['shipping_address'],
                phone_number=data['phone_number'],
                payment_method=data['payment_method'],
                notes=data.get('notes', '')
            )
            
            # Execute use case
            output_data = place_order_use_case.execute(input_data)
            
            if not output_data.success:
                return jsonify({
                    'success': False,
                    'error': output_data.error_message
                }), 400
            
            # Convert to response
            return jsonify({
                'success': True,
                'message': output_data.message,
                'order_id': output_data.order_id,
                'total_amount': output_data.total_amount
            }), 201
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @order_bp.route('/my-orders', methods=['GET'])
    @login_required
    def get_my_orders():
        """Get user's orders"""
        try:
            user_id = session.get('user_id')
            status_filter = request.args.get('status', None)
            
            # Create input data
            input_data = GetMyOrdersInputData(
                user_id=user_id,
                status_filter=status_filter
            )
            
            # Execute use case
            output_data = get_my_orders_use_case.execute(input_data)
            
            if not output_data.success:
                return jsonify({
                    'success': False,
                    'error': output_data.message
                }), 400
            
            # Convert to response
            return jsonify({
                'success': True,
                'orders': [
                    {
                        'order_id': order.order_id,
                        'total_amount': order.total_amount,
                        'status': order.status,
                        'payment_method': order.payment_method,
                        'shipping_address': order.shipping_address,
                        'phone_number': order.phone_number,
                        'notes': order.notes,
                        'created_at': order.created_at,
                        'item_count': order.item_count
                    }
                    for order in output_data.orders
                ],
                'total_orders': output_data.total_orders
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @order_bp.route('/<int:order_id>', methods=['GET'])
    @login_required
    def get_order_detail(order_id: int):
        """Get order detail by ID"""
        try:
            user_id = session.get('user_id')
            
            # Execute use case (only needs order_id)
            output_data = get_order_detail_use_case.execute(order_id)
            
            if not output_data.success:
                return jsonify({
                    'success': False,
                    'error': output_data.message
                }), 400
            
            # Convert to response
            return jsonify({
                'success': True,
                'order': {
                    'order_id': output_data.order_id,
                    'order_date': output_data.order_date.isoformat() if output_data.order_date else None,
                    'status': output_data.status,
                    'customer_id': output_data.customer_id,
                    'customer_name': output_data.customer_name,
                    'customer_email': output_data.customer_email,
                    'customer_phone': output_data.customer_phone,
                    'shipping_address': output_data.shipping_address,
                    'payment_method': output_data.payment_method,
                    'items': [
                        {
                            'product_id': item.product_id,
                            'product_name': item.product_name,
                            'product_image': item.product_image,
                            'quantity': item.quantity,
                            'unit_price': item.unit_price,
                            'subtotal': item.subtotal
                        }
                        for item in output_data.items
                    ],
                    'subtotal': output_data.subtotal,
                    'tax': output_data.tax,
                    'shipping_fee': output_data.shipping_fee,
                    'total_amount': output_data.total_amount
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @order_bp.route('/<int:order_id>/cancel', methods=['POST'])
    @login_required
    def cancel_order(order_id: int):
        """Cancel an order"""
        try:
            user_id = session.get('user_id')
            
            # Create input data
            input_data = CancelOrderInputData(
                order_id=order_id,
                user_id=user_id
            )
            
            # Execute use case
            output_data = cancel_order_use_case.execute(input_data)
            
            if not output_data.success:
                return jsonify({
                    'success': False,
                    'error': output_data.message
                }), 400
            
            # Convert to response
            return jsonify({
                'success': True,
                'message': output_data.message,
                'order_id': output_data.order_id,
                'order_status': output_data.order_status
            }), 200
            
        except (ValidationException, OrderNotFoundException) as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    return order_bp
