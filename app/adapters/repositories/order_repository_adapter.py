"""
Order Repository Adapter - SQLAlchemy implementation
Clean Architecture - Infrastructure Layer
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import func, and_, or_
from app.business.ports.order_repository import IOrderRepository
from app.domain.entities.order import Order, OrderItem
from app.domain.value_objects import Money
from app.domain.enums import OrderStatus, PaymentMethod
from app.infrastructure.database import db
from app.infrastructure.database.models import OrderModel, OrderItemModel
from decimal import Decimal


class OrderRepositoryAdapter(IOrderRepository):
    """SQLAlchemy implementation of Order repository"""
    
    def save(self, order: Order) -> Order:
        """Save order (create or update)"""
        if order.order_id:
            # Update existing
            order_model = db.session.query(OrderModel).filter_by(id=order.order_id).first()
            if order_model:
                order_model.status = order.status.value
                order_model.total_amount = float(order.total_amount.amount)
                order_model.updated_at = datetime.now()
        else:
            # Create new
            order_model = OrderModel(
                customer_id=order.customer_id,
                total_amount=float(order.total_amount.amount),
                status=order.status.value,
                payment_method=order.payment_method.value,
                shipping_address=order.shipping_address,
                order_date=order.order_date
            )
            db.session.add(order_model)
            db.session.flush()  # Get ID
            
            # Create order items
            for item in order.items:
                item_model = OrderItemModel(
                    order_id=order_model.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=float(item.unit_price.amount)
                )
                db.session.add(item_model)
        
        db.session.commit()
        return self._to_domain(order_model)
    
    def find_by_id(self, order_id: int) -> Optional[Order]:
        """Find order by ID"""
        order_model = db.session.query(OrderModel).filter_by(id=order_id).first()
        if order_model:
            return self._to_domain(order_model)
        return None
    
    def find_by_customer_id(self, customer_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        """Find orders by customer ID"""
        order_models = db.session.query(OrderModel).filter_by(
            customer_id=customer_id
        ).order_by(OrderModel.order_date.desc()).offset(skip).limit(limit).all()
        
        return [self._to_domain(model) for model in order_models]
    
    def find_by_status(self, status: OrderStatus, skip: int = 0, limit: int = 100) -> List[Order]:
        """Find orders by status"""
        order_models = db.session.query(OrderModel).filter_by(
            status=status.value
        ).order_by(OrderModel.order_date.desc()).offset(skip).limit(limit).all()
        
        return [self._to_domain(model) for model in order_models]
    
    def find_all(self, skip: int = 0, limit: int = 100) -> List[Order]:
        """Find all orders"""
        order_models = db.session.query(OrderModel).order_by(
            OrderModel.order_date.desc()
        ).offset(skip).limit(limit).all()
        
        return [self._to_domain(model) for model in order_models]
    
    def find_by_date_range(self, start_date: datetime, end_date: datetime, skip: int = 0, limit: int = 100) -> List[Order]:
        """Find orders within date range"""
        order_models = db.session.query(OrderModel).filter(
            and_(
                OrderModel.order_date >= start_date,
                OrderModel.order_date <= end_date
            )
        ).order_by(OrderModel.order_date.desc()).offset(skip).limit(limit).all()
        
        return [self._to_domain(model) for model in order_models]
    
    def delete(self, order_id: int) -> bool:
        """Delete order"""
        order_model = db.session.query(OrderModel).filter_by(id=order_id).first()
        if order_model:
            db.session.delete(order_model)
            db.session.commit()
            return True
        return False
    
    def count(self) -> int:
        """Count total orders"""
        return db.session.query(func.count(OrderModel.id)).scalar()
    
    def count_by_status(self, status: OrderStatus) -> int:
        """Count orders by status"""
        return db.session.query(func.count(OrderModel.id)).filter_by(
            status=status.value
        ).scalar()
    
    def count_by_customer(self, customer_id: int) -> int:
        """Count orders for customer"""
        return db.session.query(func.count(OrderModel.id)).filter_by(
            customer_id=customer_id
        ).scalar()
    
    def find_with_filters(
        self,
        filters: dict,
        page: int = 1,
        per_page: int = 20,
        sort_by: str = 'newest'
    ) -> tuple[List[Order], int]:
        """Find orders with advanced filters and pagination"""
        query = db.session.query(OrderModel)
        
        # Apply filters
        if filters.get('status'):
            query = query.filter(OrderModel.status == filters['status'])
        
        if filters.get('customer_id'):
            query = query.filter(OrderModel.customer_id == filters['customer_id'])
        
        if filters.get('start_date'):
            query = query.filter(OrderModel.order_date >= filters['start_date'])
        
        if filters.get('end_date'):
            query = query.filter(OrderModel.order_date <= filters['end_date'])
        
        if filters.get('search_query'):
            search = f"%{filters['search_query']}%"
            query = query.filter(
                or_(
                    OrderModel.shipping_address.ilike(search),
                    OrderModel.id.like(search)
                )
            )
        
        # Get total count before pagination
        total = query.count()
        
        # Apply sorting
        if sort_by == 'newest':
            query = query.order_by(OrderModel.order_date.desc())
        elif sort_by == 'oldest':
            query = query.order_by(OrderModel.order_date.asc())
        elif sort_by == 'total_asc':
            query = query.order_by(OrderModel.total_amount.asc())
        elif sort_by == 'total_desc':
            query = query.order_by(OrderModel.total_amount.desc())
        
        # Apply pagination
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        
        order_models = query.all()
        orders = [self._to_domain(model) for model in order_models]
        
        return orders, total
    
    def get_order_statistics(self, filters: Optional[dict] = None) -> dict:
        """Get order statistics"""
        query = db.session.query(OrderModel)
        
        # Apply filters if provided
        if filters:
            if filters.get('status'):
                query = query.filter(OrderModel.status == filters['status'])
            if filters.get('customer_id'):
                query = query.filter(OrderModel.customer_id == filters['customer_id'])
            if filters.get('start_date'):
                query = query.filter(OrderModel.order_date >= filters['start_date'])
            if filters.get('end_date'):
                query = query.filter(OrderModel.order_date <= filters['end_date'])
        
        # Calculate statistics
        stats = {
            'total_revenue': 0,
            'pending_count': 0,
            'shipping_count': 0,
            'completed_count': 0,
            'cancelled_count': 0
        }
        
        # Total revenue (only completed orders)
        completed_query = query.filter(OrderModel.status == OrderStatus.COMPLETED.value)
        revenue = db.session.query(func.sum(OrderModel.total_amount)).filter(
            OrderModel.id.in_([o.id for o in completed_query.all()])
        ).scalar()
        stats['total_revenue'] = float(revenue) if revenue else 0
        
        # Count by status
        stats['pending_count'] = query.filter(OrderModel.status == OrderStatus.PENDING.value).count()
        stats['shipping_count'] = query.filter(OrderModel.status == OrderStatus.SHIPPING.value).count()
        stats['completed_count'] = query.filter(OrderModel.status == OrderStatus.COMPLETED.value).count()
        stats['cancelled_count'] = query.filter(OrderModel.status == OrderStatus.CANCELLED.value).count()
        
        return stats
    
    def _to_domain(self, order_model: OrderModel) -> Order:
        """Convert database model to domain entity"""
        # Reconstruct order items
        order_items = []
        for item_model in order_model.items:
            # Get product name from product model (or use fallback)
            product_name = item_model.product.name if item_model.product else f"Product {item_model.product_id}"
            
            order_item = OrderItem(
                product_id=item_model.product_id,
                product_name=product_name,
                quantity=item_model.quantity,
                unit_price=Money(Decimal(str(item_model.unit_price)), 'VND')
            )
            order_items.append(order_item)
        
        # Reconstruct order with database ID
        order = Order.reconstruct(
            order_id=order_model.id,
            customer_id=order_model.customer_id,
            items=order_items,
            total_amount=Money(Decimal(str(order_model.total_amount)), 'VND'),
            status=OrderStatus(order_model.status),
            payment_method=PaymentMethod(order_model.payment_method),
            shipping_address=order_model.shipping_address,
            order_date=order_model.order_date
        )
        
        return order
