"""
SFU CMPT 756
Sample application---user service.
"""

# Standard library modules
import logging
import sys
import time
import ast

# Installed packages
from flask import Blueprint
from flask import Flask
from flask import request
from flask import Response

import jwt

from prometheus_flask_exporter import PrometheusMetrics

import requests

import simplejson as json

# The application

app = Flask(__name__)

metrics = PrometheusMetrics(app)
metrics.info("app_info", "User process")

bp = Blueprint("app", __name__)

db = {
    "name": "http://172.17.0.1:30004/api/v1/datastore",
    "endpoint": ["read", "write", "delete", "update"],
}

db_logger = {"name": "http://172.17.0.1:30003/api/v1/logger", "endpoint": ["create"]}


def log_writer(
    customer_id,
    service_name,
    operation_name,
    status_code,
    message,
    request_message,
    response_message,
):
    # writing into the logger db
    print("inside log_writer")
    url_logger = db_logger["name"] + "/" + db_logger["endpoint"][0]
    print("inside log writer: url ", url_logger)
    response_logger = requests.post(
        url_logger,
        json={
            "customer_id": customer_id,
            "service_name": service_name,
            "operation_name": operation_name,
            "status_code": status_code,
            "message": message,
            "request_message": request_message,
            "response_message": response_message,
        },
    )
    print("respnese logger inside log writer:", response_logger)
    return response_logger


@bp.route("/", methods=["GET"])
@metrics.do_not_track()
def hello_world():
    return (
        "If you are reading this in a browser, your service is "
        "operational. Switch to curl/Postman/etc to interact using the "
        "other HTTP verbs."
    )


@bp.route("/health")
@metrics.do_not_track()
def health():
    return Response("", status=200, mimetype="application/json")


@bp.route("/readiness")
@metrics.do_not_track()
def readiness():
    return Response("", status=200, mimetype="application/json")


@bp.route("/<customer_id>", methods=["GET"])
def get_customer(customer_id):
    print("customer_id in get customer:", customer_id)
    headers = request.headers
    payload = {"objtype": "customer", "objkey": "customer_id"}

    url = db["name"] + "/" + db["endpoint"][0]
    response = requests.get(url, params=payload, json={"table_key": customer_id})
    print("response: in customer", response)
    # return True
    return response.json()


