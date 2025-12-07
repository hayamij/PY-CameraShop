"""
Admin Category Routes

Provides CRUD endpoints for category management:
- GET /admin/categories - List all categories with product counts
- GET /admin/categories/create - Create category form
- POST /admin/categories/create - Save new category
- GET /admin/categories/<id>/edit - Edit category form
- POST /admin/categories/<id>/edit - Update category
- POST /admin/categories/<id>/delete - Delete category
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from functools import wraps
from app.business.use_cases import (
    CreateCategoryUseCase, CreateCategoryInputData,
    UpdateCategoryUseCase, UpdateCategoryInputData,
    DeleteCategoryUseCase, DeleteCategoryInputData
)
from app.adapters.repositories.category_repository_adapter import CategoryRepositoryAdapter
from app.adapters.repositories.product_repository_adapter import ProductRepositoryAdapter
from app.infrastructure.database.db import db
from flask_login import current_user


admin_categories_bp = Blueprint('admin_categories', __name__, url_prefix='/admin/categories')


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


@admin_categories_bp.route('/', methods=['GET'])
@admin_required
def list_categories():
    """List all categories with product counts"""
    try:
        category_repo = CategoryRepositoryAdapter(db.session)
        product_repo = ProductRepositoryAdapter(db.session)
        
        # Get all categories
        categories = category_repo.find_all()
        
        # Add product count for each category
        categories_with_counts = []
        for category in categories:
            product_count = product_repo.count_by_category(category.id)
            categories_with_counts.append({
                'category': category,
                'product_count': product_count
            })
        
        return render_template(
            'admin/categories/list.html',
            categories=categories_with_counts
        )
    
    except Exception as e:
        flash(f'Lỗi khi tải danh sách danh mục: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard.dashboard'))


@admin_categories_bp.route('/create', methods=['GET', 'POST'])
@admin_required
def create_category():
    """Create new category"""
    if request.method == 'GET':
        return render_template('admin/categories/create.html')
    
    try:
        # Get form data
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        # Create use case
        category_repo = CategoryRepositoryAdapter(db.session)
        use_case = CreateCategoryUseCase(category_repo)
        
        # Execute
        input_data = CreateCategoryInputData(
            name=name,
            description=description
        )
        output = use_case.execute(input_data)
        
        flash(output.message, 'success')
        return redirect(url_for('admin_categories.list_categories'))
    
    except Exception as e:
        flash(f'Lỗi khi tạo danh mục: {str(e)}', 'error')
        return render_template('admin/categories/create.html')


@admin_categories_bp.route('/<int:category_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_category(category_id):
    """Edit existing category"""
    category_repo = CategoryRepositoryAdapter(db.session)
    
    if request.method == 'GET':
        try:
            # Get category
            category = category_repo.find_by_id(category_id)
            if category is None:
                flash('Không tìm thấy danh mục', 'error')
                return redirect(url_for('admin_categories.list_categories'))
            
            return render_template(
                'admin/categories/edit.html',
                category=category
            )
        
        except Exception as e:
            flash(f'Lỗi khi tải thông tin danh mục: {str(e)}', 'error')
            return redirect(url_for('admin_categories.list_categories'))
    
    # POST - Update category
    try:
        # Get form data
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        # Create use case
        use_case = UpdateCategoryUseCase(category_repo)
        
        # Execute
        input_data = UpdateCategoryInputData(
            category_id=category_id,
            name=name,
            description=description
        )
        output = use_case.execute(input_data)
        
        flash(output.message, 'success')
        return redirect(url_for('admin_categories.list_categories'))
    
    except Exception as e:
        flash(f'Lỗi khi cập nhật danh mục: {str(e)}', 'error')
        
        # Reload category for form
        category = category_repo.find_by_id(category_id)
        return render_template(
            'admin/categories/edit.html',
            category=category
        )


@admin_categories_bp.route('/<int:category_id>/delete', methods=['POST'])
@admin_required
def delete_category(category_id):
    """Delete category"""
    try:
        # Create use cases
        category_repo = CategoryRepositoryAdapter(db.session)
        product_repo = ProductRepositoryAdapter(db.session)
        use_case = DeleteCategoryUseCase(category_repo, product_repo)
        
        # Execute
        input_data = DeleteCategoryInputData(category_id=category_id)
        output = use_case.execute(input_data)
        
        flash(output.message, 'success')
    
    except Exception as e:
        flash(f'Lỗi khi xóa danh mục: {str(e)}', 'error')
    
    return redirect(url_for('admin_categories.list_categories'))
