import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class SalesOrderItemCreate(BaseModel):
    product_id: uuid.UUID
    quantity: int


class SalesOrderItemResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID
    product_id: uuid.UUID
    quantity: int

    # Selling price at time of sale
    unit_price: Decimal

    # Purchase cost at time of sale
    purchase_price: Decimal

    total_price: Decimal


class SalesOrderCreate(BaseModel):
    customer_id: uuid.UUID
    order_number: str
    notes: str | None = None
    items: list[SalesOrderItemCreate]


class SalesOrderResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID
    organization_id: uuid.UUID
    customer_id: uuid.UUID
    order_number: str
    status: str
    total_amount: Decimal
    notes: str | None
    created_at: datetime
    updated_at: datetime
    items: list[SalesOrderItemResponse]