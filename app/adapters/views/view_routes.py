"""Frontend view routes - Server-side rendering"""
from flask import Blueprint, render_template, session, redirect, url_for, flash, request, current_app
from app.adapters.api.auth_helpers import login_required
from app.infrastructure.config import get_session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import json

# Create blueprint
view_bp = Blueprint('views', __name__)


@view_bp.route('/')
def index():
    """Home page"""
    return render_template('customer/index.html')


@view_bp.route('/products')
def products():
    """Product listing page"""
    return render_template('customer/products.html')


@view_bp.route('/products/<int:product_id>')
def product_detail(product_id):
    """Product detail page"""
    return render_template('customer/product-detail.html', product_id=product_id)


@view_bp.route('/cart')
@login_required
def cart():
    """Shopping cart page"""
    return render_template('customer/cart.html')


@view_bp.route('/checkout')
@login_required
def checkout():
    """Checkout page"""
    return render_template('customer/checkout.html')


@view_bp.route('/login')
def login():
    """Login page"""
    if session.get('user_id'):
        return redirect(url_for('views.index'))
    return render_template('auth/login.html')


@view_bp.route('/register')
def register():
    """Register page"""
    if session.get('user_id'):
        return redirect(url_for('views.index'))
    return render_template('auth/register.html')


@view_bp.route('/orders')
@login_required
def my_orders():
    """My orders page"""
    return render_template('customer/orders.html')


@view_bp.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    """Order detail page"""
    return render_template('customer/order-detail.html', order_id=order_id)


