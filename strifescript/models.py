import bcrypt

from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    UniqueConstraint,

    Boolean,
    Date,
    DateTime,
    Enum,
    Integer,
    String,
    Unicode,
    UnicodeText,
    )

from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base, declared_attr, has_inherited_table
from sqlalchemy.ext.associationproxy import association_proxy

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship
    )

from sqlalchemy.orm.exc import NoResultFound

from zope.sqlalchemy import ZopeTransactionExtension

import pytz, datetime

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

def utcnow():
    return datetime.datetime.now(pytz.utc)

class Base(object):
    id = Column(Integer, primary_key=True)
    query = DBSession.query_property()

Base = declarative_base(cls=Base)

class Tablename(object):
    @declared_attr
    def __tablename__(cls):
        if (has_inherited_table(cls) and
            Tablename not in cls.__bases__):
            return None
        return cls.__name__.lower() + "s"

participants_table = Table('participants', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True, index=True),
    Column('team_id', Integer, ForeignKey('teams.id'), primary_key=True, index=True)
)

class User(Tablename, Base):
    username = Column(Unicode(50), unique=True, nullable=False)
    email = Column(Unicode(254), unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    last_login = Column(DateTime(timezone=True))
    teams = relationship('Team', secondary=participants_table)
    conflicts = association_proxy('teams', 'conflict')
    events = relationship('Event', backref='user')
    password_hash = Column(String(60), nullable=False)

    def __repr__(self):
        if self.id is None:
            return "<User('%s', unsaved=True>" % self.username
        return "<User(%d, '%s')>" % (self.id, self.username)

    @classmethod
    def get_user(cls, username):
        return cls.query.filter(cls.username == username).one()

    @classmethod
    def new(cls, username, password, email=None):
        user = cls(username=username, email=email)
        user.change_password(password)
        return user

    def update_last_login(self):
        self.last_login = utcnow()

    def check_password(self, candidate):
        return bcrypt.hashpw(candidate, self.password_hash) == self.password_hash

    def change_password(self, new_password):
        self.password_hash = User.generate_password_hash(new_password)

    # For testing purposes:
    bcrypt_difficulty = 12

    @classmethod
    def generate_password_hash(cls, new_password, difficulty=None):
        difficulty = cls.bcrypt_difficulty if difficulty is None else difficulty
        return bcrypt.hashpw(new_password, bcrypt.gensalt(difficulty))

    def for_json(self):
        return {
            u'username': self.username,
            u'email': self.email,
        }

class Team(Tablename, Base):
    name = Column(Unicode(100), nullable=False)
    conflict_id = Column(Integer, ForeignKey('conflicts.id'), nullable=False, index=True)
    notes = Column(UnicodeText, nullable=True)
    users = relationship('User', secondary=participants_table)
    events = relationship('Event', backref='team')

class Conflict(Tablename, Base):
    name = Column(Unicode(100), nullable=False)
    teams = relationship('Team', backref='conflict')
    active = Column(Boolean, nullable=False, default=True)
    events = relationship('Event', backref='conflict')

# Events
# Set script for the three volleys of the exchange, for a given team
#   - active exchange
#   - script not yet set for that team
# Reveal the next volley, for a given team
#   - active exchange
#   - scripts entered for all teams
#   - there is an unrevealed volley
# Change actions for an unrevealed volley, paying the forfeit
#   - requirements as for reveal, plus
#   - the volley the player wishes to change must have at least two actions

class Event(Tablename, Base):
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    conflict_id = Column(Integer, ForeignKey('conflicts.id'), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    exchange = Column(Integer, nullable=False, index=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False, index=True)

    discriminator = Column('type', String(50))
    __mapper_args__ = {'polymorphic_on': discriminator}

class SetScriptEvent(Event, Tablename):
    __mapper_args__ = {'polymorphic_identity': 'set_script_event'}
    id = Column(Integer, ForeignKey('events.id'), primary_key=True)
    # Postgres multidimensional arrays must have array expressions with matching dimensions
    volley_1 = Column(postgresql.ARRAY(UnicodeText), nullable=False)
    volley_2 = Column(postgresql.ARRAY(UnicodeText), nullable=False)
    volley_3 = Column(postgresql.ARRAY(UnicodeText), nullable=False)

class RevealVolleyEvent(Event):
    # which volley is to be revealed can be determined simply by counting how many revealvolleyevents there are for the team and exchange
    # which means we don't actually need a table for this class.
    __mapper_args__ = {'polymorphic_identity': 'reveal_volley_event'}

class ChangeActionsEvent(Event, Tablename):
    __mapper_args__ = {'polymorphic_identity': 'change_actions_event'}
    id = Column(Integer, ForeignKey('events.id'), primary_key=True)
    volley_no = Column(Integer, nullable=False)
    forfeited_action = Column(UnicodeText, nullable=False)
    changed_action = Column(UnicodeText, nullable=False)
    replacement_action = Column(UnicodeText, nullable=False)
