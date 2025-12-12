"""
Get Order Detail Use Case - View complete order information
Clean Architecture - Business Layer
"""
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.business.ports.order_repository import IOrderRepository
from app.business.ports.user_repository import IUserRepository
from app.business.ports.product_repository import IProductRepository
from app.domain.exceptions import OrderNotFoundException, ValidationException


class OrderDetailItemData:
    """Output data for a single item in the order"""
    
    def __init__(
        self,
        product_id: int,
        product_name: str,
        product_image: Optional[str],
        quantity: int,
        unit_price: float,
        subtotal: float
    ):
        self.product_id = product_id
        self.product_name = product_name
        self.product_image = product_image
        self.quantity = quantity
        self.unit_price = unit_price
        self.subtotal = subtotal


class GetOrderDetailOutputData:
    """Output data for order detail"""
    
    def __init__(
        self,
        success: bool,
        # Order info
        order_id: Optional[int] = None,
        order_date: Optional[datetime] = None,
        status: Optional[str] = None,
        # Customer info
        customer_id: Optional[int] = None,
        customer_name: Optional[str] = None,
        customer_email: Optional[str] = None,
        customer_phone: Optional[str] = None,
        # Shipping info
        shipping_address: Optional[str] = None,
        # Payment info
        payment_method: Optional[str] = None,
        # Items
        items: Optional[List[OrderDetailItemData]] = None,
        # Totals
        subtotal: float = 0,
        tax: float = 0,
        shipping_fee: float = 0,
        total_amount: float = 0,
        message: Optional[str] = None
    ):
        self.success = success
        self.order_id = order_id
        self.order_date = order_date
        self.status = status
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.customer_email = customer_email
        self.customer_phone = customer_phone
        self.shipping_address = shipping_address
        self.payment_method = payment_method
        self.items = items or []
        self.subtotal = subtotal
        self.tax = tax
        self.shipping_fee = shipping_fee
        self.total_amount = total_amount
        self.message = message


class GetOrderDetailUseCase:
    """
    Use case for getting complete order details
    """
    
    def __init__(
        self,
        order_repository: IOrderRepository,
        user_repository: IUserRepository,
        product_repository: IProductRepository
    ):
        self.order_repository = order_repository
        self.user_repository = user_repository
        self.product_repository = product_repository
    
    def execute(self, order_id: int) -> GetOrderDetailOutputData:
        """
        Execute the get order detail use case
        
        Args:
            order_id: ID of the order to retrieve
            
        Returns:
            GetOrderDetailOutputData with complete order information
        """
        try:
            # Validate input
            if order_id <= 0:
                raise ValidationException("Invalid order ID")
            
            # Get order
            order = self.order_repository.find_by_id(order_id)
            if not order:
                raise OrderNotFoundException(order_id)
            
            # Get customer information
            customer = self.user_repository.find_by_id(order.customer_id)
            customer_name = customer.full_name if customer else "Unknown"
            customer_email = customer.email.address if customer and customer.email else ""
            customer_phone = str(customer.phone_number) if customer and customer.phone_number else ""
            
            # Build order items with product details
            order_items = []
            subtotal = 0
            
            for item in order.items:
                product = self.product_repository.find_by_id(item.product_id)
                product_name = product.name if product else "Product Not Found"
                product_image = product.image_url if product else None
                
                # Extract amount from Money object
                unit_price_amount = item.unit_price.amount
                item_subtotal = unit_price_amount * Decimal(str(item.quantity))
                subtotal += item_subtotal
                
                order_items.append(OrderDetailItemData(
                    product_id=item.product_id,
                    product_name=product_name,
                    product_image=product_image,
                    quantity=item.quantity,
                    unit_price=float(unit_price_amount),
                    subtotal=float(item_subtotal)
                ))
            
            # Calculate totals (assuming business rules: 10% tax, $20 shipping)
            tax = subtotal * Decimal("0.10")
            shipping_fee = Decimal("20.0") if subtotal < 500 else Decimal("0")
            total = subtotal + tax + shipping_fee
            
            return GetOrderDetailOutputData(
                success=True,
                order_id=order.id,
                order_date=order.created_at,
                status=order.status.value,
                customer_id=order.customer_id,
                customer_name=customer_name,
                customer_email=customer_email,
                customer_phone=customer_phone,
                shipping_address=order.shipping_address,
                payment_method=order.payment_method.value,
                items=order_items,
                subtotal=float(subtotal),
                tax=float(tax),
                shipping_fee=float(shipping_fee),
                total_amount=float(total)
            )
            
        except OrderNotFoundException as e:
            return GetOrderDetailOutputData(
                success=False,
                message=str(e)
            )
        except ValidationException as e:
            return GetOrderDetailOutputData(
                success=False,
                message=str(e)
            )
        except Exception as e:
            return GetOrderDetailOutputData(
                success=False,
                message=f"Error retrieving order details: {str(e)}"
            )
