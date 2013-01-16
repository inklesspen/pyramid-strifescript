import collections

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
    def _user_by_username_query(cls, username):
        return cls.query.filter(cls.username == username)

    @classmethod
    def get_user(cls, username):
        return cls._user_by_username_query(username).one()

    @classmethod
    def user_exists_with_username(cls, username):
        return cls._user_by_username_query(username).count() == 1

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

    def __repr__(self):
        return "<Team(%r, %r, %r)>" % (self.id, self.conflict, self.name)

    @classmethod
    def from_validated(cls, validated):
        return cls(name=validated['name'], notes=validated['notes'], users=validated['participants'])

    def for_json(self):
        r = {
            'id': self.id,
            'name': self.name,
            'participants': [user.username for user in self.users]
        }
        if self.notes is not None:
            r['notes'] = self.notes
        return r

class Conflict(Tablename, Base):
    name = Column(Unicode(100), nullable=False)
    teams = relationship('Team', backref='conflict')
    archived = Column(Boolean, nullable=False, default=False)
    events = relationship('Event', backref='conflict', order_by='Event.created_at')

    def __repr__(self):
        return "<Conflict(%r, %r)>" % (self.id, self.name)

    @property
    def users(self):
        return User.query.join(Team.users).filter(Team.conflict == self)

    @classmethod
    def from_validated(cls, validated):
        teams = [Team.from_validated(team) for team in validated['teams']]
        return cls(name=validated['name'], teams=teams)

    def generate_exchange(self, exchange_events):
        team_scripts = {}
        team_reveals = collections.Counter()
        team_changes = collections.defaultdict(list)

        for event in exchange_events:
            if isinstance(event, SetScriptEvent):
                team_scripts[event.team] = event
            if isinstance(event, RevealVolleyEvent):
                team_reveals[event.team] += 1
            if isinstance(event, ChangeActionsEvent):
                team_changes[event.team].append(event)

        retval = {}
        for team in self.teams:
            retval[team.id] = {}
            sse = team_scripts[team]
            # We need to make copies of the volley arrays.
            retval[team.id]['script'] = [sse.volley_1[:], sse.volley_2[:], sse.volley_3[:]]
            retval[team.id]['revealed'] = team_reveals[team]
            for event in team_changes[team]:
                volley = retval[team.id]['script'][event.volley_no - 1]
                volley.remove(event.forfeited_action)
                i = volley.index(event.changed_action)
                volley[i] = event.replacement_action

        return retval
        

    def generate_history(self):
        if len(self.events) == 0:
            return []
        ee = collections.defaultdict(list)
        exchanges = set()
        for event in self.events:
            exchanges.add(event.exchange)
            ee[event.exchange].append(event)

        return [self.generate_exchange(ee[exchange]) for exchange in range(1, max(exchanges)+1)]
 
    def allowed_actions(self):
        # shortcut
        if len(self.events) == 0:
            return {team: ['set-script'] for team in self.teams}

        last_seen_exchange = max(e.exchange for e in self.events)
        exchange_events = [e for e in self.events if e.exchange == last_seen_exchange]

        script_teams = set()
        reveal_teams = collections.Counter()

        for event in exchange_events:
            if isinstance(event, SetScriptEvent):
                script_teams.add(event.team)
            if isinstance(event, RevealVolleyEvent):
                reveal_teams[event.team] += 1

        min_reveal = min(reveal_teams[team] for team in self.teams)
        if min_reveal == 3:
            # All scripts in this exchange have been revealed, new exchange
            return {team: ['set-script'] for team in self.teams}

        actions = {team: [] for team in self.teams}
        if len(script_teams) < len(self.teams):
            for team in self.teams:
                if team not in script_teams:
                    actions[team].append('set-script')
        else:
            min_reveal = min(reveal_teams[team] for team in self.teams)
            for team in self.teams:
                if reveal_teams[team] == min_reveal:
                    actions[team].append('reveal-volley')
                    # if any of the unrevealed volleys contain two actions,
                    # 'change-actions' is allowed. this means we must
                    # calculate the scripts for the exchange

        return actions

    def for_json(self):
        actions = self.allowed_actions()
        return {
            'id': self.id,
            'name': self.name,
            'teams': [team.for_json() for team in self.teams],
            'actions': {team.id: actions[team] for team in self.teams}
        }

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
