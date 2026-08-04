"""add purchase price to sales order items

Revision ID: 7c60593efe4d
Revises: b3e04a15ba4d
Create Date: 2026-08-03

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7c60593efe4d"
down_revision: Union[str, Sequence[str], None] = "b3e04a15ba4d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -------------------------------------------------
    # STEP 1
    # Add the column as nullable first.
    #
    # This is necessary because existing sales order
    # items already exist in the database.
    # -------------------------------------------------

    op.add_column(
        "sales_order_items",
        sa.Column(
            "purchase_price",
            sa.Numeric(precision=12, scale=2),
            nullable=True,
        ),
    )

    # -------------------------------------------------
    # STEP 2
    # Fill purchase_price for existing sales.
    #
    # Existing records did not previously store the
    # purchase price, so we use the current product
    # purchase price as the best available value.
    # -------------------------------------------------

    op.execute(
        """
        UPDATE sales_order_items
        SET purchase_price = products.purchase_price
        FROM products
        WHERE sales_order_items.product_id = products.id
        """
    )

    # -------------------------------------------------
    # STEP 3
    # Make purchase_price NOT NULL.
    #
    # New sales must always store their purchase price.
    # -------------------------------------------------

    op.alter_column(
        "sales_order_items",
        "purchase_price",
        existing_type=sa.Numeric(
            precision=12,
            scale=2,
        ),
        nullable=False,
    )


def downgrade() -> None:
    op.drop_column(
        "sales_order_items",
        "purchase_price",
    )