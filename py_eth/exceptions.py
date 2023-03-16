from typing import Optional

import requests


class ClientException(Exception):
    pass


class InvalidProxy(ClientException):
    pass


class APIException(Exception):
    pass


class ContractException(Exception):
    pass


class NFTException(Exception):
    pass


class TransactionException(Exception):
    pass


class NoSuchToken(TransactionException):
    pass


class InsufficientBalance(TransactionException):
    pass


class GasPriceTooHigh(TransactionException):
    pass


class FailedToApprove(TransactionException):
    pass


class WalletException(Exception):
    pass


class HTTPException(Exception):
    def __init__(self, response: Optional[requests.Response] = None) -> None:
        self.response = response
        self.json_response = self.response.json()
        if self.response:
            self.status_code = response.status_code

    def __str__(self):
        if self.json_response:
            return f'{self.status_code}: {self.json_response}'

        return f'{self.status_code}'
