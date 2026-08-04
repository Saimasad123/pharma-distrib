import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProductAlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    sku: str
    current_stock: int
    minimum_stock_level: int
    sale_price: Decimal
    batch_number: str | None
    expiry_date: date | None