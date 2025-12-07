"""
Admin Dashboard Routes - Admin panel main dashboard with data visualization
Clean Architecture - Adapters Layer
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

from app.adapters.repositories.order_repository_adapter import OrderRepositoryAdapter
from app.adapters.repositories.product_repository_adapter import ProductRepositoryAdapter
from app.adapters.repositories.user_repository_adapter import UserRepositoryAdapter
from app.business.use_cases import GetDashboardStatsUseCase
from app.infrastructure.database import db


admin_dashboard_bp = Blueprint('admin_dashboard', __name__, url_prefix='/admin')


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


@admin_dashboard_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with data visualization"""
    try:
        # Get number of days to analyze (default 30)
        days = int(request.args.get('days', 30))
        
        # Initialize repositories
        order_repo = OrderRepositoryAdapter(db.session)
        product_repo = ProductRepositoryAdapter(db.session)
        user_repo = UserRepositoryAdapter(db.session)
        
        # Execute use case
        use_case = GetDashboardStatsUseCase(order_repo, product_repo, user_repo)
        output = use_case.execute(days=days)
        
        if not output.success:
            flash(output.message, 'danger')
            return render_template('admin/dashboard/index.html', 
                                 output=None,
                                 revenue_chart=None,
                                 category_chart=None,
                                 status_chart=None,
                                 top_products_chart=None)
        
        # Generate Plotly charts
        revenue_chart = create_revenue_chart(output.revenue_dates, output.revenue_values)
        category_chart = create_category_chart(output.category_names, output.category_sales)
        status_chart = create_status_chart(output.status_names, output.status_counts)
        top_products_chart = create_top_products_chart(output.top_product_names, output.top_product_sales)
        
        return render_template('admin/dashboard/index.html',
                             output=output,
                             revenue_chart=revenue_chart,
                             category_chart=category_chart,
                             status_chart=status_chart,
                             top_products_chart=top_products_chart,
                             days=days)
        
    except Exception as e:
        flash(f'Lỗi tải dashboard: {str(e)}', 'danger')
        return render_template('admin/dashboard/index.html',
                             output=None,
                             revenue_chart=None,
                             category_chart=None,
                             status_chart=None,
                             top_products_chart=None)


def create_revenue_chart(dates, values):
    """Create revenue trend line chart"""
    if not dates or not values:
        return None
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode='lines+markers',
        name='Doanh thu',
        line=dict(color='#667eea', width=3),
        marker=dict(size=8, color='#667eea'),
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.1)'
    ))
    
    fig.update_layout(
        title='Xu hướng Doanh thu',
        xaxis_title='Ngày',
        yaxis_title='Doanh thu (VNĐ)',
        hovermode='x unified',
        template='plotly_white',
        height=400,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False})


def create_category_chart(names, sales):
    """Create sales by category pie chart"""
    if not names or not sales:
        return None
    
    fig = go.Figure(data=[go.Pie(
        labels=names,
        values=sales,
        hole=0.4,
        marker=dict(colors=px.colors.qualitative.Set3),
        textinfo='label+percent',
        textposition='outside'
    )])
    
    fig.update_layout(
        title='Doanh thu theo Danh mục',
        height=400,
        template='plotly_white',
        showlegend=True,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False})


def create_status_chart(names, counts):
    """Create order status distribution donut chart"""
    if not names or not counts:
        return None
    
    # Define colors for each status
    colors = {
        'Chờ xác nhận': '#ffc107',  # Yellow
        'Đang giao': '#0dcaf0',      # Cyan
        'Hoàn thành': '#198754',     # Green
        'Đã hủy': '#dc3545'          # Red
    }
    
    chart_colors = [colors.get(name, '#6c757d') for name in names]
    
    fig = go.Figure(data=[go.Pie(
        labels=names,
        values=counts,
        hole=0.5,
        marker=dict(colors=chart_colors),
        textinfo='label+value',
        textposition='outside'
    )])
    
    fig.update_layout(
        title='Phân bố Trạng thái Đơn hàng',
        height=400,
        template='plotly_white',
        showlegend=True,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False})


def create_top_products_chart(names, quantities):
    """Create top selling products bar chart"""
    if not names or not quantities:
        return None
    
    fig = go.Figure(data=[go.Bar(
        x=quantities,
        y=names,
        orientation='h',
        marker=dict(
            color=quantities,
            colorscale='Viridis',
            showscale=False
        ),
        text=quantities,
        textposition='outside'
    )])
    
    fig.update_layout(
        title='Top 10 Sản phẩm Bán chạy',
        xaxis_title='Số lượng đã bán',
        yaxis_title='',
        height=500,
        template='plotly_white',
        margin=dict(l=200, r=50, t=80, b=50),
        yaxis=dict(autorange='reversed')
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False})


@admin_dashboard_bp.route('/api/quick-stats')
@admin_required
def quick_stats():
    """API endpoint for quick stats refresh (AJAX)"""
    try:
        order_repo = OrderRepositoryAdapter(db.session)
        product_repo = ProductRepositoryAdapter(db.session)
        user_repo = UserRepositoryAdapter(db.session)
        
        use_case = GetDashboardStatsUseCase(order_repo, product_repo, user_repo)
        output = use_case.execute(days=7)  # Last 7 days for quick stats
        
        if output.success:
            return jsonify({
                'success': True,
                'total_revenue': output.total_revenue,
                'total_orders': output.total_orders,
                'pending_orders': output.pending_orders,
                'total_customers': output.total_customers
            })
        else:
            return jsonify({'success': False, 'message': output.message}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
