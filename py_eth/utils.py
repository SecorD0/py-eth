from typing import Union

import requests
from eth_typing import ChecksumAddress
from eth_utils import to_checksum_address

from py_eth import exceptions


def api_key_required(func):
    """Check if the explorer API key is specified."""

    def func_wrapper(self, *args, **kwargs):
        if not self.client.network.api.key:
            raise exceptions.APIException('To use this function, you must specify the explorer API key!')

        else:
            return func(self, *args, **kwargs)

    return func_wrapper


def checksum(address: str) -> ChecksumAddress:
    """
    Convert an address to checksummed.

    :param str address: the address
    :return ChecksumAddress: the checksummed address
    """
    return to_checksum_address(address)


def get_coin_symbol(chain_id: Union[int, str]) -> str:
    """
    Get a coin symbol on a network with the specified ID.

    :param Union[int, str] chain_id: the network ID
    :return str: the coin symbol
    """
    response = requests.get('https://chainid.network/chains.json').json()
    network = next((network for network in response if network['chainId'] == int(chain_id)), None)
    if network:
        return network['nativeCurrency']['symbol']

    return ''
