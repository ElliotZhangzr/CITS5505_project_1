"""add stock simulation fields

Revision ID: 0433680
Revises: c6a8cac
Create Date: 2026-05-04 15:02:21.089346
"""
from alembic import op
import sqlalchemy as sa


revision = '0433680'
down_revision = 'c6a8cac'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('stock', schema=None) as batch_op:
        batch_op.add_column(sa.Column('base_price', sa.Numeric(precision=12, scale=2), nullable=False, server_default='100.00'))
        batch_op.add_column(sa.Column('volatility', sa.Numeric(precision=8, scale=6), nullable=False, server_default='0.010000'))
        batch_op.add_column(sa.Column('drift', sa.Numeric(precision=8, scale=6), nullable=False, server_default='0.000000'))
        batch_op.add_column(sa.Column('momentum_factor', sa.Numeric(precision=8, scale=6), nullable=False, server_default='0.200000'))
        batch_op.add_column(sa.Column('mean_reversion_factor', sa.Numeric(precision=8, scale=6), nullable=False, server_default='0.030000'))
        batch_op.add_column(sa.Column('liquidity', sa.Numeric(precision=14, scale=2), nullable=False, server_default='500000.00'))
        batch_op.add_column(sa.Column('trade_impact_factor', sa.Numeric(precision=8, scale=6), nullable=False, server_default='0.500000'))
        batch_op.add_column(sa.Column('min_price', sa.Numeric(precision=12, scale=2), nullable=False, server_default='1.00'))


def downgrade():
    with op.batch_alter_table('stock', schema=None) as batch_op:
        batch_op.drop_column('min_price')
        batch_op.drop_column('trade_impact_factor')
        batch_op.drop_column('liquidity')
        batch_op.drop_column('mean_reversion_factor')
        batch_op.drop_column('momentum_factor')
        batch_op.drop_column('drift')
        batch_op.drop_column('volatility')
        batch_op.drop_column('base_price')