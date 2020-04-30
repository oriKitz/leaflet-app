"""empty message

Revision ID: 6a80fcfbb0ec
Revises: d45f954ad6da
Create Date: 2020-04-30 01:17:39.341592

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6a80fcfbb0ec'
down_revision = 'd45f954ad6da'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_preferences',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('starting_lon', sa.Float(), nullable=True),
    sa.Column('starting_lat', sa.Float(), nullable=True),
    sa.Column('starting_zoom', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_preferences')
    # ### end Alembic commands ###