import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class InventoryTransactionType(str, Enum):
    STOCK_IN = "STOCK_IN"
    STOCK_OUT = "STOCK_OUT"
    ADJUSTMENT = "ADJUSTMENT"


class InventoryTransactionCreate(BaseModel):
    product_id: uuid.UUID

    transaction_type: InventoryTransactionType

    quantity: int = Field(
        ...,
        description=(
            "Quantity to add or remove. "
            "For ADJUSTMENT, use positive or negative values."
        ),
    )

    reason: str | None = None

    notes: str | None = None


class InventoryTransactionResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    product_id: uuid.UUID
    transaction_type: InventoryTransactionType
    quantity: int
    previous_stock: int
    new_stock: int
    reason: str | None
    notes: str | None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }