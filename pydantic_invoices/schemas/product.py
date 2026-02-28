from pydantic import BaseModel, Field, ConfigDict
from pydantic_invoices.vo import Money
from typing import Optional


class ProductBase(BaseModel):
    """Base product schema with common fields."""

    code: str = Field(
        ..., min_length=1, max_length=50, description="Unique product code"
    )
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    description: Optional[str] = Field(
        None, max_length=1000, description="Product description"
    )

    # Pricing
    unit_price: Money.Input = Field(..., description="Price per unit")
    currency: str = Field(
        default="USD", max_length=3, description="Currency code (e.g., USD, EUR)"
    )

    # Tax
    tax_rate: Optional[float] = Field(
        None, ge=0, le=100, description="Tax rate percentage (0-100)"
    )

    # Inventory
    unit: str = Field(
        default="pcs",
        max_length=20,
        description="Unit of measurement (pcs, hours, kg, etc.)",
    )
    is_active: bool = Field(default=True, description="Whether this product is active")

    # Categorization
    category: Optional[str] = Field(
        None, max_length=100, description="Product category"
    )
    preferred_template: Optional[str] = Field(
        None, max_length=255, description="Preferred invoice template filename"
    )


class ProductCreate(ProductBase):
    """Schema for creating a product."""

    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product."""

    code: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    unit_price: Optional[Money.Input] = Field(None)
    currency: Optional[str] = Field(None, max_length=3)
    tax_rate: Optional[float] = Field(None, ge=0, le=100)
    unit: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None
    category: Optional[str] = Field(None, max_length=100)


class Product(ProductBase):
    """Complete product schema."""

    id: int
    unit_price: Money

    model_config = ConfigDict(from_attributes=True)
