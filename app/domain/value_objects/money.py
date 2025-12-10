"""
Money Value Object - Immutable representation of monetary values
"""
from decimal import Decimal
from typing import Optional


class Money:
    """Immutable money value object with currency support"""
    
    SUPPORTED_CURRENCIES = ['VND', 'USD']
    
    def __init__(self, amount: Decimal, currency: str = 'VND'):
        """
        Initialize Money value object
        
        Args:
            amount: Decimal amount (or numeric that can be converted to Decimal)
            currency: Currency code (default: VND)
            
        Raises:
            ValueError: If amount is negative or currency not supported
        """
        # Convert to Decimal if not already
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
            
        if amount < 0:
            raise ValueError("Money amount cannot be negative")
        if currency not in self.SUPPORTED_CURRENCIES:
            raise ValueError(f"Currency {currency} not supported. Use: {self.SUPPORTED_CURRENCIES}")
        
        self._amount = amount
        self._currency = currency
    
    @property
    def amount(self) -> Decimal:
        """Get the amount"""
        return self._amount
    
    @property
    def currency(self) -> str:
        """Get the currency"""
        return self._currency
    
    def add(self, other: 'Money') -> 'Money':
        """
        Add two Money objects
        
        Args:
            other: Another Money object
            
        Returns:
            New Money object with sum
            
        Raises:
            ValueError: If currencies don't match
        """
        if self._currency != other._currency:
            raise ValueError(f"Cannot add {self._currency} and {other._currency}")
        return Money(self._amount + other._amount, self._currency)
    
    def subtract(self, other: 'Money') -> 'Money':
        """
        Subtract two Money objects
        
        Args:
            other: Another Money object
            
        Returns:
            New Money object with difference
            
        Raises:
            ValueError: If currencies don't match or result is negative
        """
        if self._currency != other._currency:
            raise ValueError(f"Cannot subtract {other._currency} from {self._currency}")
        if self._amount < other._amount:
            raise ValueError("Cannot subtract larger amount from smaller amount")
        return Money(self._amount - other._amount, self._currency)
    
    def multiply(self, multiplier: Decimal) -> 'Money':
        """
        Multiply Money by a decimal
        
        Args:
            multiplier: Decimal multiplier
            
        Returns:
            New Money object with product
        """
        if multiplier < 0:
            raise ValueError("Multiplier cannot be negative")
        return Money(self._amount * multiplier, self._currency)
    
    def __eq__(self, other) -> bool:
        """Check equality"""
        if not isinstance(other, Money):
            return False
        return self._amount == other._amount and self._currency == other._currency
    
    def __lt__(self, other: 'Money') -> bool:
        """Less than comparison"""
        if self._currency != other._currency:
            raise ValueError(f"Cannot compare {self._currency} and {other._currency}")
        return self._amount < other._amount
    
    def __le__(self, other: 'Money') -> bool:
        """Less than or equal comparison"""
        return self == other or self < other
    
    def __gt__(self, other: 'Money') -> bool:
        """Greater than comparison"""
        if self._currency != other._currency:
            raise ValueError(f"Cannot compare {self._currency} and {other._currency}")
        return self._amount > other._amount
    
    def __ge__(self, other: 'Money') -> bool:
        """Greater than or equal comparison"""
        return self == other or self > other
    
    def __str__(self) -> str:
        """String representation"""
        if self._currency == 'VND':
            return f"{self._amount:,.0f} ₫"
        return f"{self._currency} {self._amount:,.2f}"
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"Money(amount={self._amount}, currency='{self._currency}')"
