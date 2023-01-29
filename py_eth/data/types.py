from typing import Union

from web3 import types
from web3.contract import Contract

from .models import RawContract, TokenAmount, Ether, Wei, GWei

Address = Union[str, types.Address, types.ChecksumAddress, types.ENS]
Amount = Union[float, int, TokenAmount, Ether, Wei]
Contract = Union[str, types.Address, types.ChecksumAddress, types.ENS, RawContract, Contract]
GasLimit = Union[int, Wei]
GasPrice = Union[float, int, Wei, GWei]
