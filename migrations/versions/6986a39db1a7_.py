"""empty message

Revision ID: 6986a39db1a7
Revises: 2153789e6bf6
Create Date: 2017-12-07 22:23:19.498196

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6986a39db1a7'
down_revision = '2153789e6bf6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shuttle', sa.Column('no_of_seats', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('shuttle', 'no_of_seats')
    # ### end Alembic commands ###
