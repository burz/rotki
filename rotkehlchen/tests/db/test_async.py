from random import randint, uniform

import gevent

from rotkehlchen.accounting.ledger_actions import LedgerAction, LedgerActionType
from rotkehlchen.constants.assets import A_ETH
from rotkehlchen.db.filtering import LedgerActionsFilterQuery
from rotkehlchen.db.ledger_actions import DBLedgerActions
from rotkehlchen.fval import FVal
from rotkehlchen.types import Location


def make_ledger_action():
    return LedgerAction(
        identifier=1,
        timestamp=randint(1, 16433333),
        asset=A_ETH,
        action_type=LedgerActionType.INCOME,
        location=Location.BLOCKCHAIN,
        amount=FVal(randint(1, 1642323)),
        rate=FVal(uniform(0.00001, 5)),
        link='dasd',
        notes='asdsad',
    )


def write_actions(database, num):
    actions = [make_ledger_action() for _ in range(1, num)]
    query = """
    INSERT INTO ledger_actions(
    timestamp, type, location, amount, asset, rate, rate_asset, link, notes
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);"""
    with database.user_write() as cursor:
        cursor.executemany(query, [x.serialize_for_db() for x in actions])


def read_actions(database, limit, msg_aggregator):
    dbla = DBLedgerActions(database, msg_aggregator)
    with database.conn.read_ctx() as cursor:
        dbla.get_ledger_actions(
            cursor,
            LedgerActionsFilterQuery.make(limit=limit),
            has_premium=True,
        )


def test_async_segfault(database, function_scope_messages_aggregator):
    """Test that the async and sqlite progress handler segfault yielding bug does not hit us

    The bug can be summed up as following:
    1. Get in the progress callback
    2. Context switch out of the callback with sleep(0)
    3. Enter critical section, which essentially disables the callback
    4. Write/read more data in the DB
    5. Exit critical section, re-enabling the callback
    6. Context switch back to the progress callback of (1) and exit it.
    7. Segmentation fault.
    """
    # first write some data in the DB to have enough data to read.
    write_actions(database, 1000)

    # Then start reading from one greenlet and writing from others to create the problem
    a = gevent.spawn(
        read_actions,
        database=database,
        limit=100,
        msg_aggregator=function_scope_messages_aggregator,
    )
    b = gevent.spawn(write_actions, database=database, num=200)
    c = gevent.spawn(write_actions, database=database, num=200)
    gevent.joinall([a, b, c])
