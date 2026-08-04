import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.database import get_db
from app.models import (
    Customer,
    InventoryTransaction,
    OrganizationMember,
    Product,
    SalesOrder,
    SalesOrderItem,
    User,
)
from app.schemas.sales_order import (
    SalesOrderCreate,
    SalesOrderResponse,
)


router = APIRouter(
    prefix="/sales-orders",
    tags=["Sales Orders"],
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
    response_model=SalesOrderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_sales_order(
    data: SalesOrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a pending sales order.

    The product's current purchase_price and sale_price
    are saved into the sales order item.

    Stock is NOT reduced until the order is confirmed.
    """

    organization_id = await get_user_organization_id(
        current_user,
        db,
    )

    # Check customer belongs to the organization
    result = await db.execute(
        select(Customer).where(
            Customer.id == data.customer_id,
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

    # Sales order must contain at least one item
    if not data.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sales order must contain at least one item.",
        )

    # Check duplicate order number
    result = await db.execute(
        select(SalesOrder).where(
            SalesOrder.organization_id == organization_id,
            SalesOrder.order_number == data.order_number,
        )
    )

    existing_order = result.scalar_one_or_none()

    if existing_order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An order with this order number already exists.",
        )

    # Start total revenue at zero
    total_amount = Decimal("0.00")

    # Create sales order
    sales_order = SalesOrder(
        organization_id=organization_id,
        customer_id=data.customer_id,
        order_number=data.order_number,
        status="PENDING",
        total_amount=Decimal("0.00"),
        notes=data.notes,
    )

    db.add(sales_order)

    # Get sales_order.id before creating items
    await db.flush()

    # Process every sales order item
    for item_data in data.items:

        # Validate quantity
        if item_data.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be greater than zero.",
            )

        # Get product belonging to current organization
        result = await db.execute(
            select(Product).where(
                Product.id == item_data.product_id,
                Product.organization_id == organization_id,
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

        # -------------------------------------------------
        # IMPORTANT:
        # Save prices at the time of creating the sale.
        #
        # purchase_price = product's cost
        # sale_price     = product's selling price
        # -------------------------------------------------

        purchase_price = product.purchase_price
        sale_price = product.sale_price

        # Revenue for this product
        total_price = (
            sale_price
            * item_data.quantity
        )

        # Create sales order item
        order_item = SalesOrderItem(
            sales_order_id=sales_order.id,
            product_id=product.id,
            quantity=item_data.quantity,
            purchase_price=purchase_price,
            unit_price=sale_price,
            total_price=total_price,
        )

        db.add(order_item)

        # Add item revenue to order total
        total_amount += total_price

    # Save total sales revenue
    sales_order.total_amount = total_amount

    await db.commit()

    await db.refresh(sales_order)

    return sales_order


@router.get(
    "",
    response_model=list[SalesOrderResponse],
)
async def get_sales_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all sales orders for the current organization.
    """

    organization_id = await get_user_organization_id(
        current_user,
        db,
    )

    result = await db.execute(
        select(SalesOrder)
        .where(
            SalesOrder.organization_id
            == organization_id
        )
        .order_by(
            SalesOrder.created_at.desc()
        )
    )

    return result.scalars().all()


@router.get(
    "/{order_id}",
    response_model=SalesOrderResponse,
)
async def get_sales_order(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single sales order.
    """

    organization_id = await get_user_organization_id(
        current_user,
        db,
    )

    result = await db.execute(
        select(SalesOrder).where(
            SalesOrder.id == order_id,
            SalesOrder.organization_id
            == organization_id,
        )
    )

    sales_order = result.scalar_one_or_none()

    if not sales_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales order not found.",
        )

    return sales_order


@router.post(
    "/{order_id}/confirm",
    response_model=SalesOrderResponse,
)
async def confirm_sales_order(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Confirm a pending sales order.

    This will:

    1. Check stock availability.
    2. Reduce product stock.
    3. Create STOCK_OUT transactions.
    4. Mark the order as CONFIRMED.

    Revenue and profit are based on the prices
    saved in SalesOrderItem at the time of sale.
    """

    organization_id = await get_user_organization_id(
        current_user,
        db,
    )

    # Get sales order
    result = await db.execute(
        select(SalesOrder).where(
            SalesOrder.id == order_id,
            SalesOrder.organization_id
            == organization_id,
        )
    )

    sales_order = result.scalar_one_or_none()

    if not sales_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales order not found.",
        )

    # Only pending orders can be confirmed
    if sales_order.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Order cannot be confirmed because "
                f"its current status is "
                f"{sales_order.status}."
            ),
        )

    # Get order items
    result = await db.execute(
        select(SalesOrderItem).where(
            SalesOrderItem.sales_order_id
            == sales_order.id
        )
    )

    order_items = result.scalars().all()

    if not order_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sales order has no items.",
        )

    # Store products and items
    # after checking stock availability
    products = []

    # First check ALL stock
    # before changing anything
    for item in order_items:

        result = await db.execute(
            select(Product).where(
                Product.id == item.product_id,
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
                    f"Product {item.product_id} "
                    "not found."
                ),
            )

        if product.current_stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Insufficient stock for "
                    f"{product.name}. "
                    f"Available: "
                    f"{product.current_stock}, "
                    f"Requested: "
                    f"{item.quantity}."
                ),
            )

        products.append(
            (product, item)
        )

    # Reduce stock and create transactions
    for product, item in products:

        previous_stock = product.current_stock

        product.current_stock -= item.quantity

        new_stock = product.current_stock

        transaction = InventoryTransaction(
            organization_id=organization_id,
            product_id=product.id,
            transaction_type="STOCK_OUT",
            quantity=item.quantity,
            previous_stock=previous_stock,
            new_stock=new_stock,
            reason="Product sold",
            notes=(
                f"Sales order "
                f"{sales_order.order_number}"
            ),
        )

        db.add(transaction)

    # Mark order confirmed
    sales_order.status = "CONFIRMED"

    await db.commit()

    await db.refresh(sales_order)

    return sales_order