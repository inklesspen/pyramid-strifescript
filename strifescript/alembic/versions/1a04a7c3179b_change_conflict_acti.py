"""change Conflict.active to Conflict.archived

Revision ID: 1a04a7c3179b
Revises: 467e50eb48ea
Create Date: 2013-01-11 23:12:28.767065

"""

# revision identifiers, used by Alembic.
revision = '1a04a7c3179b'
down_revision = '467e50eb48ea'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('conflicts', sa.Column('archived', sa.Boolean(), nullable=False))
    op.drop_column('conflicts', u'active')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('conflicts', sa.Column(u'active', sa.BOOLEAN(), nullable=False))
    op.drop_column('conflicts', 'archived')
    ### end Alembic commands ###