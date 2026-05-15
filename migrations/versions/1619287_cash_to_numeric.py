"""change cash column to Numeric

Revision ID: 1619287
Revises: de50e7c
Create Date: 2026-04-28 19:35:32.918423
"""
from alembic import op
import sqlalchemy as sa


revision = '1619287'
down_revision = 'de50e7c'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('cash',
               existing_type=sa.Float(),
               type_=sa.Numeric(precision=12, scale=2),
               existing_nullable=False)


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('cash',
               existing_type=sa.Numeric(precision=12, scale=2),
               type_=sa.Float(),
               existing_nullable=False)