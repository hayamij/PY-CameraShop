"""
Comprehensive test suite for Money value object
Following Clean Architecture principles - Domain layer testing
Target: 56% → 100% coverage
"""
import pytest
from decimal import Decimal
from app.domain.value_objects.money import Money


class TestMoneyInitialization:
    """Test Money object creation and validation"""
    
    def test_create_money_with_decimal_amount(self):
        """TC1: Create Money with Decimal amount"""
        money = Money(Decimal("1000000"), "VND")
        assert money.amount == Decimal("1000000")
        assert money.currency == "VND"
    
    def test_create_money_with_integer_amount(self):
        """TC2: Create Money with integer (auto-converts to Decimal)"""
        money = Money(1000000, "VND")
        assert money.amount == Decimal("1000000")
        assert money.currency == "VND"
    
    def test_create_money_with_float_amount(self):
        """TC3: Create Money with float (auto-converts to Decimal)"""
        money = Money(99.99, "USD")
        assert money.amount == Decimal("99.99")
        assert money.currency == "USD"
    
    def test_create_money_with_string_amount(self):
        """TC4: Create Money with string number (auto-converts)"""
        money = Money("5000000", "VND")
        assert money.amount == Decimal("5000000")
        assert money.currency == "VND"
    
    def test_create_money_default_currency_vnd(self):
        """TC5: Default currency is VND"""
        money = Money(Decimal("1000"))
        assert money.currency == "VND"
    
    def test_create_money_with_zero_amount(self):
        """TC6: Create Money with zero amount (valid)"""
        money = Money(Decimal("0"), "VND")
        assert money.amount == Decimal("0")
    
    def test_create_money_with_negative_amount_raises_error(self):
        """TC7: Negative amount raises ValueError"""
        with pytest.raises(ValueError, match="Money amount cannot be negative"):
            Money(Decimal("-1000"), "VND")
    
    def test_create_money_with_unsupported_currency_raises_error(self):
        """TC8: Unsupported currency raises ValueError"""
        with pytest.raises(ValueError, match="Currency EUR not supported"):
            Money(Decimal("1000"), "EUR")
    
    def test_supported_currencies_list(self):
        """TC9: Verify supported currencies"""
        assert "VND" in Money.SUPPORTED_CURRENCIES
        assert "USD" in Money.SUPPORTED_CURRENCIES
        assert len(Money.SUPPORTED_CURRENCIES) == 2


class TestMoneyProperties:
    """Test Money immutable properties"""
    
    def test_amount_property_accessible(self):
        """TC10: Amount property returns correct value"""
        money = Money(Decimal("2500000"), "VND")
        assert money.amount == Decimal("2500000")
    
    def test_currency_property_accessible(self):
        """TC11: Currency property returns correct value"""
        money = Money(Decimal("100"), "USD")
        assert money.currency == "USD"
    
    def test_money_is_immutable(self):
        """TC12: Cannot modify Money attributes directly"""
        money = Money(Decimal("1000000"), "VND")
        with pytest.raises(AttributeError):
            money.amount = Decimal("2000000")
        with pytest.raises(AttributeError):
            money.currency = "USD"


class TestMoneyAddition:
    """Test Money addition operations"""
    
    def test_add_same_currency(self):
        """TC13: Add two Money objects with same currency"""
        m1 = Money(Decimal("1000000"), "VND")
        m2 = Money(Decimal("500000"), "VND")
        result = m1.add(m2)
        
        assert result.amount == Decimal("1500000")
        assert result.currency == "VND"
        # Original objects unchanged (immutability)
        assert m1.amount == Decimal("1000000")
        assert m2.amount == Decimal("500000")
    
    def test_add_zero_amount(self):
        """TC14: Add zero Money"""
        m1 = Money(Decimal("1000000"), "VND")
        m2 = Money(Decimal("0"), "VND")
        result = m1.add(m2)
        
        assert result.amount == Decimal("1000000")
    
    def test_add_different_currencies_raises_error(self):
        """TC15: Adding different currencies raises ValueError"""
        m1 = Money(Decimal("1000000"), "VND")
        m2 = Money(Decimal("100"), "USD")
        
        with pytest.raises(ValueError, match="Cannot add VND and USD"):
            m1.add(m2)
    
    def test_add_large_amounts(self):
        """TC16: Add large amounts"""
        m1 = Money(Decimal("999999999999"), "VND")
        m2 = Money(Decimal("1"), "VND")
        result = m1.add(m2)
        
        assert result.amount == Decimal("1000000000000")


