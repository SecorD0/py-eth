import json
from typing import Union
from urllib.request import urlopen

from py_eth import exceptions
from py_eth.data import types
from py_eth.data.models import NFT
from py_eth.utils import requests_get


class NFTs:
    """
    Class with functions related to NTFs.

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

    def get_info(self, contract: types.Contract, token_id: Union[int, str] = None) -> NFT:
        """
        Get information about a NFT.

        Args:
            contract (Contract): the contract address or instance of a NFT collection.
            token_id (Union[int, str]): the NFT ID to parse the owner and attributes. (None)

        Returns:
            NFT: the NFT.

        """
        contract_address, abi = self.client.contracts.get_contract_attributes(contract)
        contract = self.client.contracts.default_nft(contract_address)
        nft = NFT(contract_address=contract_address)
        nft.name = contract.functions.name().call()
        nft.symbol = contract.functions.symbol().call()
        nft.total_supply = contract.functions.totalSupply().call()
        if token_id:
            try:
                token_id = int(token_id)
                if token_id >= nft.total_supply:
                    exceptions.NFTException('The token ID exceeds total supply!')

                nft.id = token_id
                try:
                    nft.owner = contract.functions.ownerOf(token_id).call()
                except:
                    pass

                image_url = contract.functions.tokenURI(token_id).call()
                if 'data:application/json' in image_url:
                    with urlopen(image_url) as response:
                        response = json.loads(response.read())

                else:
                    if 'ipfs://' in image_url:
                        image_url = image_url.replace('ipfs://', 'https://ipfs.io/ipfs/')

                    nft.image_url = image_url
                    response = requests_get(image_url)

                if 'attributes' in response and response['attributes']:
                    nft.parse_attributes(response['attributes'])

            except:
                pass

        return nft
