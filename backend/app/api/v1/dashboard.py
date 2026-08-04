from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.database import get_db
from app.models import (
    Customer,
    OrganizationMember,
    Product,
    SalesOrder,
    SalesOrderItem,
    Supplier,
    User,
)
from app.schemas.dashboard import DashboardResponse


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "",
    response_model=DashboardResponse,
)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get complete dashboard statistics
    for the current user's organization.
    """

    # -------------------------------------------------
    # GET USER'S ORGANIZATION
    # -------------------------------------------------

    result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.user_id == current_user.id
        )
    )

    membership = result.scalar_one_or_none()

    if not membership:
        raise HTTPException(
            status_code=404,
            detail="Organization membership not found.",
        )

    organization_id = membership.organization_id

    # -------------------------------------------------
    # TOTAL ACTIVE PRODUCTS
    # -------------------------------------------------

    result = await db.execute(
        select(func.count(Product.id)).where(
            Product.organization_id == organization_id,
            Product.is_active.is_(True),
        )
    )

    total_products = result.scalar() or 0

    # -------------------------------------------------
    # TOTAL ACTIVE CUSTOMERS
    # -------------------------------------------------

    result = await db.execute(
        select(func.count(Customer.id)).where(
            Customer.organization_id == organization_id,
            Customer.is_active.is_(True),
        )
    )

    total_customers = result.scalar() or 0

    # -------------------------------------------------
    # TOTAL ACTIVE SUPPLIERS
    # -------------------------------------------------

    result = await db.execute(
        select(func.count(Supplier.id)).where(
            Supplier.organization_id == organization_id,
            Supplier.is_active.is_(True),
        )
    )

    total_suppliers = result.scalar() or 0

    # -------------------------------------------------
    # TOTAL SALES ORDERS
    # -------------------------------------------------

    result = await db.execute(
        select(func.count(SalesOrder.id)).where(
            SalesOrder.organization_id == organization_id,
        )
    )

    total_sales_orders = result.scalar() or 0

    # -------------------------------------------------
    # PENDING SALES ORDERS
    # -------------------------------------------------

    result = await db.execute(
        select(func.count(SalesOrder.id)).where(
            SalesOrder.organization_id == organization_id,
            SalesOrder.status == "PENDING",
        )
    )

    pending_sales_orders = result.scalar() or 0

    # -------------------------------------------------
    # CONFIRMED SALES ORDERS
    # -------------------------------------------------

    result = await db.execute(
        select(func.count(SalesOrder.id)).where(
            SalesOrder.organization_id == organization_id,
            SalesOrder.status == "CONFIRMED",
        )
    )

    confirmed_sales_orders = result.scalar() or 0

    # -------------------------------------------------
    # TOTAL INVENTORY VALUE
    #
    # Current stock × CURRENT purchase price
    #
    # This is correct because inventory value represents
    # the current value of products still in stock.
    # -------------------------------------------------

    result = await db.execute(
        select(
            func.coalesce(
                func.sum(
                    Product.current_stock
                    * Product.purchase_price
                ),
                0,
            )
        ).where(
            Product.organization_id == organization_id,
            Product.is_active.is_(True),
        )
    )

    total_inventory_value = (
        result.scalar()
        or Decimal("0.00")
    )

    # -------------------------------------------------
    # LOW STOCK PRODUCTS
    # -------------------------------------------------

    result = await db.execute(
        select(func.count(Product.id)).where(
            Product.organization_id == organization_id,
            Product.is_active.is_(True),
            Product.current_stock
            <= Product.minimum_stock_level,
        )
    )

    low_stock_products = result.scalar() or 0

    # -------------------------------------------------
    # EXPIRED PRODUCTS
    # -------------------------------------------------

    result = await db.execute(
        select(func.count(Product.id)).where(
            Product.organization_id == organization_id,
            Product.is_active.is_(True),
            Product.expiry_date < func.current_date(),
        )
    )

    expired_products = result.scalar() or 0

    # -------------------------------------------------
    # TOTAL REVENUE
    #
    # Only CONFIRMED orders are included.
    #
    # Revenue is based on the selling price recorded
    # in the SalesOrderItem when the order was created.
    #
    # We calculate from SalesOrderItem instead of
    # Product.sale_price so changing a product's price
    # does NOT change historical sales revenue.
    # -------------------------------------------------

    result = await db.execute(
        select(
            func.coalesce(
                func.sum(
                    SalesOrderItem.total_price
                ),
                0,
            )
        )
        .select_from(SalesOrderItem)
        .join(
            SalesOrder,
            SalesOrder.id == SalesOrderItem.sales_order_id,
        )
        .where(
            SalesOrder.organization_id == organization_id,
            SalesOrder.status == "CONFIRMED",
        )
    )

    total_revenue = (
        result.scalar()
        or Decimal("0.00")
    )

    # -------------------------------------------------
    # TOTAL COST
    #
    # Cost = quantity × purchase price
    #
    # IMPORTANT:
    # Use SalesOrderItem.purchase_price.
    #
    # This is the purchase price saved at the time
    # the sales order was created.
    #
    # Do NOT use Product.purchase_price here.
    # Otherwise, editing a product's purchase price
    # would change the profit of old sales.
    # -------------------------------------------------

    result = await db.execute(
        select(
            func.coalesce(
                func.sum(
                    SalesOrderItem.quantity
                    * SalesOrderItem.purchase_price
                ),
                0,
            )
        )
        .select_from(SalesOrderItem)
        .join(
            SalesOrder,
            SalesOrder.id == SalesOrderItem.sales_order_id,
        )
        .where(
            SalesOrder.organization_id == organization_id,
            SalesOrder.status == "CONFIRMED",
        )
    )

    total_cost = (
        result.scalar()
        or Decimal("0.00")
    )

    # -------------------------------------------------
    # TOTAL PROFIT
    #
    # Profit = Revenue - Cost
    # -------------------------------------------------

    total_profit = (
        total_revenue
        - total_cost
    )

    # -------------------------------------------------
    # AVERAGE ORDER VALUE
    #
    # Average = Revenue / Confirmed Orders
    # -------------------------------------------------

    if confirmed_sales_orders > 0:
        average_order_value = (
            total_revenue
            / confirmed_sales_orders
        )
    else:
        average_order_value = Decimal("0.00")

    # -------------------------------------------------
    # RETURN DASHBOARD
    # -------------------------------------------------

    return DashboardResponse(
        total_products=total_products,
        total_customers=total_customers,
        total_suppliers=total_suppliers,
        total_sales_orders=total_sales_orders,
        pending_sales_orders=pending_sales_orders,
        confirmed_sales_orders=confirmed_sales_orders,
        total_inventory_value=total_inventory_value,
        low_stock_products=low_stock_products,
        expired_products=expired_products,
        total_revenue=total_revenue,
        total_cost=total_cost,
        total_profit=total_profit,
        average_order_value=average_order_value,
    )