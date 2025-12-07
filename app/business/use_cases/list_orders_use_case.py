"""
List Orders Use Case - Admin view all orders with filters and pagination
Clean Architecture - Business Layer
"""
from typing import Optional, List
from datetime import datetime
from app.business.ports.order_repository import IOrderRepository
from app.business.ports.user_repository import IUserRepository
from app.domain.exceptions import ValidationException


class ListOrdersInputData:
    """Input data for listing orders"""
    
    def __init__(
        self,
        page: int = 1,
        per_page: int = 20,
        status: Optional[str] = None,
        customer_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        search_query: Optional[str] = None,
        sort_by: str = 'newest'
    ):
        self.page = page
        self.per_page = per_page
        self.status = status
        self.customer_id = customer_id
        self.start_date = start_date
        self.end_date = end_date
        self.search_query = search_query
        self.sort_by = sort_by


class OrderItemOutputData:
    """Output data for a single order in the list"""
    
    def __init__(
        self,
        order_id: int,
        customer_id: int,
        customer_name: str,
        customer_email: str,
        total_amount: float,
        status: str,
        payment_method: str,
        shipping_address: str,
        order_date: datetime,
        item_count: int
    ):
        self.order_id = order_id
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.customer_email = customer_email
        self.total_amount = total_amount
        self.status = status
        self.payment_method = payment_method
        self.shipping_address = shipping_address
        self.order_date = order_date
        self.item_count = item_count


class ListOrdersOutputData:
    """Output data for order listing"""
    
    def __init__(
        self,
        success: bool,
        orders: List[OrderItemOutputData],
        total_orders: int,
        page: int,
        per_page: int,
        total_pages: int,
        # Statistics
        total_revenue: float = 0,
        pending_count: int = 0,
        shipping_count: int = 0,
        completed_count: int = 0,
        cancelled_count: int = 0,
        message: Optional[str] = None
    ):
        self.success = success
        self.orders = orders
        self.total_orders = total_orders
        self.page = page
        self.per_page = per_page
        self.total_pages = total_pages
        self.total_revenue = total_revenue
        self.pending_count = pending_count
        self.shipping_count = shipping_count
        self.completed_count = completed_count
        self.cancelled_count = cancelled_count
        self.message = message


class ListOrdersUseCase:
    """
    Use case for listing all orders with filtering and pagination (Admin only)
    """
    
    def __init__(
        self,
        order_repository: IOrderRepository,
        user_repository: IUserRepository
    ):
        self.order_repository = order_repository
        self.user_repository = user_repository
    
    def execute(self, input_data: ListOrdersInputData) -> ListOrdersOutputData:
        """
        Execute the list orders use case
        
        Args:
            input_data: ListOrdersInputData with filters and pagination
            
        Returns:
            ListOrdersOutputData with orders and statistics
        """
        try:
            # Validate input
            self._validate_input(input_data)
            
            # Build filters
            filters = self._build_filters(input_data)
            
            # Get paginated orders
            orders, total = self.order_repository.find_with_filters(
                filters=filters,
                page=input_data.page,
                per_page=input_data.per_page,
                sort_by=input_data.sort_by
            )
            
            # Enrich orders with customer information
            order_items = []
            for order in orders:
                customer = self.user_repository.find_by_id(order.customer_id)
                customer_name = customer.full_name if customer else "Unknown"
                customer_email = customer.email if customer else ""
                
                order_items.append(OrderItemOutputData(
                    order_id=order.order_id,
                    customer_id=order.customer_id,
                    customer_name=customer_name,
                    customer_email=customer_email,
                    total_amount=order.total_amount,
                    status=order.status.value,
                    payment_method=order.payment_method.value,
                    shipping_address=order.shipping_address,
                    order_date=order.order_date,
                    item_count=len(order.items)
                ))
            
            # Calculate statistics
            stats = self.order_repository.get_order_statistics(filters)
            
            # Calculate total pages
            total_pages = (total + input_data.per_page - 1) // input_data.per_page
            
            return ListOrdersOutputData(
                success=True,
                orders=order_items,
                total_orders=total,
                page=input_data.page,
                per_page=input_data.per_page,
                total_pages=total_pages,
                total_revenue=stats.get('total_revenue', 0),
                pending_count=stats.get('pending_count', 0),
                shipping_count=stats.get('shipping_count', 0),
                completed_count=stats.get('completed_count', 0),
                cancelled_count=stats.get('cancelled_count', 0)
            )
            
        except ValidationException as e:
            return ListOrdersOutputData(
                success=False,
                orders=[],
                total_orders=0,
                page=input_data.page,
                per_page=input_data.per_page,
                total_pages=0,
                message=str(e)
            )
        except Exception as e:
            return ListOrdersOutputData(
                success=False,
                orders=[],
                total_orders=0,
                page=input_data.page,
                per_page=input_data.per_page,
                total_pages=0,
                message=f"Error listing orders: {str(e)}"
            )
    
    def _validate_input(self, input_data: ListOrdersInputData):
        """Validate input data"""
        if input_data.page < 1:
            raise ValidationException("Page must be greater than 0")
        
        if input_data.per_page < 1 or input_data.per_page > 100:
            raise ValidationException("Per page must be between 1 and 100")
        
        if input_data.start_date and input_data.end_date:
            if input_data.start_date > input_data.end_date:
                raise ValidationException("Start date must be before end date")
        
        valid_sort_options = ['newest', 'oldest', 'total_asc', 'total_desc']
        if input_data.sort_by not in valid_sort_options:
            raise ValidationException(f"Invalid sort option. Must be one of: {', '.join(valid_sort_options)}")
    
    def _build_filters(self, input_data: ListOrdersInputData) -> dict:
        """Build filter dictionary from input data"""
        filters = {}
        
        if input_data.status:
            filters['status'] = input_data.status
        
        if input_data.customer_id:
            filters['customer_id'] = input_data.customer_id
        
        if input_data.start_date:
            filters['start_date'] = input_data.start_date
        
        if input_data.end_date:
            filters['end_date'] = input_data.end_date
        
        if input_data.search_query:
            filters['search_query'] = input_data.search_query
        
        return filters