@view_bp.route('/admin')
@login_required
def admin_dashboard():
    """Admin dashboard with Plotly charts"""
    # Check if user is admin
    if session.get('role') != 'ADMIN':
        flash('Bạn không có quyền truy cập trang này', 'error')
        return redirect(url_for('views.index'))
    
    from app.infrastructure.database.models.order_model import OrderModel
    from app.infrastructure.database.models.product_model import ProductModel, CategoryModel, BrandModel
    from app.infrastructure.database.models.user_model import UserModel
    
    # Get database session
    db_session = get_session()
    
    try:
        # 1. REVENUE BY MONTH CHART (Last 6 months)
        six_months_ago = datetime.now() - timedelta(days=180)
        revenue_data = db_session.query(
            func.year(OrderModel.created_at).label('year'),
            func.month(OrderModel.created_at).label('month'),
            func.sum(OrderModel.total_amount).label('revenue')
        ).filter(
            OrderModel.created_at >= six_months_ago,
            OrderModel.order_status.in_(['HOAN_THANH', 'DANG_GIAO'])
        ).group_by(
            func.year(OrderModel.created_at),
            func.month(OrderModel.created_at)
        ).order_by('year', 'month').all()
        
        months = []
        revenues = []
        for item in revenue_data:
            month_name = f"{item.month}/{item.year}"
            months.append(month_name)
            revenues.append(float(item.revenue or 0))
        
        revenue_chart = go.Figure(data=[
        go.Scatter(
            x=months,
            y=revenues,
            mode='lines+markers',
            line=dict(color='#007bff', width=3),
            marker=dict(size=10, color='#007bff'),
            fill='tozeroy',
            fillcolor='rgba(0, 123, 255, 0.1)'
        )
        ])
        revenue_chart.update_layout(
            title='Doanh Thu Theo Tháng (6 tháng gần nhất)',
            xaxis_title='Tháng',
            yaxis_title='Doanh Thu (VND)',
            template='plotly_white',
            hovermode='x unified',
            height=400
        )
        revenue_chart_json = json.dumps(revenue_chart, cls=PlotlyJSONEncoder)
        
        # 2. ORDER STATUS DISTRIBUTION
        status_data = db_session.query(
            OrderModel.order_status,
            func.count(OrderModel.order_id).label('count')
        ).group_by(OrderModel.order_status).all()
        
        status_labels = []
        status_values = []
        status_colors = []
        status_map = {
            'CHO_XAC_NHAN': ('Chờ Xác Nhận', '#ffc107'),
            'DANG_GIAO': ('Đang Giao', '#17a2b8'),
            'HOAN_THANH': ('Hoàn Thành', '#28a745'),
            'DA_HUY': ('Đã Hủy', '#dc3545')
        }
        
        for item in status_data:
            label, color = status_map.get(item.order_status, (item.order_status, '#6c757d'))
            status_labels.append(label)
            status_values.append(item.count)
            status_colors.append(color)
        
        status_chart = go.Figure(data=[
            go.Pie(
                labels=status_labels,
                values=status_values,
                marker=dict(colors=status_colors),
                hole=0.4,
                textinfo='label+percent+value',
                textposition='outside'
            )
        ])
        status_chart.update_layout(
            title='Phân Bố Trạng Thái Đơn Hàng',
            template='plotly_white',
            height=400
        )
        status_chart_json = json.dumps(status_chart, cls=PlotlyJSONEncoder)
        
        # 3. PRODUCT COUNT BY CATEGORY
        category_data = db_session.query(
        CategoryModel.name,
        func.count(ProductModel.product_id).label('product_count'),
            func.sum(ProductModel.stock_quantity).label('total_stock')
        ).join(
            ProductModel, ProductModel.category_id == CategoryModel.category_id
        ).group_by(
            CategoryModel.name
        ).order_by(
            func.count(ProductModel.product_id).desc()
        ).limit(8).all()
        
        categories = [item.name for item in category_data]
        product_counts = [item.product_count for item in category_data]
        
        category_chart = go.Figure(data=[
            go.Bar(
                x=categories,
                y=product_counts,
                marker=dict(
                    color=product_counts,
                    colorscale='Blues',
                    showscale=False
                ),
                text=product_counts,
                textposition='outside'
            )
        ])
        category_chart.update_layout(
            title='Số Lượng Sản Phẩm Theo Danh Mục',
            xaxis_title='Danh Mục',
            yaxis_title='Số Sản Phẩm',
            template='plotly_white',
            height=400
        )
        category_chart_json = json.dumps(category_chart, cls=PlotlyJSONEncoder)
        
        # 4. USER REGISTRATION TREND
        user_trend = db_session.query(
            func.year(UserModel.created_at).label('year'),
            func.month(UserModel.created_at).label('month'),
            func.count(UserModel.user_id).label('count')
        ).filter(
            UserModel.created_at >= six_months_ago
        ).group_by(
            func.year(UserModel.created_at),
            func.month(UserModel.created_at)
        ).order_by('year', 'month').all()
        
        user_months = []
        user_counts = []
        for item in user_trend:
            month_name = f"{item.month}/{item.year}"
            user_months.append(month_name)
            user_counts.append(item.count)
        
        user_chart = go.Figure(data=[
            go.Bar(
                x=user_months,
                y=user_counts,
                marker=dict(color='#28a745'),
                text=user_counts,
                textposition='outside'
            )
        ])
        user_chart.update_layout(
            title='Số Người Dùng Đăng Ký Mới Theo Tháng',
            xaxis_title='Tháng',
            yaxis_title='Số Người Dùng',
            template='plotly_white',
            height=400
        )
        user_chart_json = json.dumps(user_chart, cls=PlotlyJSONEncoder)
        
        return render_template('admin/dashboard.html',
                             revenue_chart=revenue_chart_json,
                             status_chart=status_chart_json,
                             category_chart=category_chart_json,
                             user_chart=user_chart_json)
    finally:
        db_session.close()


@view_bp.route('/admin/users')
@login_required
def admin_users():
    """Admin user management"""
    if session.get('role') != 'ADMIN':
        flash('Bạn không có quyền truy cập trang này', 'error')
        return redirect(url_for('views.index'))
    
    return render_template('admin/users.html')


@view_bp.route('/admin/products')
@login_required
def admin_products():
    """Admin product management"""
    if session.get('role') != 'ADMIN':
        flash('Bạn không có quyền truy cập trang này', 'error')
        return redirect(url_for('views.index'))
    
    return render_template('admin/products.html')


@view_bp.route('/admin/orders')
@login_required
def admin_orders():
    """Admin order management"""
    if session.get('role') != 'ADMIN':
        flash('Bạn không có quyền truy cập trang này', 'error')
        return redirect(url_for('views.index'))
    
    return render_template('admin/orders.html')


@view_bp.route('/admin/categories')
@login_required
def admin_categories():
    """Admin category management"""
    if session.get('role') != 'ADMIN':
        flash('Bạn không có quyền truy cập trang này', 'error')
        return redirect(url_for('views.index'))
    
    return render_template('admin/categories.html')


@view_bp.route('/admin/brands')
@login_required
def admin_brands():
    """Admin brand management"""
    if session.get('role') != 'ADMIN':
        flash('Bạn không có quyền truy cập trang này', 'error')
        return redirect(url_for('views.index'))
    
    return render_template('admin/brands.html')