class TestMoneySubtraction:
    """Test Money subtraction operations"""
    
    def test_subtract_same_currency(self):
        """TC17: Subtract two Money objects with same currency"""
        m1 = Money(Decimal("1000000"), "VND")
        m2 = Money(Decimal("300000"), "VND")
        result = m1.subtract(m2)
        
        assert result.amount == Decimal("700000")
        assert result.currency == "VND"
    
    def test_subtract_to_zero(self):
        """TC18: Subtract equal amounts results in zero"""
        m1 = Money(Decimal("1000000"), "VND")
        m2 = Money(Decimal("1000000"), "VND")
        result = m1.subtract(m2)
        
        assert result.amount == Decimal("0")
    
    def test_subtract_zero_amount(self):
        """TC19: Subtract zero Money"""
        m1 = Money(Decimal("1000000"), "VND")
        m2 = Money(Decimal("0"), "VND")
        result = m1.subtract(m2)
        
        assert result.amount == Decimal("1000000")
    
    def test_subtract_larger_from_smaller_raises_error(self):
        """TC20: Subtracting larger amount raises ValueError"""
        m1 = Money(Decimal("500000"), "VND")
        m2 = Money(Decimal("1000000"), "VND")
        
        with pytest.raises(ValueError, match="Cannot subtract larger amount from smaller amount"):
            m1.subtract(m2)
    
    def test_subtract_different_currencies_raises_error(self):
        """TC21: Subtracting different currencies raises ValueError"""
        m1 = Money(Decimal("1000000"), "VND")
        m2 = Money(Decimal("100"), "USD")
        
        with pytest.raises(ValueError, match="Cannot subtract USD from VND"):
            m1.subtract(m2)


class TestMoneyMultiplication:
    """Test Money multiplication operations"""
    
    def test_multiply_by_positive_integer(self):
        """TC22: Multiply Money by positive integer"""
        money = Money(Decimal("1000000"), "VND")
        result = money.multiply(Decimal("3"))
        
        assert result.amount == Decimal("3000000")
        assert result.currency == "VND"
    
    def test_multiply_by_decimal(self):
        """TC23: Multiply Money by decimal"""
        money = Money(Decimal("1000000"), "VND")
        result = money.multiply(Decimal("1.5"))
        
        assert result.amount == Decimal("1500000")
        assert result.currency == "VND"
    
    def test_multiply_by_zero(self):
        """TC24: Multiply Money by zero"""
        money = Money(Decimal("1000000"), "VND")
        result = money.multiply(Decimal("0"))
        
        assert result.amount == Decimal("0")
    
    def test_multiply_by_one(self):
        """TC25: Multiply Money by one (identity)"""
        money = Money(Decimal("1000000"), "VND")
        result = money.multiply(Decimal("1"))
        
        assert result.amount == Decimal("1000000")
    
    def test_multiply_by_fractional(self):
        """TC26: Multiply Money by fraction (discount scenario)"""
        money = Money(Decimal("1000000"), "VND")
        result = money.multiply(Decimal("0.9"))  # 10% discount
        
        assert result.amount == Decimal("900000")
    
    def test_multiply_by_negative_raises_error(self):
        """TC27: Multiplying by negative number raises ValueError"""
        money = Money(Decimal("1000000"), "VND")
        
        with pytest.raises(ValueError, match="Multiplier cannot be negative"):
            money.multiply(Decimal("-2"))


class TestMoneyComparison:
    """Test Money comparison operations"""
    
    def test_equality_same_amount_and_currency(self):
        """TC28: Equal Money objects"""
        m1 = Money(Decimal("1000000"), "VND")
        m2 = Money(Decimal("1000000"), "VND")
        
        assert m1 == m2
    
    def test_equality_different_amounts(self):
        """TC29: Different amounts are not equal"""
        m1 = Money(Decimal("1000000"), "VND")
        m2 = Money(Decimal("2000000"), "VND")
        
        assert m1 != m2
    
    def test_equality_different_currencies(self):
        """TC30: Different currencies are not equal"""
        m1 = Money(Decimal("1000"), "VND")
        m2 = Money(Decimal("1000"), "USD")
        
        assert m1 != m2
    
    def test_equality_with_non_money_object(self):
        """TC31: Money not equal to non-Money object"""
        money = Money(Decimal("1000000"), "VND")
        
        assert money != 1000000
        assert money != "1000000"
        assert money != None
    
    def test_less_than_same_currency(self):
        """TC32: Less than comparison"""
        m1 = Money(Decimal("500000"), "VND")
        m2 = Money(Decimal("1000000"), "VND")
        
        assert m1 < m2
        assert not (m2 < m1)
    
    def test_less_than_different_currencies_raises_error(self):
        """TC33: Less than comparison with different currencies raises error"""
        m1 = Money(Decimal("1000"), "VND")
        m2 = Money(Decimal("10"), "USD")
        
        with pytest.raises(ValueError, match="Cannot compare VND and USD"):
            m1 < m2
    
    def test_less_than_or_equal(self):
        """TC34: Less than or equal comparison"""
        m1 = Money(Decimal("1000000"), "VND")
        m2 = Money(Decimal("1000000"), "VND")
        m3 = Money(Decimal("2000000"), "VND")
        
        assert m1 <= m2  # Equal
        assert m1 <= m3  # Less than
        assert not (m3 <= m1)
    
    def test_greater_than_same_currency(self):
        """TC35: Greater than comparison"""
        m1 = Money(Decimal("2000000"), "VND")
        m2 = Money(Decimal("1000000"), "VND")
        
        assert m1 > m2
        assert not (m2 > m1)
    
    def test_greater_than_different_currencies_raises_error(self):
        """TC36: Greater than comparison with different currencies raises error"""
        m1 = Money(Decimal("1000"), "VND")
        m2 = Money(Decimal("10"), "USD")
        
        with pytest.raises(ValueError, match="Cannot compare VND and USD"):
            m1 > m2
    
    def test_greater_than_or_equal(self):
        """TC37: Greater than or equal comparison"""
        m1 = Money(Decimal("2000000"), "VND")
        m2 = Money(Decimal("2000000"), "VND")
        m3 = Money(Decimal("1000000"), "VND")
        
        assert m1 >= m2  # Equal
        assert m1 >= m3  # Greater than
        assert not (m3 >= m1)


