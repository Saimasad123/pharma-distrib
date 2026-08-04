from decimal import Decimal

from pydantic import BaseModel


class DashboardResponse(BaseModel):
    total_products: int
    total_customers: int
    total_suppliers: int

    total_sales_orders: int
    pending_sales_orders: int
    confirmed_sales_orders: int

    total_inventory_value: Decimal

    low_stock_products: int
    expired_products: int

    total_revenue: Decimal
    total_cost: Decimal
    total_profit: Decimal
    average_order_value: Decimal