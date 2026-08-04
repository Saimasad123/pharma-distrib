from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=255,
    )

    sku: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    generic_name: str | None = None
    brand_name: str | None = None
    category: str | None = None
    manufacturer: str | None = None

    unit: str = Field(
        default="piece",
        max_length=50,
    )

    purchase_price: Decimal = Field(
        ...,
        ge=0,
    )

    sale_price: Decimal = Field(
        ...,
        ge=0,
    )

    current_stock: int = Field(
        default=0,
        ge=0,
    )

    minimum_stock_level: int = Field(
        default=10,
        ge=0,
    )

    batch_number: str | None = None
    expiry_date: date | None = None
    description: str | None = None


class ProductUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    sku: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    generic_name: str | None = None
    brand_name: str | None = None
    category: str | None = None
    manufacturer: str | None = None
    unit: str | None = None

    purchase_price: Decimal | None = Field(
        default=None,
        ge=0,
    )

    sale_price: Decimal | None = Field(
        default=None,
        ge=0,
    )

    current_stock: int | None = Field(
        default=None,
        ge=0,
    )

    minimum_stock_level: int | None = Field(
        default=None,
        ge=0,
    )

    batch_number: str | None = None
    expiry_date: date | None = None
    description: str | None = None
    is_active: bool | None = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    organization_id: UUID

    name: str
    sku: str

    generic_name: str | None
    brand_name: str | None
    category: str | None
    manufacturer: str | None

    unit: str

    purchase_price: Decimal
    sale_price: Decimal

    current_stock: int
    minimum_stock_level: int

    batch_number: str | None
    expiry_date: date | None

    description: str | None

    is_active: bool