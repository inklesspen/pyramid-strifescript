from sqlalchemy import engine_from_config

import transaction

from pyramid import testing

from ..models import (
    DBSession,
    Base,
    )

from .. import models

import pytest

from fixture.loadable import EnvLoadableFixture
from fixture.style import NamedDataStyle

class LoadOnlyFixture(EnvLoadableFixture):
    def __init__(self, session=None, **kw):
        EnvLoadableFixture.__init__(self, **kw)
        self.session = session

    def commit(self):
        pass

    def rollback(self):
        pass

    class Medium(EnvLoadableFixture.Medium):
        def visit_loader(self, loader):
            self.session = loader.session

        def save(self, row, column_vals):
            obj = self.medium()
            for c, val in column_vals:
                setattr(obj, c, val)
            self.session.add(obj)
            return obj

        def clear(self, obj):
            pass
            

dbfixture = LoadOnlyFixture(
    env = models,
    style = NamedDataStyle(),
    session = DBSession
)

@pytest.mark.usefixtures("dbtransaction")
class BaseTest(object):
    def setup_method(self, method):
        self._patchers = []
        self._fixture_state = None
        self.config = testing.setUp()

    def add_patcher(self, patcher):
        self._patchers.append(patcher)
        patcher.start()
        return patcher

    def add_fixtures(self, *datasets):
        self._fixture_state = dbfixture.data(*datasets)
        self._fixture_state.setup()
        DBSession.flush()

    def teardown_method(self, method):
        transaction.abort()
        testing.tearDown()
        for patcher in self._patchers:
            patcher.stop()
        if self._fixture_state is not None:
            self._fixture_state.teardown()
            self._fixture_state = None