@bp.route("/", methods=["PUT"])
def update_user():
    headers = request.headers
    # defining logger parameters
    service_name = "customer"
    operation_name = "update_customer"
    customer_id = "None"
    content = "None"
    # check header here
    try:
        content = request.get_json()
        lname = content["lname"]
        email = content["email"]
        fname = content["fname"]
        address1 = content["address1"]
        address2 = content["address2"]
        customer_id = content["customer_id"]
        password = content["password"]
    except Exception:
        status_code = "500"
        message = "error reading arguments"
        request_message = content

        response_message = json.dumps({"message": message, "status_code": status_code})
        # calling logger functino to log the error
        log_response = log_writer(
            customer_id,
            service_name,
            operation_name,
            status_code,
            message,
            request_message,
            response_message,
        )
        print("log response inside customer:", log_response)
        return response_message

    try:
        check_customer_id = get_customer(customer_id)
    except Exception:
        # retreiving admin context id falied
        # logging into logger table
        # declaring logger parameters
        status_code = "500"
        message = "error : reteiving admin credentials failed."
        request_message = content
        response_message = json.dumps({"message": message, "status_code": status_code})
        # calling logger functino to log the error
        log_response = log_writer(
            customer_id,
            service_name,
            operation_name,
            status_code,
            message,
            request_message,
            response_message,
        )
        return Response(response_message, status=500, mimetype="application/json")
    if check_customer_id["Count"] == 0:
        # declaring logger parameters
        status_code = "404"
        message = "Sorry! This customer does not exist. Please try again."
        response_message = json.dumps({"message": message, "status_code": status_code})
        # response_message = json.dumps({"message": "Sorry! This customer does not exist. Please try again.", "status_code":status_code})
        message = "Sorry! This customer does not exist. Please try again."
        request_message = content
        # calling the logger function to write into logger table
        log_response = log_writer(
            customer_id,
            service_name,
            operation_name,
            status_code,
            message,
            request_message,
            response_message,
        )
        return Response(response_message, status=404, mimetype="application/json")

    else:

        dict_customer = ast.literal_eval(str(check_customer_id["Items"])[1:-1])
        context_id = dict_customer["context_id"]
        if context_id == "":
            status_code = "400"
            message = "error : Please login to make changes to your profile."
            request_message = content
            response_message = json.dumps(
                {"message": message, "status_code": status_code}
            )
            # calling logger functino to log the error
            log_response = log_writer(
                customer_id,
                service_name,
                operation_name,
                status_code,
                message,
                request_message,
                response_message,
            )
            return Response(response_message, status=400, mimetype="application/json")
            # return Response(json.dumps({"Message": "Please login to make changes to your profile."}),
            # 		status=400,
            # 		mimetype='application/json')
        else:
            try:
                context_id = dict_customer["context_id"]
                url = db["name"] + "/" + db["endpoint"][3]
                response = requests.put(
                    url,
                    params={"objtype": "customer", "objkey": customer_id},
                    json={
                        "objtype": "customer",
                        "objkey": "customer_id",
                        "lname": lname,
                        "email": email,
                        "fname": fname,
                        "address1": address1,
                        "address2": address2,
                        "password": password,
                        "context_id": context_id,
                    },
                )
                # return (response.json())
            except Exception:
                # declaring logger parameters
                status_code = "500"
                message = "Updating the customer failed"
                request_message = content
                response_message = json.dumps(
                    {"message": message, "status_code": status_code}
                )
                # calling the logger function to write into logger table
                log_response = log_writer(
                    customer_id,
                    service_name,
                    operation_name,
                    status_code,
                    message,
                    request_message,
                    response_message,
                )
                return response_message
                # declaring logger parameters
            response_message = response.json()
            status_code = response_message["ResponseMetadata"]["HTTPStatusCode"]
            message = "customer has been updated."
            request_message = content
            # calling the logger function to write into logger table
            log_response = log_writer(
                customer_id,
                service_name,
                operation_name,
                status_code,
                message,
                request_message,
                response_message,
            )

            # checking if the writing into logger was successful
            if log_response.json()["status_code"] == 200:
                # returning the response of create product
                return response_message
            else:
                # error in wrtiting to the logger table
                print("Customer updated but writing into logger failed")
                return log_response

        # return Response(json.dumps({"Message": "Sorry! This customer does not exist. Please try again."}),
        # 			status=404,
        # 			mimetype='application/json')

    # if 'Authorization' not in headers:
    # 	return Response(json.dumps({"error": "missing auth"}), status=401,
    # 					mimetype='application/json')
    # try:
    # 	content = request.get_json()
    # 	email = content['email']
    # 	fname = content['fname']
    # 	lname = content['lname']
    # except Exception:
    # 	return json.dumps({"message": "error reading arguments"})
    # url = db['name'] + '/' + db['endpoint'][3]
    # response = requests.put(
    # 	url,
    # 	params={"objtype": "customer", "objkey": user_id},
    # 	json={"email": email, "fname": fname, "lname": lname})
    # return (response.json())


