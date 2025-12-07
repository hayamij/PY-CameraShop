"""
Get Dashboard Statistics Use Case - Admin dashboard analytics
Clean Architecture - Business Layer
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from app.business.ports.order_repository import IOrderRepository
from app.business.ports.product_repository import IProductRepository
from app.business.ports.user_repository import IUserRepository
from app.domain.entities.order import OrderStatus


class GetDashboardStatsOutputData:
    """Output data for dashboard statistics"""
    
    def __init__(
        self,
        success: bool,
        # Overview metrics
        total_revenue: float = 0,
        total_orders: int = 0,
        total_products: int = 0,
        total_customers: int = 0,
        pending_orders: int = 0,
        # Revenue trend data (for line chart)
        revenue_dates: Optional[List[str]] = None,
        revenue_values: Optional[List[float]] = None,
        # Sales by category data (for pie chart)
        category_names: Optional[List[str]] = None,
        category_sales: Optional[List[float]] = None,
        # Order status distribution (for donut chart)
        status_names: Optional[List[str]] = None,
        status_counts: Optional[List[int]] = None,
        # Top products (for bar chart)
        top_product_names: Optional[List[str]] = None,
        top_product_sales: Optional[List[int]] = None,
        # Recent orders
        recent_orders: Optional[List[Dict]] = None,
        # Low stock products
        low_stock_products: Optional[List[Dict]] = None,
        message: Optional[str] = None
    ):
        self.success = success
        self.total_revenue = total_revenue
        self.total_orders = total_orders
        self.total_products = total_products
        self.total_customers = total_customers
        self.pending_orders = pending_orders
        
        # Chart data
        self.revenue_dates = revenue_dates or []
        self.revenue_values = revenue_values or []
        self.category_names = category_names or []
        self.category_sales = category_sales or []
        self.status_names = status_names or []
        self.status_counts = status_counts or []
        self.top_product_names = top_product_names or []
        self.top_product_sales = top_product_sales or []
        
        # Additional data
        self.recent_orders = recent_orders or []
        self.low_stock_products = low_stock_products or []
        self.message = message


class GetDashboardStatsUseCase:
    """
    Use case for getting admin dashboard statistics and analytics data
    Aggregates data from multiple repositories for visualization
    """
    
    def __init__(
        self,
        order_repository: IOrderRepository,
        product_repository: IProductRepository,
        user_repository: IUserRepository
    ):
        self.order_repository = order_repository
        self.product_repository = product_repository
        self.user_repository = user_repository
    
    def execute(self, days: int = 30) -> GetDashboardStatsOutputData:
        """
        Execute the dashboard statistics use case
        
        Args:
            days: Number of days to analyze for trends (default 30)
            
        Returns:
            GetDashboardStatsOutputData with aggregated statistics
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 1. Get overview metrics
            total_revenue = self._calculate_total_revenue()
            total_orders = self.order_repository.count()
            total_products = self.product_repository.count()
            total_customers = self.user_repository.count_customers()
            pending_orders = self.order_repository.count_by_status(OrderStatus.PENDING.value)
            
            # 2. Get revenue trend (last N days)
            revenue_dates, revenue_values = self._get_revenue_trend(start_date, end_date, days)
            
            # 3. Get sales by category
            category_names, category_sales = self._get_sales_by_category()
            
            # 4. Get order status distribution
            status_names, status_counts = self._get_order_status_distribution()
            
            # 5. Get top selling products
            top_product_names, top_product_sales = self._get_top_products(limit=10)
            
            # 6. Get recent orders (last 5)
            recent_orders = self._get_recent_orders(limit=5)
            
            # 7. Get low stock products (stock < 10)
            low_stock_products = self._get_low_stock_products(threshold=10)
            
            return GetDashboardStatsOutputData(
                success=True,
                total_revenue=total_revenue,
                total_orders=total_orders,
                total_products=total_products,
                total_customers=total_customers,
                pending_orders=pending_orders,
                revenue_dates=revenue_dates,
                revenue_values=revenue_values,
                category_names=category_names,
                category_sales=category_sales,
                status_names=status_names,
                status_counts=status_counts,
                top_product_names=top_product_names,
                top_product_sales=top_product_sales,
                recent_orders=recent_orders,
                low_stock_products=low_stock_products
            )
            
        except Exception as e:
            return GetDashboardStatsOutputData(
                success=False,
                message=f"Error loading dashboard: {str(e)}"
            )
    
    def _calculate_total_revenue(self) -> float:
        """Calculate total revenue from completed orders"""
        completed_orders = self.order_repository.find_by_status(OrderStatus.COMPLETED.value)
        total = sum(order.total_amount.amount for order in completed_orders)
        return float(total)
    
    def _get_revenue_trend(self, start_date: datetime, end_date: datetime, days: int):
        """Get daily revenue for the specified period"""
        dates = []
        values = []
        
        for i in range(days):
            date = start_date + timedelta(days=i)
            next_date = date + timedelta(days=1)
            
            # Get orders for this day
            daily_orders = self.order_repository.find_by_date_range(
                date, 
                next_date,
                status=OrderStatus.COMPLETED.value
            )
            
            daily_revenue = sum(order.total_amount.amount for order in daily_orders)
            
            dates.append(date.strftime('%Y-%m-%d'))
            values.append(float(daily_revenue))
        
        return dates, values
    
    def _get_sales_by_category(self):
        """Get sales grouped by product category"""
        # This requires querying orders and aggregating by product category
        # For simplicity, we'll get all completed orders and group by category
        completed_orders = self.order_repository.find_by_status(OrderStatus.COMPLETED.value)
        
        category_totals = {}
        
        for order in completed_orders:
            for item in order.items:
                # Get product to find its category
                product = self.product_repository.find_by_id(item.product_id)
                if product:
                    category_name = product.category.name if product.category else "Khác"
                    
                    if category_name not in category_totals:
                        category_totals[category_name] = 0
                    
                    category_totals[category_name] += float(item.subtotal().amount)
        
        # Sort by sales descending
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        
        names = [cat[0] for cat in sorted_categories]
        sales = [cat[1] for cat in sorted_categories]
        
        return names, sales
    
    def _get_order_status_distribution(self):
        """Get order counts by status"""
        statuses = [
            ('Chờ xác nhận', OrderStatus.PENDING.value),
            ('Đang giao', OrderStatus.SHIPPING.value),
            ('Hoàn thành', OrderStatus.COMPLETED.value),
            ('Đã hủy', OrderStatus.CANCELLED.value)
        ]
        
        names = []
        counts = []
        
        for status_name, status_value in statuses:
            count = self.order_repository.count_by_status(status_value)
            if count > 0:  # Only include statuses with orders
                names.append(status_name)
                counts.append(count)
        
        return names, counts
    
    def _get_top_products(self, limit: int = 10):
        """Get top selling products by quantity"""
        # Get all completed orders
        completed_orders = self.order_repository.find_by_status(OrderStatus.COMPLETED.value)
        
        product_quantities = {}
        
        for order in completed_orders:
            for item in order.items:
                if item.product_id not in product_quantities:
                    product_quantities[item.product_id] = {
                        'name': item.product_name,
                        'quantity': 0
                    }
                product_quantities[item.product_id]['quantity'] += item.quantity
        
        # Sort by quantity descending and take top N
        sorted_products = sorted(
            product_quantities.values(),
            key=lambda x: x['quantity'],
            reverse=True
        )[:limit]
        
        names = [p['name'] for p in sorted_products]
        quantities = [p['quantity'] for p in sorted_products]
        
        return names, quantities
    
    def _get_recent_orders(self, limit: int = 5):
        """Get most recent orders"""
        all_orders = self.order_repository.find_all()
        
        # Sort by order date descending
        recent = sorted(all_orders, key=lambda x: x.order_date, reverse=True)[:limit]
        
        orders_data = []
        for order in recent:
            # Get customer info
            customer = self.user_repository.find_by_id(order.customer_id)
            
            orders_data.append({
                'order_id': order.id,
                'customer_name': customer.full_name if customer else 'N/A',
                'total': float(order.total_amount.amount),
                'status': order.status.value,
                'date': order.order_date.strftime('%d/%m/%Y %H:%M')
            })
        
        return orders_data
    
    def _get_low_stock_products(self, threshold: int = 10):
        """Get products with stock below threshold"""
        all_products = self.product_repository.find_all()
        
        low_stock = []
        for product in all_products:
            if product.stock_quantity <= threshold and product.is_visible:
                low_stock.append({
                    'id': product.id,
                    'name': product.name,
                    'stock': product.stock_quantity,
                    'category': product.category.name if product.category else 'N/A'
                })
        
        # Sort by stock ascending
        low_stock.sort(key=lambda x: x['stock'])
        
        return low_stock
