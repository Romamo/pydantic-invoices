import pytest
from decimal import Decimal
from pydantic_invoices.vo import Money

def test_money_basic_parsing():
    assert Money("100.50").amount == Decimal("100.50")
    assert Money(100.50).amount == Decimal("100.5")
    assert Money(100).amount == Decimal("100")

def test_money_regional_parsing():
    # US/UK style
    assert Money("1,234.56").amount == Decimal("1234.56")
    # German/EU style
    assert Money("1.234,56").amount == Decimal("1234.56")
    # Simple comma
    assert Money("1234,56").amount == Decimal("1234.56")
    # No thousand separator
    assert Money("1234.56").amount == Decimal("1234.56")

def test_money_arithmetic():
    m1 = Money("10.50")
    m2 = Money("5.25")
    
    assert (m1 + m2).amount == Decimal("15.75")
    assert (m1 - m2).amount == Decimal("5.25")
    assert (m1 * 2).amount == Decimal("21.00")

def test_money_different_currencies():
    m1 = Money("10.50", "USD")
    m2 = Money("5.25", "EUR")
    
    with pytest.raises(ValueError, match="Cannot add different currencies"):
        m1 + m2

def test_money_invalid_parsing():
    with pytest.raises(ValueError, match="Invalid format for Money"):
        Money("invalid")

def test_money_pydantic_validation():
    from pydantic import BaseModel
    
    class Model(BaseModel):
        price: Money
        
    m = Model(price="1.234,56")
    assert isinstance(m.price, Money)
    assert m.price.amount == Decimal("1234.56")
    
    # Check serialization
    assert m.model_dump()["price"] == "1234.56"