@bp.route("/", methods=["POST"])
def create_user():
    """
    Create a user.
    If a record already exists with the same fname, lname, and email,
    the old UUID is replaced with a new one.
    """
    # defining logger parameters
    service_name = "customer"
    operation_name = "create_customer"
    customer_id = "None"
    content = "None"
    try:
        content = request.get_json()
        lname = content["lname"]
        email = content["email"]
        fname = content["fname"]
        address1 = content["address1"]
        address2 = content["address2"]
        customer_id = content["customer_id"]
        password = content["password"]
    except Exception:
        status_code = "500"
        message = "error reading arguments"
        request_message = content
        response_message = json.dumps({"message": message, "status_code": status_code})
        # calling logger functino to log the error
        log_response = log_writer(
            customer_id,
            service_name,
            operation_name,
            status_code,
            message,
            request_message,
            response_message,
        )
        print("log response inside customer:", log_response)
        return response_message
    # 		return json.dumps({"message": "error reading arguments"})

    try:
        check_customer_id = get_customer(customer_id)
    except Exception:
        # retreiving admin context id falied
        # logging into logger table
        # declaring logger parameters
        status_code = "500"
        message = "error : reteiving admin credentials failed."
        request_message = content
        response_message = json.dumps({"message": message, "status_code": status_code})
        # calling logger functino to log the error
        log_response = log_writer(
            customer_id,
            service_name,
            operation_name,
            status_code,
            message,
            request_message,
            response_message,
        )
        return Response(response_message, status=500, mimetype="application/json")

    if check_customer_id["Count"] > 0:
        status_code = "400"
        message = "error : The requested customer id is already taken. Please use a different customer id"
        request_message = content
        response_message = json.dumps({"message": message, "status_code": status_code})
        # calling logger functino to log the error
        log_response = log_writer(
            customer_id,
            service_name,
            operation_name,
            status_code,
            message,
            request_message,
            response_message,
        )
        return Response(response_message, status=400, mimetype="application/json")
        # return Response(json.dumps({"Message": "The requested customer id is already taken. Please use a different customer id"}),
        # 				status=400,
        # 				mimetype='application/json')

    try:
        # setting db variables and endpoint
        url = db["name"] + "/" + db["endpoint"][1]

        # adding new customer to the  customer table
        response = requests.post(
            url,
            json={
                "objtype": "customer",
                "objkey": "customer_id",
                "lname": lname,
                "email": email,
                "fname": fname,
                "address1": address1,
                "address2": address2,
                "customer_id": customer_id,
                "password": password,
                "context_id": "",
            },
        )
        # return (response.json())
    except Exception:
        # declaring logger parameters
        status_code = "500"
        message = "Writing into the customer db failed"
        request_message = content
        response_message = json.dumps({"message": message, "status_code": status_code})
        # calling the logger function to write into logger table
        log_response = log_writer(
            customer_id,
            service_name,
            operation_name,
            status_code,
            message,
            request_message,
            response_message,
        )
        return response_message

    # declaring logger parameters
    response_message = response.json()
    status_code = response_message["status_code"]
    message = response_message["message"]
    request_message = content
    # calling the logger function to write into logger table
    log_response = log_writer(
        customer_id,
        service_name,
        operation_name,
        status_code,
        message,
        request_message,
        response_message,
    )

    # checking if the writing into logger was successful
    if log_response.json()["status_code"] == 200:
        # returning the response of create product
        return response_message
    else:
        # error in wrtiting to the logger table
        print("Customer created but writing into logger failed")
        return log_response


