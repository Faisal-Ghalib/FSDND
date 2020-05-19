"""empty message

Revision ID: e1e64bfd54ae
Revises: ce07796988d2
Create Date: 2020-05-15 20:25:16.101974

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1e64bfd54ae'
down_revision = 'ce07796988d2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('generes', sa.ARRAY(sa.String()), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'generes')
    # ### end Alembic commands ###
