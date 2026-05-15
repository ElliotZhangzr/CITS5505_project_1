"""add stock holding and transaction models

Revision ID: bbc86f3
Revises: ca802ac
Create Date: 2026-04-29 20:39:06.763291
"""
from alembic import op
import sqlalchemy as sa


revision = 'bbc86f3'
down_revision = 'ca802ac'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('stock_holding',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('stock_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('average_cost', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('total_cost', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['stock_id'], ['stock.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'stock_id', name='uq_user_stock_holding')
    )
    op.create_table('stock_transaction',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('stock_id', sa.Integer(), nullable=False),
    sa.Column('side', sa.String(length=4), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('price', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('gross_amount', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('realized_profit', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('average_cost_before', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('cash_balance_after', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['stock_id'], ['stock.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('stock_transaction')
    op.drop_table('stock_holding')