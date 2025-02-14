"""empty message

Revision ID: 53d415065e30
Revises: 6a80fcfbb0ec
Create Date: 2020-04-30 18:31:49.903434

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '53d415065e30'
down_revision = '6a80fcfbb0ec'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('query_polygon_parameters',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('query_id', sa.Integer(), nullable=False),
    sa.Column('lon_column', sa.String(length=100), nullable=False),
    sa.Column('lat_column', sa.String(length=100), nullable=False),
    sa.ForeignKeyConstraint(['query_id'], ['query.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('query_polygon_parameters')
    # ### end Alembic commands ###
