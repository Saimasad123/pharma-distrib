import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.database import get_db
from app.models import Customer, OrganizationMember, User
from app.schemas.customer import (
    CustomerCreate,
    CustomerResponse,
    CustomerUpdate,
)


router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)


async def get_user_organization_id(
    current_user: User,
    db: AsyncSession,
) -> uuid.UUID:
    """
    Get the organization ID for the currently authenticated user.
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
# CREATE CUSTOMER
# =========================================================

@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_customer(
    data: CustomerCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new customer for the current user's organization.
    """

    organization_id = await get_user_organization_id(
        current_user,
        db,
    )

    customer = Customer(
        organization_id=organization_id,
        name=data.name,
        contact_person=data.contact_person,
        phone=data.phone,
        email=data.email,
        address=data.address,
        tax_number=data.tax_number,
    )

    db.add(customer)

    await db.commit()
    await db.refresh(customer)

    return customer


# =========================================================
# GET ALL ACTIVE CUSTOMERS
# =========================================================

@router.get(
    "",
    response_model=list[CustomerResponse],
)
async def get_customers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all active customers belonging to
    the current user's organization.
    """

    organization_id = await get_user_organization_id(
        current_user,
        db,
    )

    result = await db.execute(
        select(Customer)
        .where(
            Customer.organization_id == organization_id,
            Customer.is_active.is_(True),
        )
        .order_by(Customer.created_at.desc())
    )

    customers = result.scalars().all()

    return customers


# =========================================================
# GET SINGLE ACTIVE CUSTOMER
# =========================================================

@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
)
async def get_customer(
    customer_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single active customer belonging to
    the current user's organization.
    """

    organization_id = await get_user_organization_id(
        current_user,
        db,
    )

    result = await db.execute(
        select(Customer).where(
            Customer.id == customer_id,
            Customer.organization_id == organization_id,
            Customer.is_active.is_(True),
        )
    )

    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        )

    return customer


# =========================================================
# UPDATE CUSTOMER
# =========================================================

@router.put(
    "/{customer_id}",
    response_model=CustomerResponse,
)
async def update_customer(
    customer_id: uuid.UUID,
    data: CustomerUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update an active customer belonging to
    the current user's organization.
    """

    organization_id = await get_user_organization_id(
        current_user,
        db,
    )

    result = await db.execute(
        select(Customer).where(
            Customer.id == customer_id,
            Customer.organization_id == organization_id,
            Customer.is_active.is_(True),
        )
    )

    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            customer,
            field,
            value,
        )

    await db.commit()
    await db.refresh(customer)

    return customer


# =========================================================
# SOFT DELETE CUSTOMER
# =========================================================

@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_customer(
    customer_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Soft delete a customer by setting is_active to False.
    """

    organization_id = await get_user_organization_id(
        current_user,
        db,
    )

    result = await db.execute(
        select(Customer).where(
            Customer.id == customer_id,
            Customer.organization_id == organization_id,
            Customer.is_active.is_(True),
        )
    )

    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        )

    customer.is_active = False

    await db.commit()

    return None