@bp.route("/", methods=["DELETE"])
def delete_user():
    headers = request.headers
    service_name = "customer"
    operation_name = "delete_customer"
    customer_id = "None"
    try:
        content = request.get_json()
        customer_id = content["customer_id"]

    except Exception:
        status_code = "500"
        message = "error reading arguments"
        request_message = content
        response_message = json.dumps({"message": message, "status_code": status_code})
        # calling logger functino to log the error
        log_response = log_writer(
            customer_id,
            service_name,
            operation_name,
            status_code,
            message,
            request_message,
            response_message,
        )
        return response_message
    try:
        check_customer_id = get_customer(customer_id)
    except Exception:
        # retreiving admin context id falied
        # logging into logger table
        # declaring logger parameters
        status_code = "500"
        message = "error : reteiving admin credentials failed."
        request_message = content
        response_message = json.dumps({"message": message, "status_code": status_code})
        # calling logger functino to log the error
        log_response = log_writer(
            customer_id,
            service_name,
            operation_name,
            status_code,
            message,
            request_message,
            response_message,
        )
        return Response(response_message, status=500, mimetype="application/json")

    if check_customer_id["Count"] > 0:
        dict_customer = ast.literal_eval(str(check_customer_id["Items"])[1:-1])
        context_id = dict_customer["context_id"]
        if context_id == "":
            status_code = "400"
            message = "error : Please login to make changes to your profile."
            request_message = content
            response_message = json.dumps(
                {"message": message, "status_code": status_code}
            )
            # calling logger functino to log the error
            log_response = log_writer(
                customer_id,
                service_name,
                operation_name,
                status_code,
                message,
                request_message,
                response_message,
            )
            return Response(response_message, status=400, mimetype="application/json")

            # return Response(json.dumps({"Message": "Please login to delete your profile."}),
            # 		status=400,
            # 		mimetype='application/json')
        else:
            try:
                url = db["name"] + "/" + db["endpoint"][2]

                response = requests.delete(
                    url, params={"objtype": "customer", "objkey": customer_id}
                )
            except Exception:
                # declaring logger parameters
                status_code = "500"
                message = "Deleting the customer failed"
                request_message = content
                response_message = json.dumps(
                    {"message": message, "status_code": status_code}
                )
                # calling the logger function to write into logger table
                log_response = log_writer(
                    customer_id,
                    service_name,
                    operation_name,
                    status_code,
                    message,
                    request_message,
                    response_message,
                )
                return response_message
            response_message = response.json()
            status_code = response_message["ResponseMetadata"]["HTTPStatusCode"]
            message = "Your profile is deleted successfully."
            request_message = content
            # calling the logger function to write into logger table
            log_response = log_writer(
                customer_id,
                service_name,
                operation_name,
                status_code,
                message,
                request_message,
                response_message,
            )

            # checking if the writing into logger was successful
            if log_response.json()["status_code"] == 200:
                # returning the response of create product
                return response_message
            else:
                # error in wrtiting to the logger table
                print("Customer deleted but writing into logger failed")
                return log_response

            # return Response(json.dumps({"Message": "Your profile is deleted successfully."}),
            # 		status=200,
            # 		mimetype='application/json')
    else:
        status_code = "404"
        message = "Sorry! This customer does not exist. Please try again."
        response_message = json.dumps({"message": message, "status_code": status_code})
        # response_message = json.dumps({"message": "Sorry! This customer does not exist. Please try again.", "status_code":status_code})
        message = "Sorry! This customer does not exist. Please try again."
        request_message = content
        # calling the logger function to write into logger table
        log_response = log_writer(
            customer_id,
            service_name,
            operation_name,
            status_code,
            message,
            request_message,
            response_message,
        )
        return Response(response_message, status=404, mimetype="application/json")
        # return Response(json.dumps({"Message": "Sorry! This customer does not exist. Please try again."}),
        # 			status=404,
        # 			mimetype='application/json')

    # check header here
    # if 'Authorization' not in headers:
    # 	return Response(json.dumps({"error": "missing auth"}),
    # 					status=401,
    # 					mimetype='application/json')


# @bp.route('/<user_id>', methods=['GET'])
# def get_user(user_id):
# 	headers = request.headers
# 	# check header here
# 	if 'Authorization' not in headers:
# 		return Response(
# 			json.dumps({"error": "missing auth"}),
# 			status=401,
# 			mimetype='application/json')
# 	payload = {"objtype": "customer", "objkey": user_id}
# 	url = db['name'] + '/' + db['endpoint'][0]
# 	response = requests.get(url, params=payload)
# 	return (response.json())


