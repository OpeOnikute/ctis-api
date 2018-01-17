"""empty message

Revision ID: ef28c65ccfd1
Revises: eb351c01be77
Create Date: 2018-01-12 18:28:23.356319

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ef28c65ccfd1'
down_revision = 'eb351c01be77'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('User', sa.Column('is_admin', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('User', 'is_admin')
    # ### end Alembic commands ###
