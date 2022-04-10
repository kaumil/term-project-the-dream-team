"""
Simple test that calls `test` then `shutdown`.

Result of test in program return code:
0: Test succeeded
1: Test failed
"""

# Standard library modules
import argparse
import sys

# Installed packages
import requests


def parse_args():
    argp = argparse.ArgumentParser(
        "db_test",
        description="Simple test of db service"
    )
    argp.add_argument("name", help="DNS name or IP address of db server")
    argp.add_argument("port", type=int, help="Port number of db server")
    return argp.parse_args()


def get_url(name, port):
    return "http://{}:{}/api/v1/datastore/".format(name, port)


def test(args):
    url = get_url(args.name, args.port)
    r = requests.get(url + "health")
    return r.status_code


if __name__ == "__main__":
    args = parse_args()
    trc = test(args)
    if trc == 200:
        sys.exit(0)
    else:
        sys.exit(1)