@bp.route("/login", methods=["PUT"])
def login():
    customer_id = "None"
    operation_name = "login customer"
    service_name = "customer"
    try:
        content = request.get_json()
        # uid = content['uid']
        customer_id = content["customer_id"]
        password = content["password"]
    except Exception:
        status_code = "500"
        message = "error reading arguments"
        request_message = content
        response_message = json.dumps({"message": message, "status_code": status_code})
        # calling logger functino to log the error
        log_response = log_writer(
            customer_id,
            service_name,
            operation_name,
            status_code,
            message,
            request_message,
            response_message,
        )
        return response_message
    try:
        check_customer_id = get_customer(customer_id)
    except Exception:
        # retreiving admin context id falied
        # logging into logger table
        # declaring logger parameters
        status_code = "500"
        message = "error : reteiving admin credentials failed."
        request_message = content
        response_message = json.dumps({"message": message, "status_code": status_code})
        # calling logger functino to log the error
        log_response = log_writer(
            customer_id,
            service_name,
            operation_name,
            status_code,
            message,
            request_message,
            response_message,
        )
        return Response(response_message, status=500, mimetype="application/json")
    if check_customer_id["Count"] == 0:
        # declaring logger parameters
        status_code = "404"
        message = "Sorry! This customer does not exist. Please try again."
        response_message = json.dumps({"message": message, "status_code": status_code})
        # response_message = json.dumps({"message": "Sorry! This customer does not exist. Please try again.", "status_code":status_code})
        message = "Sorry! This customer does not exist. Please try again."
        request_message = content
        # calling the logger function to write into logger table
        log_response = log_writer(
            customer_id,
            service_name,
            operation_name,
            status_code,
            message,
            request_message,
            response_message,
        )
        return Response(response_message, status=404, mimetype="application/json")

    else:
        dict_customer = ast.literal_eval(str(check_customer_id["Items"])[1:-1])
        password_db = dict_customer["password"]
        if password != password_db:
            status_code = "400"
            message = "error : Your credentials do not match. Please try again"
            request_message = content
            response_message = json.dumps(
                {"message": message, "status_code": status_code}
            )
            # calling logger functino to log the error
            log_response = log_writer(
                customer_id,
                service_name,
                operation_name,
                status_code,
                message,
                request_message,
                response_message,
            )
            return Response(response_message, status=400, mimetype="application/json")
            # return Response(json.dumps({"Message": "Please login to make changes to your profile."}),
            # 		status=400,
            # 		mimetype='application/json')
        else:
            lname = dict_customer["lname"]
            fname = dict_customer["fname"]
            email = dict_customer["email"]
            address1 = dict_customer["address1"]
            address2 = dict_customer["address2"]
            encoded = jwt.encode(
                {"customer_id": customer_id, "time": time.time()},
                "secret",
                algorithm="HS256",
            )
            context_id = encoded
            try:
                url = db["name"] + "/" + db["endpoint"][3]
                response = requests.put(
                    url,
                    params={"objtype": "customer", "objkey": customer_id},
                    json={
                        "objtype": "customer",
                        "objkey": "customer_id",
                        "lname": lname,
                        "email": email,
                        "fname": fname,
                        "address1": address1,
                        "address2": address2,
                        "password": password,
                        "context_id": context_id,
                    },
                )
                status_code = 200
                message = "You have logged in successfully to CyberShop."
                request_message = content
                response_message = json.dumps(
                    {"message": message, "status_code": status_code}
                )
                log_response = log_writer(
                    customer_id,
                    service_name,
                    operation_name,
                    status_code,
                    message,
                    request_message,
                    response_message,
                )
                return Response(
                    json.dumps({"context_id": context_id}),
                    status=200,
                    mimetype="application/json",
                )
            except Exception:
                status_code = "503"
                message = "error: could not log out. call to db failed."
                request_message = content
                response_message = json.dumps(
                    {"message": message, "status_code": status_code}
                )
                # calling logger functino to log the error
                log_response = log_writer(
                    customer_id,
                    service_name,
                    operation_name,
                    status_code,
                    message,
                    request_message,
                    response_message,
                )
                return response_message
            # response_message = response.json()
            # #status_code = response_message["ResponseMetadata"]["HTTPStatusCode"]

            # #calling the logger function to write into logger table
            # log_response = log_writer(customer_id, service_name, operation_name, status_code, message, request_message, response_message)

            # #checking if the writing into logger was successful
            # if log_response.json()['status_code'] == 200:
            # 	#returning the response of create product
            # 	return (response_message)
            # else:
            # 		#error in wrtiting to the logger table
            # 	return log_response


