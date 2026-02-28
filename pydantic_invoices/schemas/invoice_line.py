from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, computed_field
from pydantic_invoices.vo import Money


class InvoiceLineBase(BaseModel):
    """Base invoice line schema."""

    description: str = Field(
        ..., min_length=1, max_length=500, description="Line item description"
    )
    quantity: int = Field(..., gt=0, description="Quantity")
    unit_price: Money.Input = Field(..., description="Price per unit")
    tax_rate: Optional[float] = Field(
        default=0.0, ge=0, le=100, description="Tax rate percentage (0-100)"
    )


class InvoiceLineCreate(InvoiceLineBase):
    """Schema for creating an invoice line."""

    pass


class InvoiceLine(InvoiceLineBase):
    """Complete invoice line schema with computed properties."""

    id: int
    invoice_id: int
    unit_price: Money

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total(self) -> Money:
        """Calculate line total (quantity × unit_price)."""
        return self.unit_price * self.quantity

    model_config = ConfigDict(from_attributes=True)
