"""
Python  API for the music service.
"""

# Standard library modules

# Installed packages
import requests


class Users():
    """Python API for the users service.

    Handles the details of formatting HTTP requests and decoding
    the results.

    Parameters
    ----------
    url: string
        The URL for accessing the users service. Often
        'http://users:30000/'. Note the trailing slash.
    """

    def __init__(self, url):
        self._url = url

    def create(self, users_id, username, password, users_role, disabled):
        r = requests.post(
            self._url + "create_user/",
            json={
                "users_id": users_id,
                "username": username,
                "password": password,
                "users_role": users_role,
                "disabled": disabled,
            },
        )
        return r.status_code

    def read(self, users_id):
        r = requests.get(self._url + "get_user/" + users_id)
        return r.status_code
