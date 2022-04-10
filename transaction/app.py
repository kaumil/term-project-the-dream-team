"""
CMPT 756 Final Project
Application Transaction service
"""

# Standard Library Modules
from datetime import datetime
import logging
import sys

# Installed packages
from flask import Blueprint
from flask import Flask
from flask import request
from flask import Response
from http import HTTPStatus
from uuid import uuid4

import json
import requests

from prometheus_flask_exporter import PrometheusMetrics


# Application Code Starts here

app = Flask(__name__)

metrics = PrometheusMetrics(app, group_by="endpoint")
metrics.info("app_info", "Logger Application Info", version="1.0.0")

bp = Blueprint("app", __name__)


# docker internal host: 172.17.0.2

db = {
    "name": "http://cmpt756marketplacedb:30004/api/v1/datastore",
    "endpoint": ["read", "write", "delete", "update"],
}

db_logger = {
    "name": "http://logger:30003/api/v1/logger",
    "endpoint": ["create_log"]
}

db_image = {
    "name": "http://images:30001/api/v1/images",
    "endpoint": ["update"]
}

# db = {}


@bp.route("/", methods=["GET"])
@metrics.do_not_track()
def first_endpoint():
    """
    First endpoint

    Returns:
        flask.Response: Flask Response
    """
    return Response(
        "",
        status=HTTPStatus.OK,
        mimetype="application/json",
    )


@bp.route("/health", methods=["GET"])
@metrics.do_not_track()
def health_check():
    """
    Function for health check

    Returns:
        flask.Response: Flask Response
    """
    return Response(
        "Healthy",
        status=HTTPStatus.OK,
        mimetype="application/json",
    )


@bp.route("/readiness")
@metrics.do_not_track()
def readiness():
    """
    Function to check readiness

    Returns:
        flask.Response: Flask Response
    """
    return Response(
        "Ready",
        status=HTTPStatus.OK,
        mimetype="application/json",
    )


def log_writer(user_id, service_name, operation_name, status_code, message):
    # writing into the logger db
    url_logger = db_logger["name"] + "/" + db_logger["endpoint"][0]
    response_logger = requests.post(
        url_logger,
        json={
            "users_id": user_id,
            "service_name": service_name,
            "operation_name": operation_name,
            "status_code": status_code,
            "message": message,
        },
    )

    return response_logger


@bp.route("/create_transaction/", methods=["POST"])
def create_transaction():
    """
    Function to create a transaction in the database

    Returns:
        JSON: Response JSON
    """
    # headers = request.headers

    # check header here
    # if "Authorization" not in headers:
    #     return Response(
    #         json.dumps({"error": "missing auth"}),
    #         status=401,
    #         mimetype="application/json",
    #     )

    service_name = "transactions"
    operation_name = "create_transaction"
    seller_id = None

    try:
        content = request.get_json()
        transaction_id = (
            content["transactions_id"] if "transactions_id" in content
            else str(uuid4())
        )
        seller_id = content["seller_id"]
        image_id = content["images_id"]
    except Exception as e:

        status_code = "500"
        message = repr(e)
        log_writer(
            seller_id,
            service_name,
            operation_name,
            status_code,
            message)
        return Response(
            repr(e),
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
            mimetype="application/json",
        )
        # return json.dumps({"message": "error reading arguments"})

    url = db["name"] + "/" + db["endpoint"][1]

    requests.post(
        url,
        json={
            "objtype": "transactions",
            "transactions_id": transaction_id,
            "images_id": image_id,
            "seller_id": seller_id,
            "sold": "False",
        },
    )

    # calling the logger function to write into logger table
    log_writer(
        seller_id,
        service_name,
        operation_name,
        "200",
        "transaction created")
    return Response(
        "Transaction Created",
        status=HTTPStatus.OK,
        mimetype="application/json",
    )


@bp.route("/read_transaction/<transaction_id>", methods=["GET"])
def read_transaction(transaction_id):
    """
    Function to read transaction metadata

    Args:
        transaction_id (str): Transaction id

    Returns:
        JSON: Response JSON
    """
    # headers = request.headers
    # check header here
    # if "Authorization" not in headers:
    #     return Response(
    #         json.dumps({"error": "missing auth"}),
    #         status=401,
    #         mimetype="application/json",
    #     )

    payload = {"objtype": "transactions", "objkey": transaction_id}
    url = db["name"] + "/" + db["endpoint"][0]
    requests.get(
        url,
        params=payload,
    )
    return Response(
        "Transaction Read",
        status=HTTPStatus.OK,
        mimetype="application/json",
    )


