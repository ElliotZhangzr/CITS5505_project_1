"""add user profile fields

Revision ID: 76502a3
Revises: 0433680
Create Date: 2026-05-05 16:26:57.672158
"""
from alembic import op
import sqlalchemy as sa


revision = '76502a3'
down_revision = '0433680'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('bio', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('avatar_url', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('hide_holdings', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('hide_holdings')
        batch_op.drop_column('avatar_url')
        batch_op.drop_column('bio')