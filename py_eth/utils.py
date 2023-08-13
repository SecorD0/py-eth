from typing import Union, Optional

import requests
from eth_typing import ChecksumAddress
from eth_utils import to_checksum_address

from py_eth import exceptions


def api_key_required(func):
    """Check if the Blockscan API key is specified."""

    def func_wrapper(self, *args, **kwargs):
        if not self.client.network.api.key or not self.client.network.api.functions:
            raise exceptions.APIException('To use this function, you must specify the explorer API key!')

        else:
            return func(self, *args, **kwargs)

    return func_wrapper


def checksum(address: str) -> ChecksumAddress:
    """
    Convert an address to checksummed.

    Args:
        address (str): the address.

    Returns:
        ChecksumAddress: the checksummed address.

    """
    return to_checksum_address(address)


def requests_get(url: str, **kwargs) -> Optional[dict]:
    """
    Make a GET request and check if it was successful.

    Args:
        url (str): a URL.
        **kwargs: arguments for a GET request, e.g. 'params', 'headers', 'data' or 'json'.

    Returns:
        Optional[dict]: received dictionary in response.

    """
    response = requests.get(url, **kwargs)
    json_response = response.json()
    if response.status_code <= 201:
        status = json_response.get('status')
        if status is not None and not int(status):
            raise exceptions.HTTPException(response=response)

        return json_response

    raise exceptions.HTTPException(response=response)


def get_coin_symbol(chain_id: Union[int, str]) -> str:
    """
    Get a coin symbol on a network with the specified ID.

    Args:
        chain_id (Union[int, str]): the network ID.

    Returns:
        str: the coin symbol.

    """
    response = requests_get('https://chainid.network/chains.json')
    network = next((network for network in response if network['chainId'] == int(chain_id)), None)
    if network:
        return network['nativeCurrency']['symbol']

    return ''
