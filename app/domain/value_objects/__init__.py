"""Value Objects - Immutable domain concepts"""
from .money import Money
from .email import Email
from .phone_number import PhoneNumber

__all__ = ['Money', 'Email', 'PhoneNumber']
