"""starting

Revision ID: 21f7c33730df
Revises: None
Create Date: 2013-01-07 13:02:53.901730

"""

# revision identifiers, used by Alembic.
revision = '21f7c33730df'
down_revision = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.Unicode(length=50), nullable=False),
    sa.Column('email', sa.Unicode(length=254), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('logins',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
    sa.Column('type', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('passwordlogins',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('password_hash', sa.String(length=60), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['logins.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('conflicts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Unicode(length=100), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('teams',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Unicode(length=100), nullable=False),
    sa.Column('conflict_id', sa.Integer(), nullable=False),
    sa.Column('notes', sa.UnicodeText(), nullable=True),
    sa.ForeignKeyConstraint(['conflict_id'], ['conflicts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('participants',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('team_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'team_id')
    )
    op.create_table('events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('conflict_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('exchange', sa.Integer(), nullable=False),
    sa.Column('team_id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['conflict_id'], ['conflicts.id'], ),
    sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('setscriptevents',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('volley_1', postgresql.ARRAY(sa.UnicodeText()), nullable=False),
    sa.Column('volley_2', postgresql.ARRAY(sa.UnicodeText()), nullable=False),
    sa.Column('volley_3', postgresql.ARRAY(sa.UnicodeText()), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['events.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('changeactionsevents',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('volley_no', sa.Integer(), nullable=False),
    sa.Column('forfeited_action', sa.UnicodeText(), nullable=False),
    sa.Column('changed_action', sa.UnicodeText(), nullable=False),
    sa.Column('replacement_action', sa.UnicodeText(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['events.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    op.drop_table('changeactionsevents')
    op.drop_table('setscriptevents')
    op.drop_table('events')
    op.drop_table('participants')
    op.drop_table('teams')
    op.drop_table('conflicts')
    op.drop_table('passwordlogins')
    op.drop_table('logins')
    op.drop_table('users')
    ### end Alembic commands ###
