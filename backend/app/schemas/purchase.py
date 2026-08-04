import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PurchaseItemCreate(BaseModel):
    product_id: uuid.UUID
    quantity: int
    unit_cost: Decimal


class PurchaseCreate(BaseModel):
    supplier_id: uuid.UUID
    purchase_number: str
    notes: str | None = None
    items: list[PurchaseItemCreate]


class PurchaseItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    purchase_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    unit_cost: Decimal
    total_cost: Decimal


class PurchaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    supplier_id: uuid.UUID
    purchase_number: str
    status: str
    total_amount: Decimal
    notes: str | None
    created_at: datetime
    updated_at: datetime
    items: list[PurchaseItemResponse] = []