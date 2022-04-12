"""
Python  API for the music service.
"""

# Standard library modules

# Installed packages
import requests


class Images():
    """Python API for the images service.

    Handles the details of formatting HTTP requests and decoding
    the results.

    Parameters
    ----------
    url: string
        The URL for accessing the users service. Often
        'http://images:30001/'. Note the trailing slash.
    """

    def __init__(self, url):
        self._url = url

    def create(self, images_id, users_id):
        r = requests.post(
            self._url + "create_image/",
            json={
                "images_id": images_id,
                "users_id": users_id,
            },
        )
        return r.status_code

    def read(self, images_id):
        r = requests.get(self._url + "read_image/" + images_id)

        return r.status_code
