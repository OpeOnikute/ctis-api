"""empty message

Revision ID: eb351c01be77
Revises: e2230e63835b
Create Date: 2017-12-12 01:53:20.336610

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'eb351c01be77'
down_revision = 'e2230e63835b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('User', 'status',
               existing_type=mysql.ENUM(u'blocked', u'disabled', u'enabled', u'pending'),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('User', 'status',
               existing_type=mysql.ENUM(u'blocked', u'disabled', u'enabled', u'pending'),
               nullable=True)
    # ### end Alembic commands ###
