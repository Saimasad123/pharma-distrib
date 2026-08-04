import uuid
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user_context
from app.database import get_db
from app.models import Product
from app.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from app.schemas.product_alert import ProductAlertResponse


router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


# ============================================================
# CREATE PRODUCT
# ============================================================

@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    data: ProductCreate,
    context=Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    current_user, organization_id = context

    # Check if SKU already exists
    result = await db.execute(
        select(Product).where(
            Product.organization_id == organization_id,
            Product.sku == data.sku,
        )
    )

    existing_product = result.scalar_one_or_none()

    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A product with this SKU already exists.",
        )

    product = Product(
        organization_id=organization_id,
        **data.model_dump(),
    )

    db.add(product)

    await db.commit()
    await db.refresh(product)

    return product


# ============================================================
# GET ALL PRODUCTS
# ============================================================

@router.get(
    "",
    response_model=list[ProductResponse],
)
async def get_products(
    context=Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    current_user, organization_id = context

    result = await db.execute(
        select(Product)
        .where(
            Product.organization_id == organization_id
        )
        .order_by(
            Product.created_at.desc()
        )
    )

    return result.scalars().all()


# ============================================================
# LOW STOCK PRODUCTS
# IMPORTANT: These routes must come BEFORE /{product_id}
# ============================================================

@router.get(
    "/low-stock",
    response_model=list[ProductAlertResponse],
)
async def get_low_stock_products(
    context=Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get active products whose stock is at or below
    the minimum stock level.
    """

    current_user, organization_id = context

    result = await db.execute(
        select(Product)
        .where(
            Product.organization_id == organization_id,
            Product.is_active.is_(True),
            Product.current_stock
            <= Product.minimum_stock_level,
        )
        .order_by(
            Product.current_stock.asc()
        )
    )

    return result.scalars().all()


# ============================================================
# EXPIRING PRODUCTS
# ============================================================

@router.get(
    "/expiring",
    response_model=list[ProductAlertResponse],
)
async def get_expiring_products(
    context=Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get active products expiring within the next 90 days.
    """

    current_user, organization_id = context

    today = date.today()

    expiry_limit = today + timedelta(
        days=90
    )

    result = await db.execute(
        select(Product)
        .where(
            Product.organization_id == organization_id,
            Product.is_active.is_(True),
            Product.expiry_date.is_not(None),
            Product.expiry_date >= today,
            Product.expiry_date <= expiry_limit,
        )
        .order_by(
            Product.expiry_date.asc()
        )
    )

    return result.scalars().all()


# ============================================================
# EXPIRED PRODUCTS
# ============================================================

@router.get(
    "/expired",
    response_model=list[ProductAlertResponse],
)
async def get_expired_products(
    context=Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get active products that have already expired.
    """

    current_user, organization_id = context

    today = date.today()

    result = await db.execute(
        select(Product)
        .where(
            Product.organization_id == organization_id,
            Product.is_active.is_(True),
            Product.expiry_date.is_not(None),
            Product.expiry_date < today,
        )
        .order_by(
            Product.expiry_date.asc()
        )
    )

    return result.scalars().all()


# ============================================================
# GET SINGLE PRODUCT
# IMPORTANT: Keep this AFTER /low-stock, /expiring, /expired
# ============================================================

@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
async def get_product(
    product_id: uuid.UUID,
    context=Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    current_user, organization_id = context

    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.organization_id == organization_id,
        )
    )

    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    return product


# ============================================================
# UPDATE PRODUCT
# ============================================================

@router.put(
    "/{product_id}",
    response_model=ProductResponse,
)
async def update_product(
    product_id: uuid.UUID,
    data: ProductUpdate,
    context=Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    current_user, organization_id = context

    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.organization_id == organization_id,
        )
    )

    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    # Check SKU uniqueness
    if "sku" in update_data:
        sku_result = await db.execute(
            select(Product).where(
                Product.organization_id == organization_id,
                Product.sku == update_data["sku"],
                Product.id != product_id,
            )
        )

        if sku_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A product with this SKU already exists.",
            )

    for field, value in update_data.items():
        setattr(
            product,
            field,
            value,
        )

    await db.commit()
    await db.refresh(product)

    return product


# ============================================================
# DELETE PRODUCT
# ============================================================

@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_product(
    product_id: uuid.UUID,
    context=Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    current_user, organization_id = context

    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.organization_id == organization_id,
        )
    )

    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    await db.delete(product)

    await db.commit()

    return None

