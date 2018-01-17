"""empty message

Revision ID: 2630e75b9fda
Revises: ef28c65ccfd1
Create Date: 2018-01-14 19:15:39.738658

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '2630e75b9fda'
down_revision = 'ef28c65ccfd1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('directions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('location_id', sa.Integer(), nullable=True),
    sa.Column('driving', sa.String(length=128), nullable=True),
    sa.Column('walking', sa.String(length=128), nullable=True),
    sa.Column('transit', sa.String(length=128), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['location_id'], ['location.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_column(u'User', 'is_admin')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(u'User', sa.Column('is_admin', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.drop_table('directions')
    # ### end Alembic commands ###
