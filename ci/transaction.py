"""
Python  API for the music service.
"""

# Standard library modules

# Installed packages
import requests


class Transaction():
    """Python API for the images service.

    Handles the details of formatting HTTP requests and decoding
    the results.

    Parameters
    ----------
    url: string
        The URL for accessing the users service. Often
        'http://transaction:30002/'. Note the trailing slash.
    """

    def __init__(self, url):
        self._url = url

    def create(self, transaction_id, seller_id, images_id):
        r = requests.post(
            self._url + "create_transaction/",
            json={
                "transaction_id": transaction_id,
                "seller_id": seller_id,
                "images_id": images_id,
            },
        )
        return r.status_code

    def read(self, transaction_id):
        r = requests.get(self._url + "read_transaction/" + transaction_id)

        return r.status_code