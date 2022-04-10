"""
SFU CMPT 756
Application User service
"""

# Standard library modules
import logging
import sys
import time

# Installed packages
from flask import Blueprint
from flask import Flask
from flask import request
from flask import Response
from http import HTTPStatus
from uuid import uuid4

import json
import jwt

from prometheus_flask_exporter import PrometheusMetrics

import requests

# The application

app = Flask(__name__)

metrics = PrometheusMetrics(app)
metrics.info("app_info", "User process")

bp = Blueprint("app", __name__)

db = {
    "name": "http://cmpt756marketplacedb:30004/api/v1/datastore",
    "endpoint": ["read", "write", "delete", "update"],
}

db_logger = {
    "name": "http://logger:30003/api/v1/logger",
    "endpoint": ["create_log"]}


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


@bp.route("/health")
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


@bp.route("/update_user/<user_id>", methods=["PUT"])
def update_user(user_id):
    """
    Function to update user data

    Args:
        user_id (str): User ID

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
    try:
        content = request.get_json()
        username = content["username"]
        password = content["password"]
        role = content["users_role"]
        disabled = content["disabled"]
    except Exception as e:
        # return json.dumps({"message": repr(e)})
        return Response(
            repr(e),
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
            mimetype="application/json",
        )

    url = db["name"] + "/" + db["endpoint"][3]
    requests.put(
        url,
        params={"objtype": "users", "objkey": user_id},
        json={
            "username": username,
            "password": password,
            "users_role": role,
            "disabled": disabled,
        },
    )
    return Response(
        "User Updated",
        status=HTTPStatus.OK,
        mimetype="application/json",
    )


@bp.route("/create_user/", methods=["POST"])
def create_user():
    """
    Create a user.
    If a record already exists with the same fname, lname, and email,
    the old UUID is replaced with a new one.
    """
    try:
        content = request.get_json()
        username = content["username"]
        password = content["password"]
        role = content["users_role"]
        user_id = content["users_id"] if "users_id" in content\
            else str(uuid4())

    except Exception as e:
        # return json.dumps({"message": repr(e)})
        return Response(
            repr(e),
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
            mimetype="application/json",
        )

    url = db["name"] + "/" + db["endpoint"][1]

    requests.post(
        url,
        json={
            "objtype": "users",
            "users_id": user_id,
            "username": username,
            "password": password,
            "users_role": role,
            "disabled": "False",
        },
    )
    return Response(
        "User Created",
        status=HTTPStatus.OK,
        mimetype="application/json",
    )


@bp.route("/delete_user/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    # headers = request.headers
    # check header here
    # if "Authorization" not in headers:
    #     return Response(
    #         json.dumps({"error": "missing auth"}),
    #         status=401,
    #         mimetype="application/json",
    #     )
    url = db["name"] + "/" + db["endpoint"][2]

    requests.delete(url, params={"objtype": "users", "objkey": user_id})
    return Response(
        "User Deleted",
        status=HTTPStatus.OK,
        mimetype="application/json",
    )


@bp.route("/get_user/<user_id>", methods=["GET"])
def get_user(user_id):
    # headers = request.headers
    # check header here
    # if "Authorization" not in headers:
    #     return Response(
    #         json.dumps({"error": "missing auth"}),
    #         status=401,
    #         mimetype="application/json",
    #     )
    payload = {"objtype": "users", "objkey": user_id}
    url = db["name"] + "/" + db["endpoint"][0]
    requests.get(url, params=payload)
    return Response(
        "User Read",
        status=HTTPStatus.OK,
        mimetype="application/json",
    )


@bp.route("/login/", methods=["PUT"])
def login():
    try:
        content = request.get_json()
        uid = content["users_id"]
    except Exception as e:
        # return json.dumps({"message": repr(e)})
        return Response(
            repr(e),
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
            mimetype="application/json",
        )

    url = db["name"] + "/" + db["endpoint"][0]
    response = requests.get(url, params={"objtype": "users", "objkey": uid})
    data = response.json()
    if len(data["Items"]) > 0:
        encoded = jwt.encode(
            {"user_id": uid, "time": time.time()}, "secret", algorithm="HS256"
        )
    return encoded


@bp.route("/logoff/", methods=["PUT"])
def logoff():
    try:
        content = request.get_json()
        _ = content["jwt"]
    except Exception as e:
        return json.dumps({"message": repr(e)})
    return {}


# All database calls will have this prefix.  Prometheus metric
# calls will not---they will have route '/metrics'.  This is
# the conventional organization.
app.register_blueprint(bp, url_prefix="/api/v1/users/")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logging.error("Usage: app.py <service-port>")
        sys.exit(-1)

    p = int(sys.argv[1])
    # Do not set debug=True---that will disable the Prometheus metrics
    app.run(host="0.0.0.0", port=p, threaded=True)
