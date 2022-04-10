"""
CMPT 756 Final Project
Application Image service
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

from uuid import uuid4
import requests


from prometheus_flask_exporter import PrometheusMetrics


# Application Code Starts here

app = Flask(__name__)

metrics = PrometheusMetrics(app, group_by="endpoint")
metrics.info("app_info", "Logger Application Info", version="1.0.0")

bp = Blueprint("app", __name__)

db = {
    "name": "http://cmpt756marketplacedb:30004/api/v1/datastore",
    "endpoint": ["read", "write", "delete", "update"],
}

db_logger = {
    "name": "http://logger:30003/api/v1/logger",
    "endpoint": ["create_log"],
}

# docker internal host: 172.17.0.2


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


@bp.route("/create_image/", methods=["POST"])
def create_image():
    """
    Function to create an image item on the database

    Returns:
        JSON: JSON object depicting the response from hitting the database
    """
    # headers = request.headers
    # # check header here
    # if "Authorization" not in headers:
    #     return Response(
    #         json.dumps({"error": "missing auth"}),
    #         status=401,
    #         mimetype="application/json",
    #     )
    # print(request.get_json())

    service_name = "images"
    operation_name = "create_image"
    user_id = None

    try:
        content = request.get_json()
        image_id = content["images_id"] if "images_id" in content \
            else str(uuid4())
        user_id = content["users_id"]

    except Exception as e:

        # status_code = HTTPStatus.INTERNAL_SERVER_ERROR

        return Response(
            repr(e),
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
            mimetype="application/json",
        )

    url = db["name"] + "/" + db["endpoint"][1]
    now = datetime.now()

    requests.post(
        url,
        json={
            "objtype": "images",
            "images_id": image_id,
            "users_id": user_id,
            "uploaded_on": now.strftime("%Y-%m-%dT%H:%M:%S"),
        },
    )

    # # logging the event
    # response_message = response.json()
    # calling the logger function to write into logger table
    log_writer(user_id, service_name, operation_name, "200", "image added")

    return Response(
        "Image Created",
        status=HTTPStatus.OK,
        mimetype="application/json",
    )


@bp.route("/read_image/<image_id>", methods=["GET"])
def read_image(image_id):
    """
    Function to read image metadata
    """
    # headers = request.headers
    # # check header here
    # if "Authorization" not in headers:
    #     return Response(
    #         json.dumps({"error": "missing auth"}),
    #         status=401,
    #         mimetype="application/json",
    #     )

    payload = {"objtype": "images", "objkey": image_id}
    url = db["name"] + "/" + db["endpoint"][0]
    requests.get(
        url,
        params=payload,
    )
    return Response(
        "Image Read",
        status=HTTPStatus.OK,
        mimetype="application/json",
    )


@bp.route("/change_owner/<image_id>", methods=["PUT"])
def update_image(image_id):
    """
    Function to update image metadata

    Returns:
        JSON: Response JSON
    """
    # headers = request.headers
    # # check header here
    # if "Authorization" not in headers:
    #     return Response(
    #         json.dumps({"error": "missing auth"}),
    #         status=401,
    #         mimetype="application/json",
    #     )
    service_name = "images"
    operation_name = "update_image"
    user_id = None

    try:
        content = request.get_json()
        new_user_id = content["users_id"]

    except Exception as e:
        status_code = "500"
        message = repr(e)
        log_writer(user_id, service_name, operation_name, status_code, message)

        return Response(
            repr(e),
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
            mimetype="application/json",
        )

        # return json.dumps({"message": "error reading arguments"})

    payload = {"objtype": "images", "objkey": image_id}
    url = db["name"] + "/" + db["endpoint"][3]

    response = requests.put(
        url,
        params=payload,
        json={"users_id": new_user_id},
    )

    # logging the event
    response.json()
    # calling the logger function to write into logger table
    log_writer(user_id, service_name, operation_name, "200", "image updated")

    return Response(
        "Image Updated",
        status=HTTPStatus.OK,
        mimetype="application/json",
    )


@bp.route("/delete_image/<image_id>", methods=["DELETE"])
def delete_image(image_id):
    """
    Function to delete image

    Returns:
        JSON: Response JSON
    """
    # headers = request.headers
    # # check header here
    # if "Authorization" not in headers:
    #     return Response(
    #         json.dumps({"error": "missing auth"}),
    #         status=401,
    #         mimetype="application/json",
    #     )

    service_name = "images"
    operation_name = "delete_image"
    user_id = None

    payload = {"objtype": "images", "objkey": image_id}
    url = db["name"] + "/" + db["endpoint"][0]
    image_response = requests.get(
        url,
        params=payload,
    )
    user_id = image_response["Items"][0]["users_id"]

    url = db["name"] + "/" + db["endpoint"][2]
    response = requests.delete(
        url,
        params={"objtype": "images", "objkey": image_id},
    )

    # logging the event
    response.json()

    # calling the logger function to write into logger table
    log_writer(user_id, service_name, operation_name, "200", "image deleted")
    return Response(
        "Image Deleted",
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


app.register_blueprint(bp, url_prefix="/api/v1/images/")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logging.error("missing port arg 1")
        sys.exit(-1)
    p = int(sys.argv[1])
    # Do not set debug=True, it will disable Prometheus metrics
    app.run(host="0.0.0.0", port=p, threaded=True)
