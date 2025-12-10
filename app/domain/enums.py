"""
Domain Enums - Type-safe enumeration values
"""
from enum import Enum


class UserRole(Enum):
    """User role enumeration"""
    ADMIN = "ADMIN"
    CUSTOMER = "CUSTOMER"
    GUEST = "GUEST"
    
    def __str__(self):
        return self.value
    
    def is_admin(self) -> bool:
        """Check if role is admin"""
        return self == UserRole.ADMIN
    
    def is_customer(self) -> bool:
        """Check if role is customer"""
        return self == UserRole.CUSTOMER
    
    def is_guest(self) -> bool:
        """Check if role is guest"""
        return self == UserRole.GUEST


class OrderStatus(Enum):
    """Order status enumeration"""
    PENDING = "CHO_XAC_NHAN"
    SHIPPING = "DANG_GIAO"
    COMPLETED = "HOAN_THANH"
    CANCELLED = "DA_HUY"
    
    def __str__(self):
        return self.value
    
    def can_transition_to(self, new_status: 'OrderStatus') -> bool:
        """
        Check if status can transition to new status
        
        Valid transitions:
        - PENDING -> SHIPPING, CANCELLED
        - SHIPPING -> COMPLETED
        - Others -> No transition allowed
        """
        if self == OrderStatus.PENDING:
            return new_status in [OrderStatus.SHIPPING, OrderStatus.CANCELLED]
        elif self == OrderStatus.SHIPPING:
            return new_status == OrderStatus.COMPLETED
        return False
    
    def is_terminal(self) -> bool:
        """Check if this is a terminal status (no further transitions)"""
        return self in [OrderStatus.COMPLETED, OrderStatus.CANCELLED]
    
    def is_modifiable(self) -> bool:
        """Check if order can still be modified"""
        return self == OrderStatus.PENDING


class PaymentMethod(Enum):
    """Payment method enumeration"""
    CASH = "TIEN_MAT"
    COD = "COD"  # Cash on Delivery
    BANK_TRANSFER = "CHUYEN_KHOAN"  # Bank transfer / Chuyển khoản
    CREDIT_CARD = "THE_CREDIT"
    
    def __str__(self):
        return self.value
    
    def requires_confirmation(self) -> bool:
        """Check if payment method requires manual confirmation"""
        return self == PaymentMethod.BANK_TRANSFER
