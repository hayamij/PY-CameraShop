"""
Admin Product Routes - Product management CRUD operations
Clean Architecture - Adapters Layer
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps

from app.adapters.repositories.product_repository_adapter import ProductRepositoryAdapter
from app.adapters.repositories.category_repository_adapter import CategoryRepositoryAdapter
from app.adapters.repositories.brand_repository_adapter import BrandRepositoryAdapter
from app.business.use_cases import (
    ListProductsUseCase, ListProductsInputData,
    GetProductDetailUseCase, GetProductDetailInputData,
    CreateProductUseCase, CreateProductInputData,
    UpdateProductUseCase, UpdateProductInputData,
    DeleteProductUseCase, DeleteProductInputData,
    ToggleProductVisibilityUseCase
)
from app.infrastructure.database import db


admin_products_bp = Blueprint('admin_products', __name__, url_prefix='/admin/products')


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash('Bạn không có quyền truy cập trang này', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_products_bp.route('/')
@admin_required
def list_products():
    """List all products for admin management"""
    try:
        # Get filter parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        category_id = request.args.get('category_id', type=int)
        brand_id = request.args.get('brand_id', type=int)
        search_query = request.args.get('search', '').strip()
        sort_by = request.args.get('sort', 'newest')
        show_hidden = request.args.get('show_hidden', 'false') == 'true'
        
        # Initialize repositories
        product_repo = ProductRepositoryAdapter(db.session)
        category_repo = CategoryRepositoryAdapter(db.session)
        brand_repo = BrandRepositoryAdapter(db.session)
        
        # Execute use case
        use_case = ListProductsUseCase(product_repo)
        input_data = ListProductsInputData(
            page=page,
            per_page=per_page,
            category_id=category_id,
            brand_id=brand_id,
            min_price=None,
            max_price=None,
            search_query=search_query,
            sort_by=sort_by,
            include_hidden=show_hidden  # Admin can see hidden products
        )
        
        output = use_case.execute(input_data)
        
        # Get all categories and brands for filters
        categories = category_repo.find_all()
        brands = brand_repo.find_all()
        
        return render_template('admin/products/list.html',
                             output=output,
                             categories=categories,
                             brands=brands,
                             show_hidden=show_hidden)
        
    except Exception as e:
        flash(f'Lỗi tải danh sách sản phẩm: {str(e)}', 'danger')
        return render_template('admin/products/list.html',
                             output=None,
                             categories=[],
                             brands=[])


@admin_products_bp.route('/create', methods=['GET', 'POST'])
@admin_required
def create_product():
    """Create new product"""
    category_repo = CategoryRepositoryAdapter(db.session)
    brand_repo = BrandRepositoryAdapter(db.session)
    
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            price = float(request.form.get('price', 0))
            stock_quantity = int(request.form.get('stock_quantity', 0))
            category_id = int(request.form.get('category_id', 0))
            brand_id = int(request.form.get('brand_id', 0))
            image_url = request.form.get('image_url', '').strip()
            is_visible = request.form.get('is_visible') == 'on'
            
            # Initialize repositories
            product_repo = ProductRepositoryAdapter(db.session)
            
            # Execute use case
            use_case = CreateProductUseCase(product_repo, category_repo, brand_repo)
            input_data = CreateProductInputData(
                name=name,
                description=description,
                price=price,
                stock_quantity=stock_quantity,
                category_id=category_id,
                brand_id=brand_id,
                image_url=image_url if image_url else None,
                is_visible=is_visible
            )
            
            output = use_case.execute(input_data)
            
            if output.success:
                flash(output.message, 'success')
                return redirect(url_for('admin_products.list_products'))
            else:
                flash(output.message, 'danger')
                
        except ValueError as e:
            flash(f'Dữ liệu không hợp lệ: {str(e)}', 'danger')
        except Exception as e:
            flash(f'Lỗi tạo sản phẩm: {str(e)}', 'danger')
    
    # GET request - show form
    categories = category_repo.find_all()
    brands = brand_repo.find_all()
    
    return render_template('admin/products/create.html',
                         categories=categories,
                         brands=brands)


@admin_products_bp.route('/<int:product_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    """Edit existing product"""
    product_repo = ProductRepositoryAdapter(db.session)
    category_repo = CategoryRepositoryAdapter(db.session)
    brand_repo = BrandRepositoryAdapter(db.session)
    
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            price = float(request.form.get('price', 0))
            stock_quantity = int(request.form.get('stock_quantity', 0))
            category_id = int(request.form.get('category_id', 0))
            brand_id = int(request.form.get('brand_id', 0))
            image_url = request.form.get('image_url', '').strip()
            is_visible = request.form.get('is_visible') == 'on'
            
            # Execute use case
            use_case = UpdateProductUseCase(product_repo, category_repo, brand_repo)
            input_data = UpdateProductInputData(
                product_id=product_id,
                name=name,
                description=description,
                price=price,
                stock_quantity=stock_quantity,
                category_id=category_id,
                brand_id=brand_id,
                image_url=image_url if image_url else None,
                is_visible=is_visible
            )
            
            output = use_case.execute(input_data)
            
            if output.success:
                flash(output.message, 'success')
                return redirect(url_for('admin_products.list_products'))
            else:
                flash(output.message, 'danger')
                
        except ValueError as e:
            flash(f'Dữ liệu không hợp lệ: {str(e)}', 'danger')
        except Exception as e:
            flash(f'Lỗi cập nhật sản phẩm: {str(e)}', 'danger')
    
    # GET request - show form with current data
    product = product_repo.find_by_id(product_id)
    if not product:
        flash('Không tìm thấy sản phẩm', 'danger')
        return redirect(url_for('admin_products.list_products'))
    
    categories = category_repo.find_all()
    brands = brand_repo.find_all()
    
    return render_template('admin/products/edit.html',
                         product=product,
                         categories=categories,
                         brands=brands)


@admin_products_bp.route('/<int:product_id>/delete', methods=['POST'])
@admin_required
def delete_product(product_id):
    """Delete product (soft delete)"""
    try:
        product_repo = ProductRepositoryAdapter(db.session)
        
        # Execute use case
        use_case = DeleteProductUseCase(product_repo)
        input_data = DeleteProductInputData(product_id=product_id)
        
        output = use_case.execute(input_data)
        
        if output.success:
            flash(output.message, 'success')
        else:
            flash(output.message, 'danger')
            
    except Exception as e:
        flash(f'Lỗi xóa sản phẩm: {str(e)}', 'danger')
    
    return redirect(url_for('admin_products.list_products'))


@admin_products_bp.route('/<int:product_id>/toggle-visibility', methods=['POST'])
@admin_required
def toggle_visibility(product_id):
    """Toggle product visibility (show/hide)"""
    try:
        product_repo = ProductRepositoryAdapter(db.session)
        
        # Execute use case
        use_case = ToggleProductVisibilityUseCase(product_repo)
        input_data = DeleteProductInputData(product_id=product_id)
        
        output = use_case.execute(input_data)
        
        # Support AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': output.success,
                'message': output.message
            })
        
        if output.success:
            flash(output.message, 'success')
        else:
            flash(output.message, 'danger')
            
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'message': f'Lỗi: {str(e)}'
            }), 500
        flash(f'Lỗi thay đổi trạng thái: {str(e)}', 'danger')
    
    return redirect(url_for('admin_products.list_products'))


@admin_products_bp.route('/<int:product_id>')
@admin_required
def product_detail(product_id):
    """View product detail (admin view)"""
    try:
        product_repo = ProductRepositoryAdapter(db.session)
        
        # Execute use case
        use_case = GetProductDetailUseCase(product_repo)
        input_data = GetProductDetailInputData(product_id=product_id)
        
        output = use_case.execute(input_data)
        
        if not output.success:
            flash(output.message, 'danger')
            return redirect(url_for('admin_products.list_products'))
        
        return render_template('admin/products/detail.html', output=output)
        
    except Exception as e:
        flash(f'Lỗi tải chi tiết sản phẩm: {str(e)}', 'danger')
        return redirect(url_for('admin_products.list_products'))
