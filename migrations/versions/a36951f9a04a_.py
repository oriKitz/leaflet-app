"""empty message

Revision ID: a36951f9a04a
Revises: 
Create Date: 2020-04-24 14:00:42.927822

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a36951f9a04a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('query', sa.Column('query_name', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('query', 'query_name')
    # ### end Alembic commands ###
