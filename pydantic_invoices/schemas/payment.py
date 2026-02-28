from pydantic import BaseModel, Field, ConfigDict
from pydantic_invoices.vo import Money
from datetime import datetime
from typing import Optional


class PaymentBase(BaseModel):
    """Base payment schema."""

    amount: Money.Input = Field(..., description="Payment amount")
    payment_date: datetime = Field(
        default_factory=datetime.now, description="Date payment was received"
    )
    payment_method: str = Field(
        ..., max_length=50, description="Payment method (e.g., Bank Transfer, Cash)"
    )
    reference: Optional[str] = Field(
        None, max_length=100, description="Payment reference number"
    )


class PaymentCreate(PaymentBase):
    """Schema for creating a payment."""

    invoice_id: int = Field(..., description="Invoice ID this payment is for")


class Payment(PaymentBase):
    """Complete payment schema."""

    id: int
    invoice_id: int
    amount: Money

    model_config = ConfigDict(from_attributes=True)
