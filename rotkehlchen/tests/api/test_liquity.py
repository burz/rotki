import random

import pytest
import requests

from rotkehlchen.chain.ethereum.types import string_to_ethereum_address
from rotkehlchen.constants.assets import A_ETH, A_LQTY, A_LUSD
from rotkehlchen.fval import FVal
from rotkehlchen.tests.utils.api import (
    api_url_for,
    assert_ok_async_response,
    assert_proper_response_with_result,
    wait_for_async_task_with_result,
)

LQTY_ADDR = string_to_ethereum_address('0x063c26fF1592688B73d8e2A18BA4C23654e2792E')
LQTY_STAKING = string_to_ethereum_address('0x73C91af57C657DfD05a31DAcA7Bff1aEb5754629')
LQTY_PROXY = string_to_ethereum_address('0x9476832d4687c14b2c1a04E2ee4693162a7340B6')
ADDR_WITHOUT_TROVE = string_to_ethereum_address('0xA0446D8804611944F1B527eCD37d7dcbE442caba')

liquity_mocked_historical_prices = {
    A_ETH: {
        'USD': {
            1627818194: FVal('3000'),
            1627818617: FVal('3000'),
            1627827057: FVal('3500'),
            1641529258: FVal('3395'),
        },
    },
    A_LQTY: {
        'USD': {
            1627827057.: FVal('3.7'),
        },
    },
    A_LUSD: {
        'USD': {
            1627818194: FVal('1.02'),
            1627818617: FVal('1.019'),
            1627827057: FVal('1.02'),
            1641529258: FVal('1.0010'),
        },
    },
}


@pytest.mark.parametrize('ethereum_accounts', [[LQTY_ADDR]])
@pytest.mark.parametrize('ethereum_modules', [['liquity']])
@pytest.mark.parametrize('should_mock_current_price_queries', [True])
def test_trove_position(rotkehlchen_api_server, inquirer):  # pylint: disable=unused-argument
    """Test that we can get the status of the user's troves"""
    async_query = random.choice([False, True])
    response = requests.get(api_url_for(
        rotkehlchen_api_server,
        'liquitytrovesresource',
    ), json={'async_query': async_query})
    if async_query:
        task_id = assert_ok_async_response(response)
        result = wait_for_async_task_with_result(rotkehlchen_api_server, task_id)
    else:
        result = assert_proper_response_with_result(response)

    assert LQTY_ADDR in result
    trove_data = result[LQTY_ADDR]
    assert 'collateral' in trove_data
    assert 'debt' in trove_data
    assert 'collateralization_ratio' in trove_data
    assert 'liquidation_price' in trove_data
    assert trove_data['active'] is True


@pytest.mark.parametrize('ethereum_accounts', [[LQTY_STAKING]])
@pytest.mark.parametrize('ethereum_modules', [['liquity']])
@pytest.mark.parametrize('start_with_valid_premium', [True])
@pytest.mark.parametrize('should_mock_current_price_queries', [True])
def test_trove_staking(rotkehlchen_api_server, inquirer):  # pylint: disable=unused-argument
    """Test that we can get the status of the staked lqty"""
    async_query = random.choice([False, True])
    response = requests.get(api_url_for(
        rotkehlchen_api_server,
        'liquitystakingresource',
    ), json={'async_query': async_query})
    if async_query:
        task_id = assert_ok_async_response(response)
        result = wait_for_async_task_with_result(rotkehlchen_api_server, task_id)
    else:
        result = assert_proper_response_with_result(response)

    assert LQTY_STAKING in result
    stake_data = result[LQTY_STAKING]
    assert 'amount' in stake_data and stake_data['amount'].isnumeric()


@pytest.mark.parametrize('ethereum_accounts', [[LQTY_ADDR, LQTY_PROXY]])
@pytest.mark.parametrize('ethereum_modules', [['liquity']])
@pytest.mark.parametrize('should_mock_current_price_queries', [False])
@pytest.mark.parametrize('should_mock_price_queries', [True])
@pytest.mark.parametrize('mocked_price_queries', [liquity_mocked_historical_prices])
@pytest.mark.parametrize('start_with_valid_premium', [True])
def test_trove_events(rotkehlchen_api_server):
    """Test that Trove events events are correctly queried"""
    async_query = random.choice([True, False])
    response = requests.get(
        api_url_for(
            rotkehlchen_api_server,
            'liquitytroveshistoryresource',
        ), json={
            'async_query': async_query,
            'from_timestamp': 0,
            'to_timestamp': 1628026696,
            'reset_db_data': False,
        },
    )
    if async_query:
        task_id = assert_ok_async_response(response)
        result = wait_for_async_task_with_result(rotkehlchen_api_server, task_id)
    else:
        result = assert_proper_response_with_result(response)

    assert LQTY_ADDR in result
    assert len(result[LQTY_ADDR]) == 2
    trove_action = result[LQTY_ADDR][0]
    tx_id = '0xc8ad6f6ec244a93e1d66e60d1eab2ff2cb9de1f3a1f45c7bb4e9d2f720254137'
    assert trove_action['tx'] == tx_id
    assert trove_action['timestamp'] == 1627818194
    assert trove_action['kind'] == 'trove'
    assert trove_action['debt_delta']['amount'] == trove_action['debt_after']['amount']
    assert trove_action['debt_delta']['amount'] == '6029.001719188487125'
    assert trove_action['trove_operation'] == 'Open Trove'
    assert trove_action['collateral_after']['amount'] == trove_action['collateral_delta']['amount']
    assert trove_action['collateral_delta']['amount'] == '3.5'
    assert trove_action['sequence_number'] == '74148'

    # Check for account with dsproxy
    response = requests.get(
        api_url_for(
            rotkehlchen_api_server,
            'liquitytroveshistoryresource',
        ), json={
            'async_query': async_query,
            'from_timestamp': 1641529258,
            'to_timestamp': 1641529258,
            'reset_db_data': False,
        },
    )
    if async_query:
        task_id = assert_ok_async_response(response)
        result = wait_for_async_task_with_result(rotkehlchen_api_server, task_id)
    else:
        result = assert_proper_response_with_result(response)
    assert len(result[LQTY_PROXY]) == 1
    trove_action = result[LQTY_PROXY][0]
    tx_id = '0xef24b51a09151cce6728de1f9c3a0e69ca40db1dcc82f287a1743e41c90ce95b'
    assert trove_action['tx'] == tx_id
    assert trove_action['timestamp'] == 1641529258
    assert trove_action['kind'] == 'trove'
    assert trove_action['debt_after']['amount'] == '0'
    assert trove_action['debt_delta']['amount'] == '-27436.074977906493051'
    assert trove_action['trove_operation'] == 'Liquidation In Normal Mode'
    assert trove_action['collateral_after']['amount'] == '0'
    assert trove_action['collateral_delta']['amount'] == '-9.420492116554037728'
    assert trove_action['sequence_number'] == '105764'


