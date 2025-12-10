"""Admin routes for product/category/brand/order management"""
from flask import Blueprint, request, jsonify, session
from app.business.use_cases.create_product_use_case import (
    CreateProductUseCase,
    CreateProductInputData
)
from app.business.use_cases.update_product_use_case import (
    UpdateProductUseCase,
    UpdateProductInputData
)
from app.business.use_cases.delete_product_use_case import (
    DeleteProductUseCase,
    DeleteProductInputData
)
from app.business.use_cases.create_category_use_case import (
    CreateCategoryUseCase,
    CreateCategoryInputData
)
from app.business.use_cases.update_category_use_case import (
    UpdateCategoryUseCase,
    UpdateCategoryInputData
)
from app.business.use_cases.delete_category_use_case import (
    DeleteCategoryUseCase,
    DeleteCategoryInputData
)
from app.business.use_cases.create_brand_use_case import (
    CreateBrandUseCase,
    CreateBrandInputData
)
from app.business.use_cases.update_brand_use_case import (
    UpdateBrandUseCase,
    UpdateBrandInputData
)
from app.business.use_cases.delete_brand_use_case import (
    DeleteBrandUseCase,
    DeleteBrandInputData
)
from app.business.use_cases.list_orders_use_case import (
    ListOrdersUseCase,
    ListOrdersInputData
)
from app.business.use_cases.update_order_status_use_case import (
    UpdateOrderStatusUseCase,
    UpdateOrderStatusInputData
)
from app.adapters.api.auth_helpers import login_required
from functools import wraps


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'ADMIN':
            return jsonify({
                'success': False,
                'error': 'Admin access required'
            }), 403
        return f(*args, **kwargs)
    return decorated_function


