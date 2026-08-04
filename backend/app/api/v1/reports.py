from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user_context
from app.database import get_db
from app.models import Product, SalesOrder, SalesOrderItem


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


# =========================================================
# PROFIT REPORT
# =========================================================

@router.get("/profit")
async def get_profit_report(
    start_date: date | None = Query(
        default=None,
        description="Start date, e.g. 2026-07-01",
    ),
    end_date: date | None = Query(
        default=None,
        description="End date, e.g. 2026-07-31",
    ),
    context=Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get revenue, cost, and profit.

    Only CONFIRMED sales orders are included.

    Optional date filters can be used:
    /reports/profit?start_date=2026-07-01&end_date=2026-07-31
    """

    current_user, organization_id = context

    # Validate dates
    if start_date and end_date:
        if start_date > end_date:
            return {
                "error": "start_date cannot be after end_date."
            }

    # Base query
    query = (
        select(
            func.coalesce(
                func.sum(
                    SalesOrderItem.quantity
                    * SalesOrderItem.unit_price
                ),
                0,
            ).label("total_revenue"),

            func.coalesce(
                func.sum(
                    SalesOrderItem.quantity
                    * Product.purchase_price
                ),
                0,
            ).label("total_cost"),
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
    )

    # Start date filter
    if start_date:
        start_datetime = datetime.combine(
            start_date,
            time.min,
        )

        query = query.where(
            SalesOrder.created_at
            >= start_datetime
        )

    # End date filter
    if end_date:
        # Add one day so the complete end date is included
        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            time.min,
        )

        query = query.where(
            SalesOrder.created_at
            < end_datetime
        )

    result = await db.execute(query)

    row = result.one()

    total_revenue = row.total_revenue or 0
    total_cost = row.total_cost or 0
    total_profit = (
        total_revenue
        - total_cost
    )

    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_revenue": total_revenue,
        "total_cost": total_cost,
        "total_profit": total_profit,
    }


# =========================================================
# REVENUE REPORT
# =========================================================

@router.get("/revenue")
async def get_revenue_report(
    start_date: date | None = Query(
        default=None,
    ),
    end_date: date | None = Query(
        default=None,
    ),
    context=Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get total confirmed sales revenue.

    Optional date filtering is supported.
    """

    current_user, organization_id = context

    query = (
        select(
            func.coalesce(
                func.sum(
                    SalesOrderItem.quantity
                    * SalesOrderItem.unit_price
                ),
                0,
            )
        )
        .select_from(SalesOrderItem)
        .join(
            SalesOrder,
            SalesOrder.id
            == SalesOrderItem.sales_order_id,
        )
        .where(
            SalesOrder.organization_id
            == organization_id,
            SalesOrder.status == "CONFIRMED",
        )
    )

    if start_date:
        start_datetime = datetime.combine(
            start_date,
            time.min,
        )

        query = query.where(
            SalesOrder.created_at
            >= start_datetime
        )

    if end_date:
        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            time.min,
        )

        query = query.where(
            SalesOrder.created_at
            < end_datetime
        )

    result = await db.execute(query)

    total_revenue = (
        result.scalar()
        or 0
    )

    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_revenue": total_revenue,
    }


# =========================================================
# MONTHLY REPORT
# =========================================================

@router.get("/monthly")
async def get_monthly_report(
    year: int = Query(
        default=date.today().year,
        ge=2000,
        le=2100,
    ),
    month: int = Query(
        default=date.today().month,
        ge=1,
        le=12,
    ),
    context=Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get revenue, cost, profit, and order count
    for a specific month.
    """

    current_user, organization_id = context

    # First day of month
    start_date = date(
        year,
        month,
        1,
    )

    # First day of next month
    if month == 12:
        end_date = date(
            year + 1,
            1,
            1,
        )
    else:
        end_date = date(
            year,
            month + 1,
            1,
        )

    start_datetime = datetime.combine(
        start_date,
        time.min,
    )

    end_datetime = datetime.combine(
        end_date,
        time.min,
    )

    result = await db.execute(
        select(
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
            ).label("total_orders"),
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

            SalesOrder.created_at
            >= start_datetime,

            SalesOrder.created_at
            < end_datetime,
        )
    )

    row = result.one()

    revenue = row.revenue or 0
    cost = row.cost or 0
    profit = revenue - cost

    return {
        "year": year,
        "month": month,
        "revenue": revenue,
        "cost": cost,
        "profit": profit,
        "total_orders": row.total_orders or 0,
    }


# =========================================================
# ANNUAL REPORT
# =========================================================

@router.get("/annual")
async def get_annual_report(
    year: int = Query(
        default=date.today().year,
        ge=2000,
        le=2100,
    ),
    context=Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get revenue, cost, profit, and order count
    for a specific year.
    """

    current_user, organization_id = context

    start_date = date(
        year,
        1,
        1,
    )

    end_date = date(
        year + 1,
        1,
        1,
    )

    start_datetime = datetime.combine(
        start_date,
        time.min,
    )

    end_datetime = datetime.combine(
        end_date,
        time.min,
    )

    result = await db.execute(
        select(
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
            ).label("total_orders"),
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

            # IMPORTANT:
            # Must be CONFIRMED, not Confirmed
            SalesOrder.status
            == "CONFIRMED",

            SalesOrder.created_at
            >= start_datetime,

            SalesOrder.created_at
            < end_datetime,
        )
    )

    row = result.one()

    revenue = row.revenue or 0
    cost = row.cost or 0
    profit = revenue - cost

    return {
        "year": year,
        "revenue": revenue,
        "cost": cost,
        "profit": profit,
        "total_orders": row.total_orders or 0,
    }