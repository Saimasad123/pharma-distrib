import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


# =========================================================
# CREATE SUPPLIER
# =========================================================

class SupplierCreate(BaseModel):
    name: str
    contact_person: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    tax_number: str | None = None


# =========================================================
# UPDATE SUPPLIER
# =========================================================

class SupplierUpdate(BaseModel):
    name: str | None = None
    contact_person: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    tax_number: str | None = None


# =========================================================
# SUPPLIER RESPONSE
# =========================================================

class SupplierResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID
    organization_id: uuid.UUID

    name: str
    contact_person: str | None
    phone: str | None
    email: str | None
    address: str | None
    tax_number: str | None

    is_active: bool

    created_at: datetime
    updated_at: datetime