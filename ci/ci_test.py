"""
Integration test of the CMPT 756 sample applicaton.

Result of test in program return code:
0: Test succeeded
1: Test failed
"""

# Standard library modules
import argparse
from email import message
import os
import sys
from time import sleep

# Installed packages

# Local modules
import create_tables
import users
import images
import transaction
import logger

# The services check only that we pass an authorization,
# not whether it's valid


def parse_args():
    """Parse the command-line arguments.

    Returns
    -------
    namespace
        A namespace of all the arguments, augmented with names
        'user_url' and 'music_url'.
    """
    argp = argparse.ArgumentParser(
        "ci_test", description="Integration test of CMPT 756 sample application"
    )
    argp.add_argument("users_address", help="DNS name or IP address of users service.")
    argp.add_argument("users_port", type=int, help="Port number of users service.")
    argp.add_argument(
        "images_address", help="DNS name or IP address of images service."
    )
    argp.add_argument("images_port", type=int, help="Port number of images service.")
    argp.add_argument(
        "transaction_address", help="DNS name or IP address of transaction service."
    )
    argp.add_argument(
        "transaction_port", type=int, help="Port number of transaction service."
    )
    argp.add_argument(
        "logger_address", help="DNS name or IP address of logger service."
    )
    argp.add_argument("logger_port", type=int, help="Port number of logger service.")
    
    args = argp.parse_args()
    args.users_url = "http://{}:{}/api/v1/users/".format(
        args.users_address, args.users_port
    )
    args.images_url = "http://{}:{}/api/v1/images/".format(
        args.images_address, args.images_port
    )
    args.transaction_url = "http://{}:{}/api/v1/transaction/".format(
        args.transaction_address, args.transaction_port
    )
    args.logger_url = "http://{}:{}/api/v1/logger/".format(
        args.logger_address, args.logger_port
    )
    return args


def get_env_vars(args):
    """Augment the arguments with environment variable values.

    Parameters
    ----------
    args: namespace
        The command-line argument values.

    Environment variables
    ---------------------
    AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
        SVC_LOADER_TOKEN, DYNAMODB_URL: string
        Environment variables specifying these AWS access parameters.

    Modifies
    -------
    args
        The args namespace augmented with the following names:
        dynamodb_region, access_key_id, secret_access_key, loader_token,
        dynamodb_url

        These names contain the string values passed in the corresponding
        environment variables.

    Returns
    -------
    Nothing
    """
    # These are required to be present
    args.dynamodb_region = os.getenv("AWS_REGION")
    args.access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    args.secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    args.loader_token = os.getenv("SVC_LOADER_TOKEN")
    args.dynamodb_url = os.getenv("DYNAMODB_URL")


def setup(args):
    """Create the DynamoDB tables.

    Parameters
    ----------
    args: namespace
        The arguments specifying the tables. Uses dynamodb_url,
        dynamodb_region, access_key_id, secret_access_key, table_suffix.
    """
    create_tables.create_tables(
        args.dynamodb_url,
        args.dynamodb_region,
        args.access_key_id,
        args.secret_access_key,
        "users",
        "images",
        "transactions",
        "logger",
    )


def run_test(args):
    """Run the tests.

    Parameters
    ----------
    args: namespace
        The arguments for the test. Uses music_url.

    Prerequisites
    -------------
    The DyamoDB tables must already exist.

    Returns
    -------
    number
        An HTTP status code representing the test result.
        Some "pseudo-HTTP" codes are defined in the 600 range
        to indicate conditions that are not included in the HTTP
        specification.


    """

    userv = users.Users(args.users_url)
    imgv = images.Images(args.images_url)
    transv = transaction.Transaction(args.transaction_url)
    logv = logger.Logger(args.logger_url)

    users_id, username, password, role, disabled = (
        "e0038fea-f9ed-4c65-aa0e-fc189206faee",
        "foo",
        "bar",
        "buyer",
        "disabled",
    )

    trc = userv.create(users_id, username, password, role, disabled)
    if trc == 500:
        sys.exit(1)
    trc1 = userv.read(users_id)

    images_id, users_id = (
        "c97dee22-7270-4fb2-ad25-8386b05d8dc2",
        "567dce7f-b7b4-4efd-b75e-2b98592abe6d",
    )
    trc = imgv.create(images_id, users_id)
    if trc == 500:
        sys.exit(1)
    trc2 = imgv.read(images_id)

    transaction_id, seller_id, images_id = (
        "0b08fc9f-ea46-4b90-b8ae-35fe856da0d8",
        "567dce7f-b7b4-4efd-b75e-2b98592abe6d",
        "51b616bd-cc17-4075-b539-d8a013b6522a",
    )
    trc = transv.create(transaction_id, seller_id, images_id)
    if trc == 500:
        sys.exit(1)
    trc3 = transv.read(transaction_id)

    return 200


if __name__ == "__main__":
    args = parse_args()
    get_env_vars(args)
    setup(args)
    sleep(20)
    trc = run_test(args)
    if trc != 200:
        sys.exit(1)
