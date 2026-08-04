import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.database import get_db
from app.models import (
    InventoryTransaction,
    OrganizationMember,
    Product,
    User,
)
from app.schemas.inventory import (
    InventoryTransactionCreate,
    InventoryTransactionResponse,
    InventoryTransactionType,
)


router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
)


async def get_user_organization_id(
    current_user: User,
    db: AsyncSession,
) -> uuid.UUID:
    result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.user_id
            == current_user.id
        )
    )

    membership = result.scalar_one_or_none()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization membership not found.",
        )

    return membership.organization_id


@router.post(
    "/transactions",
    response_model=InventoryTransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_inventory_transaction(
    data: InventoryTransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    organization_id = await get_user_organization_id(
        current_user,
        db,
    )

    # Find product belonging to user's organization
    result = await db.execute(
        select(Product).where(
            Product.id == data.product_id,
            Product.organization_id
            == organization_id,
            Product.is_active.is_(True),
        )
    )

    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    previous_stock = product.current_stock

    # STOCK_IN
    if (
        data.transaction_type
        == InventoryTransactionType.STOCK_IN
    ):
        if data.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "STOCK_IN quantity must be "
                    "greater than zero."
                ),
            )

        new_stock = (
            previous_stock
            + data.quantity
        )

    # STOCK_OUT
    elif (
        data.transaction_type
        == InventoryTransactionType.STOCK_OUT
    ):
        if data.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "STOCK_OUT quantity must be "
                    "greater than zero."
                ),
            )

        if data.quantity > previous_stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Insufficient stock. "
                    f"Available stock: "
                    f"{previous_stock}."
                ),
            )

        new_stock = (
            previous_stock
            - data.quantity
        )

    # ADJUSTMENT
    else:
        if data.quantity == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Adjustment quantity "
                    "cannot be zero."
                ),
            )

        new_stock = (
            previous_stock
            + data.quantity
        )

        if new_stock < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Stock adjustment cannot "
                    "result in negative stock."
                ),
            )

    # Update product stock
    product.current_stock = new_stock

    # Create transaction record
    transaction = InventoryTransaction(
        organization_id=organization_id,
        product_id=product.id,
        transaction_type=(
            data.transaction_type.value
        ),
        quantity=data.quantity,
        previous_stock=previous_stock,
        new_stock=new_stock,
        reason=data.reason,
        notes=data.notes,
    )

    db.add(transaction)

    await db.commit()

    await db.refresh(transaction)

    return transaction


@router.get(
    "/transactions",
    response_model=list[
        InventoryTransactionResponse
    ],
)
async def get_inventory_transactions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    organization_id = await get_user_organization_id(
        current_user,
        db,
    )

    result = await db.execute(
        select(InventoryTransaction)
        .where(
            InventoryTransaction.organization_id
            == organization_id
        )
        .order_by(
            InventoryTransaction.created_at.desc()
        )
    )

    transactions = result.scalars().all()

    return list(transactions)


@router.get(
    "/transactions/{product_id}",
    response_model=list[
        InventoryTransactionResponse
    ],
)
async def get_product_inventory_history(
    product_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    organization_id = await get_user_organization_id(
        current_user,
        db,
    )

    # Verify product belongs to organization
    product_result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.organization_id
            == organization_id,
        )
    )

    product = product_result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    result = await db.execute(
        select(InventoryTransaction)
        .where(
            InventoryTransaction.product_id
            == product_id,
            InventoryTransaction.organization_id
            == organization_id,
        )
        .order_by(
            InventoryTransaction.created_at.desc()
        )
    )

    transactions = result.scalars().all()

    return list(transactions)