class TestMoneyStringRepresentation:
    """Test Money string formatting"""
    
    def test_str_representation_vnd(self):
        """TC38: VND string format with dong symbol"""
        money = Money(Decimal("1000000"), "VND")
        result = str(money)
        
        assert "1,000,000" in result
        assert "₫" in result
    
    def test_str_representation_vnd_with_zero(self):
        """TC39: VND zero amount formatting"""
        money = Money(Decimal("0"), "VND")
        result = str(money)
        
        assert "0" in result
        assert "₫" in result
    
    def test_str_representation_usd(self):
        """TC40: USD string format"""
        money = Money(Decimal("99.99"), "USD")
        result = str(money)
        
        assert "USD" in result
        assert "99.99" in result
    
    def test_str_representation_large_amount(self):
        """TC41: Large amount formatting"""
        money = Money(Decimal("123456789"), "VND")
        result = str(money)
        
        assert "123,456,789" in result
    
    def test_repr_representation(self):
        """TC42: Developer representation"""
        money = Money(Decimal("1000000"), "VND")
        result = repr(money)
        
        assert "Money" in result
        assert "1000000" in result
        assert "VND" in result
    
    def test_repr_for_debugging(self):
        """TC43: Repr useful for debugging"""
        money = Money(Decimal("99.50"), "USD")
        result = repr(money)
        
        assert "amount=99.5" in result or "amount=99.50" in result
        assert "currency='USD'" in result


class TestMoneyEdgeCases:
    """Test edge cases and special scenarios"""
    
    def test_very_large_amount(self):
        """TC44: Handle very large amounts"""
        large_amount = Decimal("999999999999999999")
        money = Money(large_amount, "VND")
        
        assert money.amount == large_amount
    
    def test_very_small_decimal_amount(self):
        """TC45: Handle small decimal amounts (USD cents)"""
        money = Money(Decimal("0.01"), "USD")
        
        assert money.amount == Decimal("0.01")
    
    def test_precision_preservation(self):
        """TC46: Decimal precision preserved in operations"""
        m1 = Money(Decimal("10.12"), "USD")
        m2 = Money(Decimal("5.34"), "USD")
        result = m1.add(m2)
        
        assert result.amount == Decimal("15.46")
    
    def test_chained_operations(self):
        """TC47: Chain multiple operations"""
        money = Money(Decimal("1000000"), "VND")
        result = money.multiply(Decimal("2")).add(Money(Decimal("500000"), "VND"))
        
        assert result.amount == Decimal("2500000")
    
    def test_multiple_instances_independent(self):
        """TC48: Multiple Money instances are independent"""
        m1 = Money(Decimal("1000000"), "VND")
        m2 = Money(Decimal("2000000"), "VND")
        m3 = m1.add(m2)
        
        # Original instances unchanged
        assert m1.amount == Decimal("1000000")
        assert m2.amount == Decimal("2000000")
        assert m3.amount == Decimal("3000000")
    
    def test_hash_consistency_for_equal_objects(self):
        """TC49: Equal Money objects can be compared"""
        m1 = Money(Decimal("1000000"), "VND")
        m2 = Money(Decimal("1000000"), "VND")
        
        # Should be equal
        assert m1 == m2
    
    def test_zero_amount_operations(self):
        """TC50: Operations with zero Money"""
        zero = Money(Decimal("0"), "VND")
        money = Money(Decimal("1000000"), "VND")
        
        # Add zero
        assert money.add(zero).amount == money.amount
        # Subtract zero
        assert money.subtract(zero).amount == money.amount
        # Multiply zero
        assert zero.multiply(Decimal("100")).amount == Decimal("0")