@bp.route("/logoff", methods=["PUT"])
def logoff():
    customer_id = "None"
    operation_name = "logout customer"
    service_name = "customer"
    try:
        content = request.get_json()
        # uid = content['uid']
        customer_id = content["customer_id"]
        context_id = content["context_id"]
    except Exception:
        status_code = "500"
        message = "error reading arguments"
        request_message = content
        response_message = json.dumps({"message": message, "status_code": status_code})
        # calling logger functino to log the error
        log_response = log_writer(
            customer_id,
            service_name,
            operation_name,
            status_code,
            message,
            request_message,
            response_message,
        )
        return response_message
    try:
        check_customer_id = get_customer(customer_id)
    except Exception:
        # retreiving admin context id falied
        # logging into logger table
        # declaring logger parameters
        status_code = "500"
        message = "error : reteiving admin credentials failed."
        request_message = content
        response_message = json.dumps({"message": message, "status_code": status_code})
        # calling logger functino to log the error
        log_response = log_writer(
            customer_id,
            service_name,
            operation_name,
            status_code,
            message,
            request_message,
            response_message,
        )
        return Response(response_message, status=500, mimetype="application/json")
    if check_customer_id["Count"] == 0:
        # declaring logger parameters
        status_code = "404"
        message = "Sorry! This customer does not exist. Please try again."
        response_message = json.dumps({"message": message, "status_code": status_code})
        # response_message = json.dumps({"message": "Sorry! This customer does not exist. Please try again.", "status_code":status_code})
        message = "Sorry! This customer does not exist. Please try again."
        request_message = content
        # calling the logger function to write into logger table
        log_response = log_writer(
            customer_id,
            service_name,
            operation_name,
            status_code,
            message,
            request_message,
            response_message,
        )
        return Response(response_message, status=404, mimetype="application/json")

    else:
        dict_customer = ast.literal_eval(str(check_customer_id["Items"])[1:-1])
        context_id_db = dict_customer["context_id"]
        if context_id != context_id_db:
            status_code = "400"
            message = "error : Your credentials do not match. Please try again"
            request_message = content
            response_message = json.dumps(
                {"message": message, "status_code": status_code}
            )
            # calling logger functino to log the error
            log_response = log_writer(
                customer_id,
                service_name,
                operation_name,
                status_code,
                message,
                request_message,
                response_message,
            )
            return Response(response_message, status=400, mimetype="application/json")
            # return Response(json.dumps({"Message": "Please login to make changes to your profile."}),
            # 		status=400,
            # 		mimetype='application/json')
        else:
            lname = dict_customer["lname"]
            fname = dict_customer["fname"]
            email = dict_customer["email"]
            address1 = dict_customer["address1"]
            address2 = dict_customer["address2"]
            password = dict_customer["password"]
            try:
                url = db["name"] + "/" + db["endpoint"][3]
                response = requests.put(
                    url,
                    params={"objtype": "customer", "objkey": customer_id},
                    json={
                        "objtype": "customer",
                        "objkey": "customer_id",
                        "lname": lname,
                        "email": email,
                        "fname": fname,
                        "address1": address1,
                        "address2": address2,
                        "password": password,
                        "context_id": "",
                    },
                )
            except Exception:
                status_code = "503"
                message = "error: could not log out. call to db failed."
                request_message = content
                response_message = json.dumps(
                    {"message": message, "status_code": status_code}
                )
                # calling logger functino to log the error
                log_response = log_writer(
                    customer_id,
                    service_name,
                    operation_name,
                    status_code,
                    message,
                    request_message,
                    response_message,
                )
                return response_message

            response_message = response.json()
            status_code = response_message["ResponseMetadata"]["HTTPStatusCode"]
            message = "You have logged out successfully."
            request_message = content
            # calling the logger function to write into logger table
            log_response = log_writer(
                customer_id,
                service_name,
                operation_name,
                status_code,
                message,
                request_message,
                response_message,
            )

            # checking if the writing into logger was successful
            if log_response.json()["status_code"] == 200:
                # returning the response of create product
                return response_message
            else:
                # error in wrtiting to the logger table
                print("Customer deleted but writing into logger failed")
                return log_response


# All database calls will have this prefix.  Prometheus metric
# calls will not---they will have route '/metrics'.  This is
# the conventional organization.
app.register_blueprint(bp, url_prefix="/api/v1/customer/")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logging.error("Usage: app.py <service-port>")
        sys.exit(-1)

    p = int(sys.argv[1])
    # Do not set debug=True---that will disable the Prometheus metrics
    app.run(host="0.0.0.0", port=p, threaded=True)