@pytest.mark.parametrize('ethereum_accounts', [[LQTY_ADDR]])
@pytest.mark.parametrize('ethereum_modules', [['liquity']])
@pytest.mark.parametrize('should_mock_current_price_queries', [False])
@pytest.mark.parametrize('should_mock_price_queries', [True])
@pytest.mark.parametrize('mocked_price_queries', [liquity_mocked_historical_prices])
@pytest.mark.parametrize('start_with_valid_premium', [True])
def test_staking_events(rotkehlchen_api_server):
    """Test that Trove events events are correctly queried"""
    async_query = random.choice([True, False])
    response = requests.get(
        api_url_for(
            rotkehlchen_api_server,
            'liquitystakinghistoryresource',
        ), json={
            'async_query': async_query,
            'from_timestamp': 0,
            'to_timestamp': 1628026696,
            'reset_db_data': False,
        },
    )
    if async_query:
        task_id = assert_ok_async_response(response)
        result = wait_for_async_task_with_result(rotkehlchen_api_server, task_id)
    else:
        result = assert_proper_response_with_result(response)

    assert LQTY_ADDR in result
    assert len(result[LQTY_ADDR]) == 1
    trove_stake = result[LQTY_ADDR][0]
    tx_id = '0xe527749c76a3af56d86c97a8f8f8ce07e191721e9e16a0f62a228f8a8ef6d295'
    assert trove_stake['tx'] == tx_id
    assert trove_stake['timestamp'] == 1627827057
    assert trove_stake['kind'] == 'stake'
    assert trove_stake['stake_after']['amount'] == trove_stake['stake_change']['amount']
    asset = trove_stake['stake_after']['asset']
    assert asset == '_ceth_0x6DEA81C8171D0bA574754EF6F8b412F2Ed88c54D'
    assert trove_stake['stake_after']['amount'] == '177.02'
    assert trove_stake['stake_operation'] == 'stake created'
    assert trove_stake['sequence_number'] == '51676'


@pytest.mark.parametrize('ethereum_accounts', [[ADDR_WITHOUT_TROVE]])
@pytest.mark.parametrize('ethereum_modules', [['liquity']])
@pytest.mark.parametrize('start_with_valid_premium', [True])
@pytest.mark.parametrize('should_mock_current_price_queries', [True])
def test_account_without_info(rotkehlchen_api_server, inquirer):  # pylint: disable=unused-argument
    """Test that we can get the status of the trove and the staked lqty"""
    async_query = random.choice([False, True])
    response = requests.get(api_url_for(
        rotkehlchen_api_server,
        'liquitytrovesresource',
    ), json={'async_query': async_query})
    if async_query:
        task_id = assert_ok_async_response(response)
        result = wait_for_async_task_with_result(rotkehlchen_api_server, task_id)
    else:
        result = assert_proper_response_with_result(response)

    assert ADDR_WITHOUT_TROVE not in result


@pytest.mark.parametrize('ethereum_accounts', [[LQTY_PROXY, ADDR_WITHOUT_TROVE, LQTY_ADDR]])
@pytest.mark.parametrize('ethereum_modules', [['liquity']])
@pytest.mark.parametrize('start_with_valid_premium', [True])
@pytest.mark.parametrize('should_mock_current_price_queries', [True])
def test_account_with_proxy(rotkehlchen_api_server, inquirer):  # pylint: disable=unused-argument
    """Test that we can get the status of a trove created using DSProxy"""
    async_query = random.choice([False, True])
    response = requests.get(api_url_for(
        rotkehlchen_api_server,
        'liquitytrovesresource',
    ), json={'async_query': async_query})
    if async_query:
        task_id = assert_ok_async_response(response)
        result = wait_for_async_task_with_result(rotkehlchen_api_server, task_id)
    else:
        result = assert_proper_response_with_result(response)

    assert LQTY_PROXY in result
    assert ADDR_WITHOUT_TROVE not in result
    assert LQTY_ADDR in result
    # test that the list of addresses was not mutated
    rotki = rotkehlchen_api_server.rest_api.rotkehlchen
    assert len(rotki.chain_manager.accounts.eth) == 3
