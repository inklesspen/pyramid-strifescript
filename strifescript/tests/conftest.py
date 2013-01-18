import os

import pytest

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ..models import DBSession, Base, User

@pytest.fixture(scope='session', autouse=True)
def set_bcrypt_difficulty(request):
    # The default difficulty is good for regular use, but slows down the tests too much.
    old_difficulty = User.bcrypt_difficulty
    User.bcrypt_difficulty = 2
    
    def teardown():
        User.bcrypt_difficulty = old_difficulty

    request.addfinalizer(teardown)

@pytest.fixture(scope='session')
def appsettings(request):
    config_uri = os.path.abspath(request.config.option.ini)
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    return settings

@pytest.fixture(scope='session')
def sqlengine(request, appsettings):
    engine = engine_from_config(appsettings, 'sqlalchemy.')
    return engine

@pytest.fixture(scope='session')
def dbtables(request, sqlengine):
    Base.metadata.create_all(sqlengine)

    def teardown():
        Base.metadata.drop_all(sqlengine)

    request.addfinalizer(teardown)

@pytest.fixture()
def dbtransaction(request, sqlengine, dbtables):
    connection = sqlengine.connect()
    transaction = connection.begin()
    DBSession.configure(bind=connection)

    def teardown():
        transaction.rollback()
        connection.close()
        DBSession.remove()

    request.addfinalizer(teardown)

    return connection

def pytest_addoption(parser):
    parser.addoption("--ini", action="store", metavar="INI_FILE", help="use INI_FILE to configure SQLAlchemy")

