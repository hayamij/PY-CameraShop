"""Product Routes - Product listing and detail endpoints"""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user
from app.infrastructure.database import db
from app.adapters.repositories import (
    ProductRepositoryAdapter,
    CategoryRepositoryAdapter,
    BrandRepositoryAdapter
)
from app.business.use_cases import (
    ListProductsUseCase,
    ListProductsInputData,
    GetProductDetailUseCase,
    GetProductDetailInputData
)

product_bp = Blueprint('products', __name__, url_prefix='/products')


@product_bp.route('/', methods=['GET'])
def list_products():
    """Product listing page with filtering and pagination"""
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    category_id = request.args.get('category', type=int)
    brand_id = request.args.get('brand', type=int)
    search_query = request.args.get('search', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort_by = request.args.get('sort', 'newest')
    
    # Initialize repositories
    product_repo = ProductRepositoryAdapter(db.session)
    category_repo = CategoryRepositoryAdapter(db.session)
    brand_repo = BrandRepositoryAdapter(db.session)
    
    # Get all categories and brands for filter sidebar
    all_categories = category_repo.find_all()
    all_brands = brand_repo.find_all()
    
    # Create use case and execute
    use_case = ListProductsUseCase(product_repo, category_repo, brand_repo)
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
    
    output_data = use_case.execute(input_data)
    
    # Handle errors
    if not output_data.success:
        flash(output_data.error_message, 'danger')
        return redirect(url_for('products.list_products'))
    
    return render_template(
        'products/list.html',
        products=output_data.products,
        total_products=output_data.total_products,
        total_pages=output_data.total_pages,
        current_page=output_data.current_page,
        has_next=output_data.has_next,
        has_prev=output_data.has_prev,
        categories=all_categories,
        brands=all_brands,
        selected_category=category_id,
        selected_brand=brand_id,
        search_query=search_query,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        per_page=per_page
    )


@product_bp.route('/<int:product_id>', methods=['GET'])
def product_detail(product_id):
    """Product detail page"""
    # Initialize repositories
    product_repo = ProductRepositoryAdapter(db.session)
    category_repo = CategoryRepositoryAdapter(db.session)
    brand_repo = BrandRepositoryAdapter(db.session)
    
    # Create use case and execute
    use_case = GetProductDetailUseCase(product_repo, category_repo, brand_repo)
    input_data = GetProductDetailInputData(product_id=product_id)
    
    try:
        output_data = use_case.execute(input_data)
        
        if not output_data.success:
            flash(output_data.error_message, 'danger')
            return redirect(url_for('products.list_products'))
        
        return render_template(
            'products/detail.html',
            product=output_data
        )
    except Exception as e:
        flash(f'Product not found: {str(e)}', 'danger')
        return redirect(url_for('products.list_products'))
