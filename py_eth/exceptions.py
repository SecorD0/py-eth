from typing import Optional, Dict, Any

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
    """
    An exception that occurs when an HTTP request is unsuccessful.

    Attributes:
        response (Optional[requests.Response]): a 'requests.Response' instance.
        json_response (Dict[str, Any]): a JSON response to a request.
        status_code (int): a request status code.

    """
    response: Optional[requests.Response]
    json_response: Dict[str, Any]
    status_code: int

    def __init__(self, response: Optional[requests.Response] = None) -> None:
        """
        Initialize the class.

        Args:
            response (Optional[requests.Response]): a 'requests.Response' instance.

        """
        self.response = response
        if self.response:
            self.json_response = self.response.json()
            self.status_code = response.status_code

    def __str__(self):
        if self.json_response:
            return f'{self.status_code}: {self.json_response}'

        return f'{self.status_code}'
