from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, extract, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user_context
from app.database import get_db
from app.models import (
    Customer,
    Product,
    SalesOrder,
    SalesOrderItem,
)
router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/monthly-sales")
async def get_monthly_sales_analytics(
    year: int = Query(
        default=date.today().year,
        ge=2000,
        le=2100,
    ),
    context=Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get monthly sales analytics for a specific year.

    Returns:
    - Revenue
    - Cost
    - Profit
    - Number of orders
    """

    current_user, organization_id = context

    result = await db.execute(
        select(
            extract(
                "month",
                SalesOrder.created_at,
            ).label("month"),

            func.coalesce(
                func.sum(
                    SalesOrderItem.quantity
                    * SalesOrderItem.unit_price
                ),
                0,
            ).label("revenue"),

            func.coalesce(
                func.sum(
                    SalesOrderItem.quantity
                    * Product.purchase_price
                ),
                0,
            ).label("cost"),

            func.count(
                func.distinct(
                    SalesOrder.id
                )
            ).label("orders"),
        )
        .select_from(SalesOrderItem)
        .join(
            SalesOrder,
            SalesOrder.id
            == SalesOrderItem.sales_order_id,
        )
        .join(
            Product,
            Product.id
            == SalesOrderItem.product_id,
        )
        .where(
            SalesOrder.organization_id
            == organization_id,

            SalesOrder.status
            == "CONFIRMED",

            extract(
                "year",
                SalesOrder.created_at,
            )
            == year,
        )
        .group_by(
            extract(
                "month",
                SalesOrder.created_at,
            )
        )
        .order_by(
            extract(
                "month",
                SalesOrder.created_at,
            )
        )
    )

    rows = result.all()

    monthly_data = []

    for row in rows:

        revenue = row.revenue or 0
        cost = row.cost or 0
        profit = revenue - cost

        monthly_data.append(
            {
                "month": int(row.month),
                "revenue": revenue,
                "cost": cost,
                "profit": profit,
                "orders": row.orders or 0,
            }
        )

    return {
        "year": year,
        "monthly_sales": monthly_data,
    }

@router.get("/top-products")
async def get_top_products_analytics(
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    context=Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get top-selling products for the current organization.

    Returns:
    - Product name
    - SKU
    - Quantity sold
    - Revenue
    - Cost
    - Profit
    """

    current_user, organization_id = context

    result = await db.execute(
        select(
            Product.id.label("product_id"),
            Product.name.label("product_name"),
            Product.sku.label("sku"),

            func.sum(
                SalesOrderItem.quantity
            ).label("quantity_sold"),

            func.sum(
                SalesOrderItem.quantity
                * SalesOrderItem.unit_price
            ).label("revenue"),

            func.sum(
                SalesOrderItem.quantity
                * Product.purchase_price
            ).label("cost"),
        )
        .select_from(SalesOrderItem)
        .join(
            SalesOrder,
            SalesOrder.id
            == SalesOrderItem.sales_order_id,
        )
        .join(
            Product,
            Product.id
            == SalesOrderItem.product_id,
        )
        .where(
            SalesOrder.organization_id
            == organization_id,

           SalesOrder.status == "CONFIRMED",
        )
        .group_by(
            Product.id,
            Product.name,
            Product.sku,
        )
        .order_by(
            func.sum(
                SalesOrderItem.quantity
            ).desc()
        )
        .limit(limit)
    )

    rows = result.all()

    products = []

    for row in rows:

        revenue = row.revenue or 0
        cost = row.cost or 0
        profit = revenue - cost

        products.append(
            {
                "product_id": str(
                    row.product_id
                ),
                "product_name": row.product_name,
                "sku": row.sku,
                "quantity_sold": (
                    row.quantity_sold or 0
                ),
                "revenue": revenue,
                "cost": cost,
                "profit": profit,
            }
        )

    return {
        "top_products": products,
    }

@router.get("/top-customers")
async def get_top_customers_analytics(
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    context=Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get top customers based on total spending.

    Returns:
    - Customer name
    - Number of orders
    - Total quantity purchased
    - Total spending
    """

    current_user, organization_id = context

    result = await db.execute(
        select(
            SalesOrder.customer_id.label(
                "customer_id"
            ),

            Customer.name.label(
                "customer_name"
            ),

            func.count(
                func.distinct(
                    SalesOrder.id
                )
            ).label(
                "total_orders"
            ),

            func.sum(
                SalesOrderItem.quantity
            ).label(
                "total_quantity"
            ),

            func.sum(
                SalesOrderItem.total_price
            ).label(
                "total_spending"
            ),
        )
        .select_from(SalesOrder)
        .join(
            Customer,
            Customer.id
            == SalesOrder.customer_id,
        )
        .join(
            SalesOrderItem,
            SalesOrderItem.sales_order_id
            == SalesOrder.id,
        )
        .where(
            SalesOrder.organization_id
            == organization_id,

           SalesOrder.status == "CONFIRMED",
        )
        .group_by(
            SalesOrder.customer_id,
            Customer.name,
        )
        .order_by(
            func.sum(
                SalesOrderItem.total_price
            ).desc()
        )
        .limit(limit)
    )

    rows = result.all()

    customers = []

    for row in rows:

        customers.append(
            {
                "customer_id": str(
                    row.customer_id
                ),
                "customer_name": (
                    row.customer_name
                ),
                "total_orders": (
                    row.total_orders or 0
                ),
                "total_quantity": (
                    row.total_quantity or 0
                ),
                "total_spending": (
                    row.total_spending or 0
                ),
            }
        )

    return {
        "top_customers": customers,
    }

@router.get("/inventory")
async def get_inventory_analytics(
    context=Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get inventory analytics for the current organization.

    Returns:
    - Total inventory value
    - Total stock units
    - Low-stock products
    - Expired products
    - Expiring products
    """

    current_user, organization_id = context

    # ---------------------------------------------------------
    # Total inventory value and stock
    # ---------------------------------------------------------

    result = await db.execute(
        select(
            func.coalesce(
                func.sum(
                    Product.current_stock
                    * Product.purchase_price
                ),
                0,
            ).label("total_inventory_value"),

            func.coalesce(
                func.sum(
                    Product.current_stock
                ),
                0,
            ).label("total_stock_units"),
        )
        .where(
            Product.organization_id
            == organization_id,

            Product.is_active.is_(True),
        )
    )

    row = result.one()

    total_inventory_value = (
        row.total_inventory_value or 0
    )

    total_stock_units = (
        row.total_stock_units or 0
    )

    # ---------------------------------------------------------
    # Low-stock products
    # ---------------------------------------------------------

    result = await db.execute(
        select(
            func.count(Product.id)
        )
        .where(
            Product.organization_id
            == organization_id,

            Product.is_active.is_(True),

            Product.current_stock
            <= Product.minimum_stock_level,
        )
    )

    low_stock_products = (
        result.scalar() or 0
    )

    # ---------------------------------------------------------
    # Expired products
    # ---------------------------------------------------------

    result = await db.execute(
        select(
            func.count(Product.id)
        )
        .where(
            Product.organization_id
            == organization_id,

            Product.is_active.is_(True),

            Product.expiry_date.is_not(None),

            Product.expiry_date
            < func.current_date(),
        )
    )

    expired_products = (
        result.scalar() or 0
    )

    # ---------------------------------------------------------
    # Products expiring within 90 days
    # ---------------------------------------------------------

    result = await db.execute(
        select(
            func.count(Product.id)
        )
        .where(
            Product.organization_id
            == organization_id,

            Product.is_active.is_(True),

            Product.expiry_date.is_not(None),

            Product.expiry_date
            >= func.current_date(),

            Product.expiry_date
            <= (
                func.current_date()
                + 90
            ),
        )
    )

    expiring_products = (
        result.scalar() or 0
    )

    return {
        "total_inventory_value":
            total_inventory_value,

        "total_stock_units":
            total_stock_units,

        "low_stock_products":
            low_stock_products,

        "expired_products":
            expired_products,

        "expiring_products":
            expiring_products,
    }
