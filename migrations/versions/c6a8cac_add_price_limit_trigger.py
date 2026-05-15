"""add stock price limit trigger

Revision ID: c6a8cac
Revises: bbc86f3
Create Date: 2026-04-30 02:15:38.531074
"""
from alembic import op


revision = 'c6a8cac'
down_revision = 'bbc86f3'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
    CREATE TRIGGER IF NOT EXISTS limit_stock_price_records
    AFTER INSERT ON stock_price
    WHEN (SELECT COUNT(*) FROM stock_price) > 6000
    BEGIN
        DELETE FROM stock_price
        WHERE id IN (
            SELECT id
            FROM stock_price
            ORDER BY recorded_at ASC, id ASC
            LIMIT (SELECT COUNT(*) - 6000 FROM stock_price)
        );
    END;
    """)


def downgrade():
    op.execute('DROP TRIGGER IF EXISTS limit_stock_price_records')