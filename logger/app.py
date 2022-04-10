"""
CMPT 756 Final Project
Application logging service
"""

# Standard Library Modules
import logging
import sys

# Installed packages
from flask import Blueprint
from flask import Flask
from flask import Response
from http import HTTPStatus
from flask import request
from datetime import datetime

import requests
import json
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
    "endpoint": ["create_log"]}

# db = {}


@bp.route("/", methods=["GET"])
@metrics.do_not_track()
def first_endpoint():
    return Response(
        "",
        status=HTTPStatus.OK,
        mimetype="application/json",
    )


@bp.route("/health", methods=["GET"])
@metrics.do_not_track()
def health_check():
    # data = {"status": "Healthy"}
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


@bp.route("/create_log/", methods=["POST"])
def create_log():
    """
    Logger service to log every event happening in the marketplace application.
    Each log will have a user_id, service_name, operation_name,
    status_code and operation time
    """
    print("Test check inside the create event")
    try:
        content = request.get_json()
        user_id = content["users_id"]
        service_name = content["service_name"]
        operation_name = content["operation_name"]
        status_code = content["status_code"]
        message = content["message"]

    except Exception as e:
        return json.dumps({"message": repr(e), "status_code": "500"})
    url = db["name"] + "/" + db["endpoint"][1]
    requests.post(
        url,
        json={
            "objtype": "logger",
            "logger_id": user_id,
            "service_name": service_name,
            "operation_name": operation_name,
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "status_code": status_code,
            "message": message,
        },
    )
    return Response(
        "Log Created",
        status=HTTPStatus.OK,
        mimetype="application/json",
    )


@bp.route("/read_log/<user_id>", methods=["GET"])
def read_log(user_id):
    """
    Function to read logs from a user within a time frame

    Args:
        user_id (str): Target user id to read logs from
    """
    url = db["name"] + "/" + db["endpoint"][0]

    payload = {"objtype": "logger", "objkey": user_id}
    requests.get(url, params=payload)
    return Response(
        "Log Read",
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


app.register_blueprint(bp, url_prefix="/api/v1/logger/")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logging.error("Usage: app.py <service-port>")
        sys.exit(-1)
    p = int(sys.argv[1])
    # Do not set debug=True, it will disable Prometheus metrics
    app.run(host="0.0.0.0", port=p, threaded=True)
