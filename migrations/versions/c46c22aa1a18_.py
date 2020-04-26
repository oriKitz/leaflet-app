"""empty message

Revision ID: c46c22aa1a18
Revises: 7f0bc502182d
Create Date: 2020-04-26 03:21:46.885935

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c46c22aa1a18'
down_revision = '7f0bc502182d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('team',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('layer', schema=None) as batch_op:
        batch_op.add_column(sa.Column('only_team', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('only_user', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('public', sa.Boolean(), nullable=True))

    with op.batch_alter_table('query', schema=None) as batch_op:
        batch_op.add_column(sa.Column('only_team', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('only_user', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('public', sa.Boolean(), nullable=True))

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('team_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('abcde', 'team', ['team_id'], ['id'])

    with op.batch_alter_table('query_text_parameters', schema=None) as batch_op:
        batch_op.create_foreign_key('abcdef', 'query', ['query_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('team_id')

    with op.batch_alter_table('query_text_parameters', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('query', schema=None) as batch_op:
        batch_op.drop_column('public')
        batch_op.drop_column('only_user')
        batch_op.drop_column('only_team')

    with op.batch_alter_table('layer', schema=None) as batch_op:
        batch_op.drop_column('public')
        batch_op.drop_column('only_user')
        batch_op.drop_column('only_team')

    op.drop_table('team')
    # ### end Alembic commands ###
