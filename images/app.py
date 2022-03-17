"""
CMPT 756 Final Project
Services pertaining to logging services
"""

# Standard Library Modules
import logging
import sys

# Installed packages
from flask import Blueprint
from flask import Flask
from flask import Response
from http import HTTPStatus
from flask import jsonify


from prometheus_flask_exporter import PrometheusMetrics


# Application Code Starts here

app = Flask(__name__)

metrics = PrometheusMetrics(app, group_by="endpoint")
metrics.info("app_info", "Logger Application Info", version="1.0.0")

bp = Blueprint("app", __name__)


# docker internal host: 172.17.0.2


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
