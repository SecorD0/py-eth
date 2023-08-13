from typing import Optional, Union

from eth_typing import Address
from web3.contract import Contract

from py_eth.data import types
from py_eth.data.models import Wei, TokenAmount
from py_eth.utils import checksum


class Wallet:
    """
    Class with functions related to wallet.

    Attributes:
        client (Client): the Client instance.

    """

    def __init__(self, client) -> None:
        """
        Initialize the class.

        Args:
            client (Client): the Client instance.

        """
        self.client = client

    def balance(
            self, token: Optional[types.Contract] = None, address: Optional[types.Address] = None
    ) -> Union[Wei, TokenAmount]:
        """
        Get a coin or token balance of a specified address.

        Args:
            token (Optional[Contract]): the contact address or instance of token. (coin)
            address (Optional[Address]): the address. (imported to client address)

        Returns:
            Union[Wei, TokenAmount]: the coin or token balance.

        """
        if not address:
            address = self.client.account.address

        address = checksum(address)
        if not token:
            return Wei(self.client.w3.eth.get_balance(account=address))

        contract_address, abi = self.client.contracts.get_contract_attributes(token)
        contract = self.client.contracts.default_token(contract_address=contract_address)
        return TokenAmount(
            amount=contract.functions.balanceOf(address).call(), decimals=contract.functions.decimals().call(), wei=True
        )

    def nonce(self, address: Optional[types.Contract] = None) -> int:
        """
        Get a nonce of the specified address.

        Args:
            address (Optional[Contract]): the address. (imported to client address)

        Returns:
            int: the nonce of the address.

        """
        if not address:
            address = self.client.account.address

        else:
            address, abi = self.client.contracts.get_contract_attributes(address)

        return self.client.w3.eth.get_transaction_count(address)
