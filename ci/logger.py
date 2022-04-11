"""
Python  API for the music service.
"""

# Standard library modules

# Installed packages
import requests


class Logger():
    """Python API for the images service.

    Handles the details of formatting HTTP requests and decoding
    the results.

    Parameters
    ----------
    url: string
        The URL for accessing the users service. Often
        'http://logger:30003/'. Note the trailing slash.
    """

    def __init__(self, url):
        self._url = url

    def create(self, user_id, service_name, operation_name, status_code, message):
        r = requests.post(
            self._url + "create_log/",
            json={
                "user_id": user_id,
                "service_name": service_name,
                "operation_name": operation_name,
                "status_code": status_code,
                "message": message,
            },
        )
        return r.status_code

    def read(self, users_id):
        r = requests.get(self._url + "read_log/" + users_id)

        return r.status_code