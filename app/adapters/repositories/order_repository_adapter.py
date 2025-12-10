"""Order Repository Adapter - Infrastructure implementation of order persistence."""
from typing import Optional, List, Tuple
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy import func

from ...business.ports.order_repository import IOrderRepository
from ...domain.entities.order import Order, OrderItem
from ...domain.value_objects.money import Money
from ...domain.enums import OrderStatus, PaymentMethod
from ...infrastructure.config.database import get_session
from ...infrastructure.database.models.order_model import OrderModel, OrderItemModel


class OrderRepositoryAdapter(IOrderRepository):
    """Adapter for Order persistence using SQLAlchemy."""
    
    def __init__(self, session=None):
        """
        Initialize order repository adapter.
        
        Args:
            session: SQLAlchemy session (optional, for testing)
        """
        self._session = session
        pass
    
    def save(self, order: Order) -> Order:
        """
        Save order (create or update).
        
        Args:
            order: Order entity to save
            
        Returns:
            Saved order entity with updated ID
        """
        session = self._session or get_session()
        try:
            if order.id is None:
                # Create new order
                order_model = self._to_orm_model(order)
                session.add(order_model)
                session.flush()  # Get the ID
                order = self._to_domain_entity(order_model)
            else:
                # Update existing order
                order_model = session.query(OrderModel).filter(
                    OrderModel.order_id == order.id
                ).first()
                
                if not order_model:
                    raise ValueError(f"Order with id {order.id} not found")
                
                self._update_model_from_entity(order_model, order, session)
            
            session.commit()
            return order
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def find_by_id(self, order_id: int) -> Optional[Order]:
        """
        Find order by ID.
        
        Args:
            order_id: Order ID to find
            
        Returns:
            Order entity if found, None otherwise
        """
        session = self._session or get_session()
        try:
            # Eagerly load order items and their products
            order_model = (session.query(OrderModel)
                          .options(
                              joinedload(OrderModel.items)
                              .joinedload(OrderItemModel.product)
                          )
                          .filter(OrderModel.order_id == order_id)
                          .first())
            
            if not order_model:
                return None
            
            return self._to_domain_entity(order_model)
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def find_by_customer_id(self, customer_id: int, skip: int = 0, 
                           limit: int = 100) -> List[Order]:
        """
        Find orders by customer ID with pagination.
        
        Args:
            customer_id: Customer ID to find orders for
            skip: Number of orders to skip
            limit: Maximum number of orders to return
            
        Returns:
            List of order entities
        """
        session = self._session or get_session()
        try:
            query = (session.query(OrderModel)
                    .options(
                        joinedload(OrderModel.items)
                        .joinedload(OrderItemModel.product)
                    )
                    .filter(OrderModel.user_id == customer_id)
                    .order_by(OrderModel.created_at.desc()))
            
            query = query.offset(skip).limit(limit)
            
            order_models = query.all()
            return [self._to_domain_entity(om) for om in order_models]
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def find_all(self, skip: int = 0, limit: int = 100) -> List[Order]:
        """
        Find all orders with pagination.
        
        Args:
            skip: Number of orders to skip
            limit: Maximum number of orders to return
            
        Returns:
            List of order entities
        """
        session = self._session or get_session()
        try:
            query = (session.query(OrderModel)
                    .options(
                        joinedload(OrderModel.items)
                        .joinedload(OrderItemModel.product)
                    )
                    .order_by(OrderModel.created_at.desc()))
            
            query = query.offset(skip).limit(limit)
            
            order_models = query.all()
            return [self._to_domain_entity(om) for om in order_models]
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def find_by_status(self, status: OrderStatus, skip: int = 0,
                      limit: int = 100) -> List[Order]:
        """
        Find orders by status with pagination.
        
        Args:
            status: Order status to filter by
            skip: Number of orders to skip
            limit: Maximum number of orders to return
            
        Returns:
            List of order entities
        """
        session = self._session or get_session()
        try:
            query = (session.query(OrderModel)
                    .options(
                        joinedload(OrderModel.items)
                        .joinedload(OrderItemModel.product)
                    )
                    .filter(OrderModel.order_status == status.value)
                    .order_by(OrderModel.created_at.desc()))
            
            query = query.offset(skip).limit(limit)
            
            order_models = query.all()
            return [self._to_domain_entity(om) for om in order_models]
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def find_by_date_range(self, start_date: datetime, end_date: datetime,
                          skip: int = 0, 
                          limit: int = 100) -> List[Order]:
        """
        Find orders within date range.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            skip: Number of orders to skip
            limit: Maximum number of orders to return
            
        Returns:
            List of order entities
        """
        session = self._session or get_session()
        try:
            query = (session.query(OrderModel)
                    .options(
                        joinedload(OrderModel.items)
                        .joinedload(OrderItemModel.product)
                    )
                    .filter(OrderModel.created_at >= start_date)
                    .filter(OrderModel.created_at <= end_date)
                    .order_by(OrderModel.created_at.desc()))
            
            query = query.offset(skip).limit(limit)
            
            order_models = query.all()
            return [self._to_domain_entity(om) for om in order_models]
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def count_by_user_id(self, user_id: int) -> int:
        """
        Count total orders for a user.
        
        Args:
            user_id: User ID to count orders for
            
        Returns:
            Total number of orders
        """
        session = self._session or get_session()
        try:
            count = session.query(OrderModel).filter(
                OrderModel.user_id == user_id
            ).count()
            return count
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def count(self) -> int:
        """
        Count total orders in system.
        
        Returns:
            Total number of orders
        """
        session = self._session or get_session()
        try:
            count = session.query(OrderModel).count()
            return count
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def count_by_status(self, status: OrderStatus) -> int:
        """
        Count orders by status.
        
        Args:
            status: Order status to count
            
        Returns:
            Number of orders with given status
        """
        session = self._session or get_session()
        try:
            count = session.query(OrderModel).filter(
                OrderModel.status == status.value
            ).count()
            return count
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def _to_domain_entity(self, order_model: OrderModel) -> Order:
        """
        Convert ORM model to domain entity.
        
        Args:
            order_model: OrderModel instance
            
        Returns:
            Order domain entity
        """
        # Convert order items to domain entities
        order_items = []
        for item_model in order_model.items:
            # OrderItem constructor: (product_id, product_name, quantity, unit_price)
            order_item = OrderItem(
                product_id=item_model.product_id,
                product_name=item_model.product_name,
                quantity=item_model.quantity,
                unit_price=Money(item_model.unit_price, 'VND')
            )
            order_items.append(order_item)
        
        # Reconstruct order with items
        # Order.reconstruct(order_id, customer_id, items, payment_method, shipping_address, phone_number, notes, status, total_amount, created_at, updated_at)
        return Order.reconstruct(
            order_id=order_model.order_id,
            customer_id=order_model.user_id,
            items=order_items,
            payment_method=PaymentMethod(order_model.payment_method),
            shipping_address=order_model.shipping_address,
            phone_number=order_model.phone_number,
            notes=order_model.notes or "",
            status=OrderStatus(order_model.order_status),
            total_amount=Money(order_model.total_amount, 'VND'),
            created_at=order_model.created_at,
            updated_at=order_model.created_at  # OrderModel doesn't have updated_at
        )
    
    def _to_orm_model(self, order: Order) -> OrderModel:
        """
        Convert domain entity to ORM model for new entities.
        
        Args:
            order: Order domain entity
            
        Returns:
            OrderModel instance
        """
        order_model = OrderModel(
            user_id=order.customer_id,
            shipping_address=order.shipping_address,
            phone_number=order.phone_number,
            order_status=order.status.value,
            payment_method=order.payment_method.value,
            notes=order.notes,
            total_amount=order.total_amount.amount,
            created_at=order.created_at
        )
        
        # Add order items
        for item in order.items:
            order_item_model = OrderItemModel(
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price.amount
            )
            order_model.items.append(order_item_model)
        
        return order_model
    
    def _update_model_from_entity(self, order_model: OrderModel, order: Order, session) -> None:
        """
        Update existing ORM model from domain entity.
        
        Args:
            order_model: Existing OrderModel instance
            order: Order domain entity with updates
            session: SQLAlchemy session
        """
        # Update order fields (typically only status changes after creation)
        order_model.shipping_address = order.shipping_address
        order_model.phone_number = order.phone_number
        order_model.notes = order.notes
        order_model.order_status = order.status.value
        order_model.payment_method = order.payment_method.value
        order_model.total_amount = order.total_amount.amount
        
        # Note: Order items are typically not updated after creation
        # If needed, implement similar logic to cart items update
    
    def delete(self, order_id: int) -> bool:
        """
        Delete order by ID.
        
        Args:
            order_id: Order ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        session = self._session or get_session()
        try:
            order_model = session.query(OrderModel).filter(
                OrderModel.order_id == order_id
            ).first()
            
            if not order_model:
                return False
            
            session.delete(order_model)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def count_by_customer(self, customer_id: int) -> int:
        """
        Count orders for a customer.
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Number of orders for customer
        """
        session = self._session or get_session()
        try:
            count = session.query(OrderModel).filter(
                OrderModel.user_id == customer_id
            ).count()
            return count
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def find_with_filters(
        self,
        filters: dict,
        page: int = 1,
        per_page: int = 20,
        sort_by: str = 'newest'
    ) -> Tuple[List[Order], int]:
        """
        Find orders with advanced filters and pagination.
        
        Args:
            filters: Dictionary of filters
            page: Page number (1-indexed)
            per_page: Items per page
            sort_by: Sort option
            
        Returns:
            Tuple of (orders list, total count)
        """
        session = self._session or get_session()
        try:
            query = session.query(OrderModel).options(
                joinedload(OrderModel.items).joinedload(OrderItemModel.product)
            )
            
            # Apply filters
            if filters.get('status'):
                query = query.filter(OrderModel.order_status == filters['status'])
            if filters.get('customer_id'):
                query = query.filter(OrderModel.user_id == filters['customer_id'])
            if filters.get('start_date'):
                query = query.filter(OrderModel.created_at >= filters['start_date'])
            if filters.get('end_date'):
                query = query.filter(OrderModel.created_at <= filters['end_date'])
            
            # Get total count before pagination
            total_count = query.count()
            
            # Apply sorting
            if sort_by == 'oldest':
                query = query.order_by(OrderModel.created_at.asc())
            elif sort_by == 'total_asc':
                query = query.order_by(OrderModel.total_amount.asc())
            elif sort_by == 'total_desc':
                query = query.order_by(OrderModel.total_amount.desc())
            else:  # newest (default)
                query = query.order_by(OrderModel.created_at.desc())
            
            # Apply pagination
            offset = (page - 1) * per_page
            query = query.offset(offset).limit(per_page)
            
            order_models = query.all()
            orders = [self._to_domain_entity(om) for om in order_models]
            
            return orders, total_count
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_order_statistics(self, filters: Optional[dict] = None) -> dict:
        """
        Get order statistics for dashboard.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            Dictionary with statistics
        """
        session = self._session or get_session()
        try:
            from sqlalchemy import func
            
            query = session.query(OrderModel)
            
            # Apply filters if provided
            if filters:
                if filters.get('start_date'):
                    query = query.filter(OrderModel.created_at >= filters['start_date'])
                if filters.get('end_date'):
                    query = query.filter(OrderModel.created_at <= filters['end_date'])
            
            # Calculate statistics
            stats = {
                'total_revenue': 0,
                'pending_count': 0,
                'shipping_count': 0,  # Fixed: Use SHIPPING instead of PROCESSING
                'completed_count': 0,
                'cancelled_count': 0
            }
            
            # Total revenue (only completed orders)
            revenue_query = query.filter(OrderModel.order_status == OrderStatus.COMPLETED.value)
            total_revenue = session.query(func.sum(OrderModel.total_amount)).filter(
                OrderModel.order_status == OrderStatus.COMPLETED.value
            ).scalar()
            stats['total_revenue'] = float(total_revenue) if total_revenue else 0.0
            
            # Count by status
            stats['pending_count'] = query.filter(OrderModel.order_status == OrderStatus.PENDING.value).count()
            stats['shipping_count'] = query.filter(OrderModel.order_status == OrderStatus.SHIPPING.value).count()  # Fixed: Use SHIPPING
            stats['completed_count'] = query.filter(OrderModel.order_status == OrderStatus.COMPLETED.value).count()
            stats['cancelled_count'] = query.filter(OrderModel.order_status == OrderStatus.CANCELLED.value).count()
            
            return stats
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
