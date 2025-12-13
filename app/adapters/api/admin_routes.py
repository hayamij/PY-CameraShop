"""Admin routes for product/category/brand/order management"""
from flask import Blueprint, request, jsonify, session
from app.domain.exceptions import (
    ValidationException,
    CategoryNotFoundException,
    CategoryAlreadyExistsException,
    BrandNotFoundException,
    BrandAlreadyExistsException
)
from app.business.use_cases.list_users_use_case import (
    ListUsersUseCase,
    ListUsersInputData
)
from app.business.use_cases.search_users_use_case import (
    SearchUsersUseCase,
    SearchUsersInputData
)
from app.business.use_cases.create_user_by_admin_use_case import (
    CreateUserByAdminUseCase,
    CreateUserInputData
)
from app.business.use_cases.update_user_by_admin_use_case import (
    UpdateUserByAdminUseCase,
    UpdateUserInputData
)
from app.business.use_cases.delete_user_use_case import (
    DeleteUserUseCase,
    DeleteUserInputData
)
from app.business.use_cases.change_user_role_use_case import (
    ChangeUserRoleUseCase,
    ChangeUserRoleInputData
)
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
from app.business.use_cases.create_order_by_admin_use_case import (
    CreateOrderByAdminUseCase,
    CreateOrderByAdminInputData,
    OrderItemInput
)
from app.business.use_cases.delete_order_use_case import (
    DeleteOrderUseCase,
    DeleteOrderInputData
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
    list_users_use_case: ListUsersUseCase,
    search_users_use_case: SearchUsersUseCase,
    create_user_use_case: CreateUserByAdminUseCase,
    update_user_use_case: UpdateUserByAdminUseCase,
    delete_user_use_case: DeleteUserUseCase,
    change_user_role_use_case: ChangeUserRoleUseCase,
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
    update_order_status_use_case: UpdateOrderStatusUseCase,
    create_order_by_admin_use_case: CreateOrderByAdminUseCase,
    delete_order_use_case: DeleteOrderUseCase
) -> Blueprint:
    """Create admin routes blueprint"""
    
    admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')
    
    # ==================== USER MANAGEMENT ====================
    
    @admin_bp.route('/users', methods=['GET'])
    @admin_required
    def list_users():
        """List all users with filters, pagination, and search"""
        try:
            # Extract query parameters
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            role_filter = request.args.get('role', type=str)
            active_filter = request.args.get('active', type=str)
            search_query = request.args.get('search', '', type=str)
            sort_by = request.args.get('sort_by', 'newest', type=str)  # Use valid default: newest, oldest, name_asc, name_desc
            
            # Convert active_filter string to boolean
            active_bool = None
            if active_filter:
                active_bool = active_filter.lower() in ('true', '1', 'yes')
            
            # Create input data
            input_data = ListUsersInputData(
                page=page,
                per_page=per_page,
                role_filter=role_filter,
                active_filter=active_bool,
                search_query=search_query,
                sort_by=sort_by
            )
            
            # Execute use case
            output_data = list_users_use_case.execute(input_data)
            
            if not output_data.success:
                return jsonify({
                    'success': False,
                    'error': output_data.error_message
                }), 400
            
            # Convert users to dict format
            users_dict = [
                {
                    'user_id': user.user_id,
                    'username': user.username,
                    'email': str(user.email),  # Convert Email value object to string
                    'full_name': user.full_name,
                    'phone_number': user.phone_number,
                    'address': user.address,
                    'role': user.role,
                    'is_active': user.is_active,
                    'created_at': user.created_at.isoformat() if user.created_at else None
                }
                for user in output_data.users
            ]
            
            return jsonify({
                'success': True,
                'data': {
                    'users': users_dict,
                    'pagination': {
                        'total_users': output_data.total_users,
                        'total_pages': output_data.total_pages,
                        'current_page': output_data.current_page,
                        'per_page': per_page
                    },
                    'statistics': {
                        'total_admins': output_data.total_admins,
                        'total_customers': output_data.total_customers,
                        'active_users': output_data.active_users,
                        'inactive_users': output_data.inactive_users
                    }
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @admin_bp.route('/users/search', methods=['GET'])
    @admin_required
    def search_users():
        """Search users by query string"""
        try:
            # Extract query parameter
            search_query = request.args.get('q', '', type=str)
            
            # Validate query
            if not search_query or len(search_query.strip()) < 2:
                return jsonify({
                    'success': False,
                    'error': 'Search query must be at least 2 characters'
                }), 400
            
            # Create input data
            input_data = SearchUsersInputData(search_query=search_query)
            
            # Execute use case
            output_data = search_users_use_case.execute(input_data)
            
            if not output_data.success:
                return jsonify({
                    'success': False,
                    'error': output_data.error_message
                }), 400
            
            # Convert results to dict format
            results_dict = [
                {
                    'user_id': result.user_id,
                    'username': result.username,
                    'email': result.email,
                    'full_name': result.full_name,
                    'role': result.role,
                    'is_active': result.is_active,
                    'phone_number': result.phone_number,
                    'address': result.address
                }
                for result in output_data.results
            ]
            
            return jsonify({
                'success': True,
                'data': {
                    'results': results_dict,
                    'total_results': output_data.total_results,
                    'search_query': output_data.search_query
                }
            }), 200
            
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @admin_bp.route('/users', methods=['POST'])
    @admin_required
    def create_user():
        """Create new user by admin"""
        try:
            # Get JSON data
            data = request.get_json()
            
            # Validate required fields
            required = ['username', 'email', 'password', 'full_name', 'role']
            if not data or not all(field in data for field in required):
                return jsonify({
                    'success': False,
                    'error': 'Missing required fields: username, email, password, full_name, role'
                }), 400
            
            # Create input data
            input_data = CreateUserInputData(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                full_name=data['full_name'],
                phone_number=data.get('phone_number'),
                address=data.get('address'),
                role=data['role']
            )
            
            # Execute use case
            output_data = create_user_use_case.execute(input_data)
            
            if not output_data.success:
                return jsonify({
                    'success': False,
                    'error': output_data.error_message
                }), 400
            
            return jsonify({
                'success': True,
                'data': {
                    'user_id': output_data.user_id,
                    'username': output_data.username
                },
                'message': output_data.message
            }), 201
            
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @admin_bp.route('/users/<int:user_id>', methods=['PUT'])
    @admin_required
    def update_user(user_id):
        """Update user by admin"""
        try:
            # Get admin user ID from session
            admin_user_id = session.get('user_id')
            if not admin_user_id:
                return jsonify({
                    'success': False,
                    'error': 'Authentication required'
                }), 401
            
            # Get JSON data
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            # Create input data (all fields optional except IDs)
            input_data = UpdateUserInputData(
                user_id=user_id,
                admin_user_id=admin_user_id,
                username=data.get('username'),
                email=data.get('email'),
                full_name=data.get('full_name'),
                phone_number=data.get('phone_number'),
                address=data.get('address'),
                role=data.get('role'),
                is_active=data.get('is_active')
            )
            
            # Execute use case
            output_data = update_user_use_case.execute(input_data)
            
            if not output_data.success:
                return jsonify({
                    'success': False,
                    'error': output_data.message
                }), 400
            
            return jsonify({
                'success': True,
                'data': {
                    'user_id': output_data.user_id,
                    'username': output_data.username
                },
                'message': output_data.message
            }), 200
            
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
    @admin_required
    def delete_user(user_id):
        """Delete user (soft delete) by admin"""
        try:
            # Get admin user ID from session
            admin_user_id = session.get('user_id')
            if not admin_user_id:
                return jsonify({
                    'success': False,
                    'error': 'Authentication required'
                }), 401
            
            # Create input data
            input_data = DeleteUserInputData(
                user_id=user_id,
                admin_user_id=admin_user_id
            )
            
            # Execute use case
            output_data = delete_user_use_case.execute(input_data)
            
            if not output_data.success:
                return jsonify({
                    'success': False,
                    'error': output_data.message
                }), 400
            
            return jsonify({
                'success': True,
                'data': {
                    'user_id': output_data.user_id
                },
                'message': output_data.message
            }), 200
            
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @admin_bp.route('/users/<int:user_id>/role', methods=['PUT'])
    @admin_required
    def change_user_role(user_id):
        """Change user role (promote/demote) by admin"""
        try:
            # Get admin user ID from session
            admin_user_id = session.get('user_id')
            if not admin_user_id:
                return jsonify({
                    'success': False,
                    'error': 'Authentication required'
                }), 401
            
            # Get JSON data
            data = request.get_json()
            if not data or 'new_role' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Missing required field: new_role'
                }), 400
            
            # Create input data
            input_data = ChangeUserRoleInputData(
                user_id=user_id,
                new_role=data['new_role'],
                admin_user_id=admin_user_id
            )
            
            # Execute use case
            output_data = change_user_role_use_case.execute(input_data)
            
            if not output_data.success:
                return jsonify({
                    'success': False,
                    'error': output_data.message
                }), 400
            
            return jsonify({
                'success': True,
                'data': {
                    'user_id': output_data.user_id,
                    'old_role': output_data.old_role,
                    'new_role': output_data.new_role
                },
                'message': output_data.message
            }), 200
            
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
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
            
        except (CategoryNotFoundException, ValidationException, CategoryAlreadyExistsException) as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400
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
            
        except (BrandNotFoundException, ValidationException, BrandAlreadyExistsException) as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400
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
                        'customer_email': str(o.customer_email) if o.customer_email else None,
                        'total_amount': o.total_amount,
                        'status': o.status,
                        'payment_method': o.payment_method,
                        'order_date': o.order_date.isoformat() if o.order_date else None,
                        'item_count': o.item_count
                    }
                    for o in output_data.orders
                ],
                'total_orders': output_data.total_orders,
                'total_pages': output_data.total_pages,
                'page': output_data.page,
                'per_page': output_data.per_page,
                'statistics': {
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
    
    @admin_bp.route('/orders', methods=['POST'])
    @admin_required
    def create_order():
        """Create a new order (admin)"""
        try:
            data = request.get_json()
            
            # Validate required fields (user_id is optional)
            required_fields = ['customer_email', 'customer_phone', 'shipping_address', 'payment_method', 'items']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'success': False,
                        'error': f'{field} is required'
                    }), 400
            
            # Parse items
            items = []
            for item in data['items']:
                items.append(OrderItemInput(
                    product_id=item['product_id'],
                    quantity=item['quantity'],
                    unit_price=item['unit_price']
                ))
            
            # Create input data
            input_data = CreateOrderByAdminInputData(
                customer_email=data['customer_email'],
                customer_phone=data['customer_phone'],
                shipping_address=data['shipping_address'],
                payment_method=data['payment_method'],
                items=items,
                notes=data.get('notes', ''),
                user_id=data.get('user_id')  # Optional
            )
            
            # Execute use case
            output_data = create_order_by_admin_use_case.execute(input_data)
            
            if not output_data.success:
                return jsonify({
                    'success': False,
                    'error': output_data.message
                }), 400
            
            return jsonify({
                'success': True,
                'order_id': output_data.order_id,
                'message': output_data.message
            }), 201
            
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
    
    @admin_bp.route('/orders/<int:order_id>', methods=['DELETE'])
    @admin_required
    def delete_order(order_id: int):
        """Delete an order (admin)"""
        try:
            # Create input data
            input_data = DeleteOrderInputData(order_id=order_id)
            
            # Execute use case
            output_data = delete_order_use_case.execute(input_data)
            
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
