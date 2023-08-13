import json
import time
from typing import Union, Optional, List, Dict, Any, Tuple

from eth_typing import ChecksumAddress
from evmdasm import EvmBytecode
from pretty_utils.type_functions.strings import text_between
from web3.contract import Contract

from py_eth.data import types
from py_eth.data.models import DefaultABIs, ABI, Function, RawContract
from py_eth.utils import checksum, requests_get


class Contracts:
    """
    Class with functions related to contracts.

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

    @staticmethod
    def get_signature(hex_signature: str) -> Optional[list]:
        """
        Find all matching signatures in the database of https://www.4byte.directory/.

        Args:
            hex_signature (str): a signature hash.

        Returns:
            Optional[list]: matches found.

        """
        try:
            response = requests_get(f'https://www.4byte.directory/api/v1/signatures/?hex_signature={hex_signature}')
            results = response['results']
            return [m['text_signature'] for m in sorted(results, key=lambda result: result['created_at'])]

        except:
            return

    @staticmethod
    def parse_function(text_signature: str) -> dict:
        """
        Construct a function dictionary for the Application Binary Interface (ABI) based on the provided text signature.

        Args:
            text_signature (str): a text signature, e.g. approve(address,uint256).

        Returns:
            dict: the function dictionary for the ABI.

        """
        name, sign = text_signature.split('(', 1)
        sign = sign[:-1]
        tuples = []
        while '(' in sign:
            tuple_ = text_between(text=sign[:-1], begin='(', end=')')
            tuples.append(tuple_.split(',') or [])
            sign = sign.replace(f'({tuple_})', 'tuple')

        inputs = sign.split(',')
        if inputs == ['']:
            inputs = []

        function = {
            'type': 'function',
            'name': name,
            'inputs': [],
            'outputs': [{'type': 'uint256'}]
        }
        i = 0
        for type_ in inputs:
            input_ = {'type': type_}
            if type_ == 'tuple':
                input_['components'] = [{'type': comp_type} for comp_type in tuples[i]]
                i += 1

            function['inputs'].append(input_)

        return function

    @staticmethod
    def get_contract_attributes(contract: types.Contract) -> Tuple[ChecksumAddress, Optional[list]]:
        """
        Convert different types of contract to its address and ABI.

        Args:
            contract (Contract): the contract address or instance.

        Returns:
            Tuple[ChecksumAddress, Optional[list]]: the checksummed contract address and ABI.

        """
        if isinstance(contract, (Contract, RawContract)):
            return contract.address, contract.abi

        return checksum(contract), None

    def get_abi(self, contract_address: types.Contract, raw_json: bool = False) -> Union[str, List[Dict[str, Any]]]:
        """
        Get a contract ABI from the Blockscan API, if unsuccessful, parses it based on the contract source code
            (it may be incorrect or incomplete).

        Args:
            contract_address (Contract): the contract address or instance.
            raw_json (bool): if True, it returns serialize string, otherwise it returns Python list. (False)

        Returns:
            Union[str, List[Dict[str, Any]]]: the ABI.

        """
        contract_address, abi = self.get_contract_attributes(contract_address)
        abi = []
        if self.client.network.api and self.client.network.api.key:
            try:
                abi = self.client.network.api.functions.contract.getabi(contract_address)['result']
                abi = json.loads(abi)

            except:
                abi = []

        if not abi:
            bytecode = self.client.w3.eth.get_code(contract_address)
            opcodes = EvmBytecode(bytecode).disassemble()
            hex_signatures = set()
            for i in range(len(opcodes) - 3):
                if (
                        opcodes[i].name == 'PUSH4'
                        and opcodes[i + 1].name == 'EQ'
                        and opcodes[i + 2].name == 'PUSH2'
                        and opcodes[i + 3].name == 'JUMPI'
                ):
                    hex_signatures.add(opcodes[i].operand)
            hex_signatures = list(hex_signatures)

            text_signatures = []
            for i, hex_signature in enumerate(hex_signatures):
                signature_for_hash = Contracts.get_signature(hex_signature=hex_signature)
                while signature_for_hash is None:
                    time.sleep(1)
                    signature_for_hash = Contracts.get_signature(hex_signature=hex_signature)

                if signature_for_hash:
                    text_signatures.append(signature_for_hash[0])

            for text_signature in text_signatures:
                try:
                    abi.append(Contracts.parse_function(text_signature=text_signature))

                except:
                    pass

        if raw_json:
            return json.dumps(abi)

        return abi

    def default_token(self, contract_address: types.Contract) -> Contract:
        """
        Get a token contract instance with a standard set of functions.

        Args:
            contract_address (Contract): the contract address or instance of token.

        Returns:
            Contract: the token contract instance.

        """
        contract_address, abi = self.get_contract_attributes(contract_address)
        return self.client.w3.eth.contract(address=contract_address, abi=DefaultABIs.Token)

    def default_nft(self, contract_address: types.Contract) -> Contract:
        """
        Get a NFT contract instance with a standard set of functions.

        Args:
            contract_address (Contract): the contract address or instance of a NFT collection.

        Returns:
            Contract: the NFT contract instance.

        """
        contract_address, abi = self.get_contract_attributes(contract_address)
        return self.client.w3.eth.contract(address=contract_address, abi=DefaultABIs.NFT)

    def get(
            self, contract_address: types.Contract, abi: Optional[Union[list, str]] = None,
            proxy_address: Optional[types.Contract] = None
    ) -> Contract:
        """
        Get a contract instance.

        Args:
            contract_address (Contract): the contract address or instance.
            abi (Optional[Union[list, str]]): the contract ABI. (get it using the 'get_abi' function)
            proxy_address (Optional[Contract]): the contract proxy address. (None)

        Returns:
            Contract: the contract instance.

        """
        contract_address, contract_abi = self.get_contract_attributes(contract_address)
        if not abi and not contract_abi:
            if proxy_address:
                proxy_address, proxy_abi = self.get_contract_attributes(proxy_address)
                if not proxy_abi:
                    proxy_abi = self.get_abi(contract_address=proxy_address)

                contract_abi = proxy_abi

            else:
                contract_abi = self.get_abi(contract_address=contract_address)

        if not abi:
            abi = contract_abi

        if abi:
            return self.client.w3.eth.contract(address=contract_address, abi=abi)

        return self.client.w3.eth.contract(address=contract_address)

    def get_functions(self, contract: types.Contract) -> List[Function]:
        """
        Get functions of a contract in human-readable form.

        Args:
            contract (Contract): the contract address or instance.

        Returns:
            List[Function]: functions of the contract.

        """
        if not isinstance(contract, Contract):
            contract = self.get(contract_address=contract)

        abi = contract.abi or []
        return ABI(abi=abi).functions