def create_admin_routes(
    create_product_use_case: CreateProductUseCase,
    update_product_use_case: UpdateProductUseCase,
    delete_product_use_case: DeleteProductUseCase,
    create_category_use_case: CreateCategoryUseCase,
    update_category_use_case: UpdateCategoryUseCase,
    delete_category_use_case: DeleteCategoryUseCase,
    create_brand_use_case: CreateBrandUseCase,
    update_brand_use_case: UpdateBrandUseCase,
    delete_brand_use_case: DeleteBrandUseCase,
    list_orders_use_case: ListOrdersUseCase,
    update_order_status_use_case: UpdateOrderStatusUseCase
) -> Blueprint:
    """Create admin routes blueprint"""
    
    admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')
    
    # ==================== PRODUCT MANAGEMENT ====================
    
    @admin_bp.route('/products', methods=['POST'])
    @admin_required
    def create_product():
        """Create new product"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required = ['name', 'price', 'stock_quantity', 'category_id']
            if not data or not all(field in data for field in required):
                return jsonify({
                    'success': False,
                    'error': 'Missing required fields: name, price, stock_quantity, category_id'
                }), 400
            
            # Create input data
            input_data = CreateProductInputData(
                name=data['name'],
                description=data.get('description', ''),
                price=data['price'],
                stock_quantity=data['stock_quantity'],
                category_id=data['category_id'],
                brand_id=data.get('brand_id'),
                image_url=data.get('image_url', '')
            )
            
            # Execute use case
            output_data = create_product_use_case.execute(input_data)
            
            if not output_data.success:
                return jsonify({
                    'success': False,
                    'error': output_data.message
                }), 400
            
            return jsonify({
                'success': True,
                'message': output_data.message,
                'product_id': output_data.product_id
            }), 201
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @admin_bp.route('/products/<int:product_id>', methods=['PUT'])
    @admin_required
    def update_product(product_id: int):
        """Update existing product"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            # Create input data
            input_data = UpdateProductInputData(
                product_id=product_id,
                name=data.get('name'),
                description=data.get('description'),
                price=data.get('price'),
                stock_quantity=data.get('stock_quantity'),
                category_id=data.get('category_id'),
                brand_id=data.get('brand_id'),
                image_url=data.get('image_url'),
                is_visible=data.get('is_visible')
            )
            
            # Execute use case
            output_data = update_product_use_case.execute(input_data)
            
            if not output_data.success:
                return jsonify({
                    'success': False,
                    'error': output_data.message
                }), 400
            
            return jsonify({
                'success': True,
                'message': output_data.message
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @admin_bp.route('/products/<int:product_id>', methods=['DELETE'])
    @admin_required
    def delete_product(product_id: int):
        """Delete product (soft delete)"""
        try:
            # Create input data
            input_data = DeleteProductInputData(product_id=product_id)
            
            # Execute use case
            output_data = delete_product_use_case.execute(input_data)
            
            if not output_data.success:
                return jsonify({
                    'success': False,
                    'error': output_data.message
                }), 400
            
            return jsonify({
                'success': True,
                'message': output_data.message
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # ==================== CATEGORY MANAGEMENT ====================
    
    @admin_bp.route('/categories', methods=['POST'])
    @admin_required
    def create_category():
        """Create new category"""
        try:
            data = request.get_json()
            
            if not data or 'name' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Category name is required'
                }), 400
            
            # Create input data
            input_data = CreateCategoryInputData(
                name=data['name'],
                description=data.get('description', '')
            )
            
            # Execute use case
            output_data = create_category_use_case.execute(input_data)
            
            if not output_data.success:
                return jsonify({
                    'success': False,
                    'error': output_data.message
                }), 400
            
            return jsonify({
                'success': True,
                'message': output_data.message,
                'category_id': output_data.category_id
            }), 201
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @admin_bp.route('/categories/<int:category_id>', methods=['PUT'])
    @admin_required
    def update_category(category_id: int):
        """Update existing category"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            # Create input data
            input_data = UpdateCategoryInputData(
                category_id=category_id,
                name=data.get('name'),
                description=data.get('description')
            )
            
            # Execute use case
            output_data = update_category_use_case.execute(input_data)
            
            if not output_data.success:
                return jsonify({
                    'success': False,
                    'error': output_data.message
                }), 400
            
            return jsonify({
                'success': True,
                'message': output_data.message
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @admin_bp.route('/categories/<int:category_id>', methods=['DELETE'])
    @admin_required
    def delete_category(category_id: int):
        """Delete category"""
        try:
            # Create input data
            input_data = DeleteCategoryInputData(category_id=category_id)
            
            # Execute use case
            output_data = delete_category_use_case.execute(input_data)
            
            if not output_data.success:
                return jsonify({
                    'success': False,
                    'error': output_data.message
                }), 400
            
            return jsonify({
                'success': True,
                'message': output_data.message
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # ==================== BRAND MANAGEMENT ====================
    
    @admin_bp.route('/brands', methods=['POST'])
    @admin_required
    def create_brand():
        """Create new brand"""
        try:
            data = request.get_json()
            
            if not data or 'name' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Brand name is required'
                }), 400
            
            # Create input data
            input_data = CreateBrandInputData(
                name=data['name'],
                description=data.get('description', '')
            )
            
            # Execute use case
            output_data = create_brand_use_case.execute(input_data)
            
            if not output_data.success:
                return jsonify({
                    'success': False,
                    'error': output_data.message
                }), 400
            
            return jsonify({
                'success': True,
                'message': output_data.message,
                'brand_id': output_data.brand_id
            }), 201
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @admin_bp.route('/brands/<int:brand_id>', methods=['PUT'])
    @admin_required
    def update_brand(brand_id: int):
        """Update existing brand"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            # Create input data
            input_data = UpdateBrandInputData(
                brand_id=brand_id,
                name=data.get('name'),
                description=data.get('description')
            )
            
            # Execute use case
            output_data = update_brand_use_case.execute(input_data)
            
            if not output_data.success:
                return jsonify({
                    'success': False,
                    'error': output_data.message
                }), 400
            
            return jsonify({
                'success': True,
                'message': output_data.message
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @admin_bp.route('/brands/<int:brand_id>', methods=['DELETE'])
    @admin_required
    def delete_brand(brand_id: int):
        """Delete brand"""
        try:
            # Create input data
            input_data = DeleteBrandInputData(brand_id=brand_id)
            
            # Execute use case
            output_data = delete_brand_use_case.execute(input_data)
            
            if not output_data.success:
                return jsonify({
                    'success': False,
                    'error': output_data.message
                }), 400
            
            return jsonify({
                'success': True,
                'message': output_data.message
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # ==================== ORDER MANAGEMENT ====================
    
    @admin_bp.route('/orders', methods=['GET'])
    @admin_required
    def list_orders():
        """List all orders with filters (admin view)"""
        try:
            # Get query parameters
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            status = request.args.get('status')
            customer_id = request.args.get('customer_id', type=int)
            
            # Create input data
            input_data = ListOrdersInputData(
                page=page,
                per_page=per_page,
                status=status,
                customer_id=customer_id
            )
            
            # Execute use case
            output_data = list_orders_use_case.execute(input_data)
            
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
                        'order_id': o.order_id,
                        'customer_id': o.customer_id,
                        'customer_name': o.customer_name,
                        'total_amount': o.total_amount,
                        'order_status': o.status,  # Fixed: Use 'status' not 'order_status'
                        'payment_method': o.payment_method,
                        'created_at': o.order_date.isoformat() if o.order_date else None,  # Fixed: Use 'order_date' not 'created_at'
                        'item_count': o.item_count
                    }
                    for o in output_data.orders
                ],
                'total_orders': output_data.total_orders,
                'total_pages': output_data.total_pages,
                'current_page': output_data.page,  # Fixed: Use 'page' not 'current_page'
                'statistics': {  # Fixed: Build statistics object from individual properties
                    'total_revenue': output_data.total_revenue,
                    'pending_count': output_data.pending_count,
                    'shipping_count': output_data.shipping_count,
                    'completed_count': output_data.completed_count,
                    'cancelled_count': output_data.cancelled_count
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @admin_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
    @admin_required
    def update_order_status(order_id: int):
        """Update order status"""
        try:
            data = request.get_json()
            
            if not data or 'new_status' not in data:
                return jsonify({
                    'success': False,
                    'error': 'New status is required'
                }), 400
            
            # Create input data
            input_data = UpdateOrderStatusInputData(
                order_id=order_id,
                new_status=data['new_status']
            )
            
            # Execute use case
            output_data = update_order_status_use_case.execute(input_data)
            
            if not output_data.success:
                return jsonify({
                    'success': False,
                    'error': output_data.message
                }), 400
            
            return jsonify({
                'success': True,
                'message': output_data.message
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    return admin_bp
