from sqlalchemy import engine_from_config

import transaction

from pyramid import testing

from ..models import (
    DBSession,
    Base,
    )

import pytest

class BaseTest(object):
    @pytest.fixture(autouse=True)
    def dbtransaction(self, request, sqlengine):
        DBSession.remove()
        connection = sqlengine.connect()
        transaction = connection.begin()
        DBSession.configure(bind=connection)

        def teardown():
            transaction.rollback()
            connection.close()
            DBSession.remove()

        request.addfinalizer(teardown)

    def setup_method(self, method):
        self._patchers = []
        self.config = testing.setUp()

    def add_patcher(self, patcher):
        self._patchers.append(patcher)
        patcher.start()
        return patcher

    def teardown_method(self, method):
        transaction.abort()
        testing.tearDown()
        for patcher in self._patchers:
            patcher.stop()
