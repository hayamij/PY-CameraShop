"""
Admin Brand Routes

Provides CRUD endpoints for brand management:
- GET /admin/brands - List all brands with product counts
- GET /admin/brands/create - Create brand form
- POST /admin/brands/create - Save new brand
- GET /admin/brands/<id>/edit - Edit brand form
- POST /admin/brands/<id>/edit - Update brand
- POST /admin/brands/<id>/delete - Delete brand
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from functools import wraps
from app.business.use_cases import (
    CreateBrandUseCase, CreateBrandInputData,
    UpdateBrandUseCase, UpdateBrandInputData,
    DeleteBrandUseCase, DeleteBrandInputData
)
from app.adapters.repositories.brand_repository_adapter import BrandRepositoryAdapter
from app.adapters.repositories.product_repository_adapter import ProductRepositoryAdapter
from app.infrastructure.database.db import db
from flask_login import current_user


admin_brands_bp = Blueprint('admin_brands', __name__, url_prefix='/admin/brands')


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Vui lòng đăng nhập để truy cập trang này', 'error')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin():
            flash('Bạn không có quyền truy cập trang này', 'error')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function


@admin_brands_bp.route('/', methods=['GET'])
@admin_required
def list_brands():
    """List all brands with product counts"""
    try:
        brand_repo = BrandRepositoryAdapter(db.session)
        product_repo = ProductRepositoryAdapter(db.session)
        
        # Get all brands
        brands = brand_repo.find_all()
        
        # Add product count for each brand
        brands_with_counts = []
        for brand in brands:
            product_count = product_repo.count_by_brand(brand.id)
            brands_with_counts.append({
                'brand': brand,
                'product_count': product_count
            })
        
        return render_template(
            'admin/brands/list.html',
            brands=brands_with_counts
        )
    
    except Exception as e:
        flash(f'Lỗi khi tải danh sách thương hiệu: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard.dashboard'))


@admin_brands_bp.route('/create', methods=['GET', 'POST'])
@admin_required
def create_brand():
    """Create new brand"""
    if request.method == 'GET':
        return render_template('admin/brands/create.html')
    
    try:
        # Get form data
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        logo_url = request.form.get('logo_url', '').strip()
        
        # Create use case
        brand_repo = BrandRepositoryAdapter(db.session)
        use_case = CreateBrandUseCase(brand_repo)
        
        # Execute
        input_data = CreateBrandInputData(
            name=name,
            description=description,
            logo_url=logo_url
        )
        output = use_case.execute(input_data)
        
        flash(output.message, 'success')
        return redirect(url_for('admin_brands.list_brands'))
    
    except Exception as e:
        flash(f'Lỗi khi tạo thương hiệu: {str(e)}', 'error')
        return render_template('admin/brands/create.html')


@admin_brands_bp.route('/<int:brand_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_brand(brand_id):
    """Edit existing brand"""
    brand_repo = BrandRepositoryAdapter(db.session)
    
    if request.method == 'GET':
        try:
            # Get brand
            brand = brand_repo.find_by_id(brand_id)
            if brand is None:
                flash('Không tìm thấy thương hiệu', 'error')
                return redirect(url_for('admin_brands.list_brands'))
            
            return render_template(
                'admin/brands/edit.html',
                brand=brand
            )
        
        except Exception as e:
            flash(f'Lỗi khi tải thông tin thương hiệu: {str(e)}', 'error')
            return redirect(url_for('admin_brands.list_brands'))
    
    # POST - Update brand
    try:
        # Get form data
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        logo_url = request.form.get('logo_url', '').strip()
        
        # Create use case
        use_case = UpdateBrandUseCase(brand_repo)
        
        # Execute
        input_data = UpdateBrandInputData(
            brand_id=brand_id,
            name=name,
            description=description,
            logo_url=logo_url
        )
        output = use_case.execute(input_data)
        
        flash(output.message, 'success')
        return redirect(url_for('admin_brands.list_brands'))
    
    except Exception as e:
        flash(f'Lỗi khi cập nhật thương hiệu: {str(e)}', 'error')
        
        # Reload brand for form
        brand = brand_repo.find_by_id(brand_id)
        return render_template(
            'admin/brands/edit.html',
            brand=brand
        )


@admin_brands_bp.route('/<int:brand_id>/delete', methods=['POST'])
@admin_required
def delete_brand(brand_id):
    """Delete brand"""
    try:
        # Create use cases
        brand_repo = BrandRepositoryAdapter(db.session)
        product_repo = ProductRepositoryAdapter(db.session)
        use_case = DeleteBrandUseCase(brand_repo, product_repo)
        
        # Execute
        input_data = DeleteBrandInputData(brand_id=brand_id)
        output = use_case.execute(input_data)
        
        flash(output.message, 'success')
    
    except Exception as e:
        flash(f'Lỗi khi xóa thương hiệu: {str(e)}', 'error')
    
    return redirect(url_for('admin_brands.list_brands'))
