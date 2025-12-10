"""Product routes"""
from flask import Blueprint, request, jsonify
from app.business.use_cases.list_products_use_case import (
    ListProductsUseCase,
    ListProductsInputData
)
from app.business.use_cases.get_product_detail_use_case import (
    GetProductDetailUseCase,
    GetProductDetailInputData
)
from app.domain.exceptions import ProductNotFoundException


def create_product_routes(
    list_products_use_case: ListProductsUseCase,
    get_product_detail_use_case: GetProductDetailUseCase
) -> Blueprint:
    """Create product routes blueprint"""
    
    product_bp = Blueprint('products', __name__, url_prefix='/api/products')
    
    @product_bp.route('', methods=['GET'])
    def list_products():
        """List products with filters and pagination"""
        try:
            # Get query parameters
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 12, type=int)
            category_id = request.args.get('category_id', type=int)
            brand_id = request.args.get('brand_id', type=int)
            search_query = request.args.get('search_query', type=str)
            min_price = request.args.get('min_price', type=float)
            max_price = request.args.get('max_price', type=float)
            sort_by = request.args.get('sort_by', 'newest', type=str)
            
            # Create input data
            input_data = ListProductsInputData(
                page=page,
                per_page=per_page,
                category_id=category_id,
                brand_id=brand_id,
                search_query=search_query,
                min_price=min_price,
                max_price=max_price,
                sort_by=sort_by
            )
            
            # Execute use case
            output_data = list_products_use_case.execute(input_data)
            
            if not output_data.success:
                return jsonify({
                    'success': False,
                    'error': output_data.error_message
                }), 400
            
            # Convert to response
            return jsonify({
                'success': True,
                'products': [
                    {
                        'product_id': p.product_id,
                        'name': p.name,
                        'description': p.description,
                        'price': p.price,
                        'currency': p.currency,
                        'stock_quantity': p.stock_quantity,
                        'category_name': p.category_name,
                        'brand_name': p.brand_name,
                        'image_url': p.image_url,
                        'is_available': p.is_available
                    }
                    for p in output_data.products
                ],
                'total_products': output_data.total_products,
                'total_pages': output_data.total_pages,
                'current_page': output_data.current_page,
                'has_next': output_data.has_next,
                'has_prev': output_data.has_prev
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @product_bp.route('/<int:product_id>', methods=['GET'])
    def get_product_detail(product_id: int):
        """Get product detail by ID"""
        try:
            # Create input data
            input_data = GetProductDetailInputData(product_id=product_id)
            
            # Execute use case
            output_data = get_product_detail_use_case.execute(input_data)
            
            if not output_data.success:
                if 'not found' in output_data.error_message.lower():
                    return jsonify({
                        'success': False,
                        'error': output_data.error_message
                    }), 404
                return jsonify({
                    'success': False,
                    'error': output_data.error_message
                }), 400
            
            # Convert to response
            return jsonify({
                'success': True,
                'product': {
                    'product_id': output_data.product_id,
                    'name': output_data.name,
                    'description': output_data.description,
                    'price': output_data.price,
                    'currency': output_data.currency,
                    'stock_quantity': output_data.stock_quantity,
                    'category_id': output_data.category_id,
                    'category_name': output_data.category_name,
                    'brand_id': output_data.brand_id,
                    'brand_name': output_data.brand_name,
                    'image_url': output_data.image_url,
                    'is_available': output_data.is_available
                    # NOTE: warranty_period and specifications removed - not in Product entity
                }
            }), 200
            
        except ProductNotFoundException as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 404
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    return product_bp
