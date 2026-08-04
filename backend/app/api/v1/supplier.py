import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.database import get_db
from app.models import Supplier, OrganizationMember, User
from app.schemas.supplier import (
    SupplierCreate,
    SupplierResponse,
    SupplierUpdate,
)


router = APIRouter(
    prefix="/suppliers",
    tags=["Suppliers"],
)


async def get_user_organization_id(
    current_user: User,
    db: AsyncSession,
) -> uuid.UUID:
    """
    Get organization ID for the current user.
    """

    result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.user_id == current_user.id
        )
    )

    membership = result.scalar_one_or_none()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization membership not found.",
        )

    return membership.organization_id


# =========================================================
# CREATE SUPPLIER
# =========================================================

@router.post(
    "",
    response_model=SupplierResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_supplier(
    data: SupplierCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new supplier.
    """

    organization_id = await get_user_organization_id(
        current_user,
        db,
    )

    supplier = Supplier(
        organization_id=organization_id,
        name=data.name,
        contact_person=data.contact_person,
        phone=data.phone,
        email=data.email,
        address=data.address,
        tax_number=data.tax_number,
    )

    db.add(supplier)

    await db.commit()
    await db.refresh(supplier)

    return supplier


# =========================================================
# GET ALL ACTIVE SUPPLIERS
# =========================================================

@router.get(
    "",
    response_model=list[SupplierResponse],
)
async def get_suppliers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all active suppliers for the organization.
    """

    organization_id = await get_user_organization_id(
        current_user,
        db,
    )

    result = await db.execute(
        select(Supplier)
        .where(
            Supplier.organization_id == organization_id,
            Supplier.is_active.is_(True),
        )
        .order_by(Supplier.created_at.desc())
    )

    return result.scalars().all()


# =========================================================
# GET SINGLE ACTIVE SUPPLIER
# =========================================================

@router.get(
    "/{supplier_id}",
    response_model=SupplierResponse,
)
async def get_supplier(
    supplier_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get one active supplier.
    """

    organization_id = await get_user_organization_id(
        current_user,
        db,
    )

    result = await db.execute(
        select(Supplier).where(
            Supplier.id == supplier_id,
            Supplier.organization_id == organization_id,
            Supplier.is_active.is_(True),
        )
    )

    supplier = result.scalar_one_or_none()

    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found.",
        )

    return supplier


# =========================================================
# UPDATE SUPPLIER
# =========================================================

@router.put(
    "/{supplier_id}",
    response_model=SupplierResponse,
)
async def update_supplier(
    supplier_id: uuid.UUID,
    data: SupplierUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update an active supplier.
    """

    organization_id = await get_user_organization_id(
        current_user,
        db,
    )

    result = await db.execute(
        select(Supplier).where(
            Supplier.id == supplier_id,
            Supplier.organization_id == organization_id,
            Supplier.is_active.is_(True),
        )
    )

    supplier = result.scalar_one_or_none()

    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found.",
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            supplier,
            field,
            value,
        )

    await db.commit()
    await db.refresh(supplier)

    return supplier


# =========================================================
# SOFT DELETE SUPPLIER
# =========================================================

@router.delete(
    "/{supplier_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_supplier(
    supplier_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Soft delete a supplier.
    """

    organization_id = await get_user_organization_id(
        current_user,
        db,
    )

    result = await db.execute(
        select(Supplier).where(
            Supplier.id == supplier_id,
            Supplier.organization_id == organization_id,
            Supplier.is_active.is_(True),
        )
    )

    supplier = result.scalar_one_or_none()

    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found.",
        )

    supplier.is_active = False

    await db.commit()

    return None