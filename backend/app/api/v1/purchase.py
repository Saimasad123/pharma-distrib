import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.database import get_db
from app.models import (
    InventoryTransaction,
    OrganizationMember,
    Product,
    Purchase,
    PurchaseItem,
    Supplier,
    User,
)
from app.schemas.purchase import (
    PurchaseCreate,
    PurchaseResponse,
)


router = APIRouter(
    prefix="/purchases",
    tags=["Purchases"],
)


async def get_user_organization_id(
    current_user: User,
    db: AsyncSession,
) -> uuid.UUID:
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


@router.post(
    "",
    response_model=PurchaseResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_purchase(
    data: PurchaseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    organization_id = await get_user_organization_id(
        current_user,
        db,
    )

    # Check supplier belongs to the organization
    result = await db.execute(
        select(Supplier).where(
            Supplier.id == data.supplier_id,
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

    if not data.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Purchase must contain at least one item.",
        )

    # Check duplicate purchase number
    result = await db.execute(
        select(Purchase).where(
            Purchase.organization_id == organization_id,
            Purchase.purchase_number
            == data.purchase_number,
        )
    )

    existing_purchase = result.scalar_one_or_none()

    if existing_purchase:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Purchase number already exists.",
        )

    purchase = Purchase(
        organization_id=organization_id,
        supplier_id=data.supplier_id,
        purchase_number=data.purchase_number,
        status="PENDING",
        total_amount=Decimal("0.00"),
        notes=data.notes,
    )

    db.add(purchase)

    await db.flush()

    total_amount = Decimal("0.00")

    for item_data in data.items:

        if item_data.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be greater than zero.",
            )

        if item_data.unit_cost < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unit cost cannot be negative.",
            )

        # Check product belongs to organization
        result = await db.execute(
            select(Product).where(
                Product.id == item_data.product_id,
                Product.organization_id
                == organization_id,
                Product.is_active.is_(True),
            )
        )

        product = result.scalar_one_or_none()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Product {item_data.product_id} "
                    "not found."
                ),
            )

        total_cost = (
            item_data.unit_cost
            * item_data.quantity
        )

        purchase_item = PurchaseItem(
            purchase_id=purchase.id,
            product_id=product.id,
            quantity=item_data.quantity,
            unit_cost=item_data.unit_cost,
            total_cost=total_cost,
        )

        db.add(purchase_item)

        total_amount += total_cost

    purchase.total_amount = total_amount

    await db.commit()

    # Reload purchase
    result = await db.execute(
        select(Purchase).where(
            Purchase.id == purchase.id
        )
    )

    purchase = result.scalar_one()

    return purchase


@router.get(
    "",
    response_model=list[PurchaseResponse],
)
async def get_purchases(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    organization_id = await get_user_organization_id(
        current_user,
        db,
    )

    result = await db.execute(
        select(Purchase)
        .where(
            Purchase.organization_id
            == organization_id
        )
        .order_by(
            Purchase.created_at.desc()
        )
    )

    return result.scalars().all()


@router.get(
    "/{purchase_id}",
    response_model=PurchaseResponse,
)
async def get_purchase(
    purchase_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    organization_id = await get_user_organization_id(
        current_user,
        db,
    )

    result = await db.execute(
        select(Purchase).where(
            Purchase.id == purchase_id,
            Purchase.organization_id
            == organization_id,
        )
    )

    purchase = result.scalar_one_or_none()

    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase not found.",
        )

    return purchase


@router.post(
    "/{purchase_id}/receive",
    response_model=PurchaseResponse,
)
async def receive_purchase(
    purchase_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    organization_id = await get_user_organization_id(
        current_user,
        db,
    )

    # Get purchase
    result = await db.execute(
        select(Purchase).where(
            Purchase.id == purchase_id,
            Purchase.organization_id
            == organization_id,
        )
    )

    purchase = result.scalar_one_or_none()

    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase not found.",
        )

    # Prevent receiving twice
    if purchase.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Purchase cannot be received. "
                f"Current status: {purchase.status}"
            ),
        )

    # Get purchase items
    result = await db.execute(
        select(PurchaseItem).where(
            PurchaseItem.purchase_id
            == purchase.id
        )
    )

    purchase_items = result.scalars().all()

    if not purchase_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Purchase has no items.",
        )

    # Process every item
    for purchase_item in purchase_items:

        # Lock product row to prevent stock conflicts
        result = await db.execute(
            select(Product)
            .where(
                Product.id
                == purchase_item.product_id,
                Product.organization_id
                == organization_id,
            )
            .with_for_update()
        )

        product = result.scalar_one_or_none()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Product "
                    f"{purchase_item.product_id} "
                    "not found."
                ),
            )

        previous_stock = product.current_stock

        new_stock = (
            previous_stock
            + purchase_item.quantity
        )

        # Update stock
        product.current_stock = new_stock

        # Create inventory transaction
        transaction = InventoryTransaction(
            organization_id=organization_id,
            product_id=product.id,
            transaction_type="STOCK_IN",
            quantity=purchase_item.quantity,
            previous_stock=previous_stock,
            new_stock=new_stock,
            reason="Purchase received",
            notes=(
                f"Purchase "
                f"{purchase.purchase_number} "
                f"received from supplier."
            ),
        )

        db.add(transaction)

    # Mark purchase as received
    purchase.status = "RECEIVED"

    await db.commit()

    # Reload purchase
    result = await db.execute(
        select(Purchase).where(
            Purchase.id == purchase.id
        )
    )

    purchase = result.scalar_one()

    return purchase