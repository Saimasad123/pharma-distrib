from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.product import router as product_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.supplier import router as supplier_router
from app.api.v1.purchase import router as purchase_router
from app.api.v1.customer import router as customer_router
from app.api.v1.sales_order import router as sales_order_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.reports import router as reports_router
from app.api.v1.analytics import router as analytics_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(product_router)
router.include_router(inventory_router)
router.include_router(supplier_router)
router.include_router(purchase_router)
router.include_router(customer_router)
router.include_router(sales_order_router)
router.include_router(dashboard_router)
router.include_router(reports_router)
router.include_router(analytics_router)