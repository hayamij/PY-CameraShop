"""Catalog routes - Categories and Brands"""
from flask import Blueprint, jsonify
from app.business.ports.category_repository import ICategoryRepository
from app.business.ports.brand_repository import IBrandRepository


def create_catalog_routes(
    category_repository: ICategoryRepository,
    brand_repository: IBrandRepository
) -> Blueprint:
    """Create catalog routes blueprint"""
    
    catalog_bp = Blueprint('catalog', __name__, url_prefix='/api/catalog')
    
    @catalog_bp.route('/categories', methods=['GET'])
    def list_categories():
        """Get all active categories"""
        try:
            categories = category_repository.find_all(active_only=True)
            
            return jsonify({
                'success': True,
                'categories': [
                    {
                        'category_id': cat.id,
                        'name': cat.name,
                        'description': cat.description
                    }
                    for cat in categories
                ]
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @catalog_bp.route('/brands', methods=['GET'])
    def list_brands():
        """Get all active brands"""
        try:
            brands = brand_repository.find_all(active_only=True)
            
            return jsonify({
                'success': True,
                'brands': [
                    {
                        'brand_id': brand.id,
                        'name': brand.name,
                        'description': brand.description
                    }
                    for brand in brands
                ]
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    return catalog_bp