@bp.route("/change_transaction/<transaction_id>", methods=["PUT"])
def update_transaction(transaction_id):
    """
    Function to update transaction

    Args:
        transaction_id (str): Transaction id

    Returns:
        JSON: Response JSON
    """
    # headers = request.headers
    # check header here
    # if "Authorization" not in headers:
    #     return Response(
    #         json.dumps({"error": "missing auth"}),
    #         status=401,
    #         mimetype="application/json",
    #     )

    service_name = "transactions"
    operation_name = "change_transaction"
    buyer_id = None

    try:
        content = request.get_json()
        buyer_id = content["buyer_id"]

    except Exception as e:

        status_code = "500"
        message = repr(e)
        json.dumps({"message": message, "status_code": status_code})
        log_writer(
            buyer_id,
            service_name,
            operation_name,
            status_code,
            message)

        return Response(
            repr(e),
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
            mimetype="application/json",
        )
        # return json.dumps({"message": "error reading arguments"})

    payload = {"objtype": "transactions", "objkey": transaction_id}
    url = db["name"] + "/" + db["endpoint"][0]
    response = requests.get(
        url,
        params=payload,
    )

    transaction_data = response.json()
    # Changing image ownership

    image_id = transaction_data["Items"][0]["images_id"]
    image_payload = {"objtype": "images", "objkey": image_id}
    imagedb_url = db["name"] + "/" + db["endpoint"][0]
    requests.put(
        imagedb_url,
        params=image_payload,
        json={"user_id": buyer_id},
    )

    # Updating the transaction
    url = db["name"] + "/" + db["endpoint"][3]
    now = datetime.now()
    response = requests.put(
        url,
        params=payload,
        json={
            "buyer_id": buyer_id,
            "sold_on": now.strftime("%Y-%m-%dT%H:%M:%S"),
        },
    )

    # logging the event
    response.json()

    # calling the logger function to write into logger table
    log_writer(
        buyer_id,
        service_name,
        operation_name,
        "200",
        "transaction updated")

    return Response(
        "Transaction Updated",
        status=HTTPStatus.OK,
        mimetype="application/json",
    )


@bp.route("/delete_transaction/<transaction_id>", methods=["DELETE"])
def delete_transaction(transaction_id):
    """
    Function to delete transaction

    Args:
        transaction_id (str): Transaction id

    Returns:
        JSON: Response JSON
    """
    # headers = request.headers
    # check header here
    # if "Authorization" not in headers:
    #     return Response(
    #         json.dumps({"error": "missing auth"}),
    #         status=401,
    #         mimetype="application/json",
    #     )

    service_name = "transactions"
    operation_name = "delete_transaction"
    buyer_id = None

    payload = {"objtype": "transactions", "objkey": transaction_id}
    url = db["name"] + "/" + db["endpoint"][0]
    response = requests.get(
        url,
        params=payload,
    )

    buyer_id = response.json()["Items"][0]["buyer_id"]

    url = db["name"] + "/" + db["endpoint"][2]
    response = requests.delete(
        url,
        params={"objtype": "transactions", "objkey": transaction_id},
    )

    # calling the logger function to write into logger table
    log_writer(
        buyer_id,
        service_name,
        operation_name,
        "200",
        "transaction deleted")

    return Response(
        "Transaction Deleted",
        status=HTTPStatus.OK,
        mimetype="application/json",
    )


@bp.after_request
def add_header(response):
    """
    Function to add headers to the Flask Response

    Args:
        response (flask.Response): Flask Response Object

    Returns:
        flask.Response : Flask Response Object
    """
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["Cache-Control"] = "public, max-age=0"
    return response


app.register_blueprint(bp, url_prefix="/api/v1/transaction/")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logging.error("missing port arg 1")
        sys.exit(-1)
    p = int(sys.argv[1])
    # Do not set debug=True, it will disable Prometheus metrics
    app.run(host="0.0.0.0", port=p, threaded=True)
