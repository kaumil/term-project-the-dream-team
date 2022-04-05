#
# Front-end to bring some sanity to the litany of tools and switches
# in calling the sample application from the command line.
#
# This file covers off driving the API independent of where the cluster is
# running.
# Be sure to set your context appropriately for the log monitor.
#
# The intended approach to working with this makefile is to update select
# elements (body, id, IP, port, etc) as you progress through your workflow.
# Where possible, stodout outputs are tee into .out files for later review.
#


KC=kubectl
CURL=curl

# Keep all the logs out of main directory
LOG_DIR=logs

# look these up with 'make ls'
# You need to specify the container because istio injects side-car container
# into each pod.
# db: cmpt756marketplacedb
PODLOGGER=pod/users-8557865b4b-jnwrj
PODCONT=service1

# show deploy and pods in current ns; svc of marketplace ns
ls: showcontext
	$(KC) get gw,deployments,pods
	$(KC) -n $(NS) get svc

logs:
	$(KC) logs $(PODLOGGER) -c $(PODCONT)

#
# Replace this with the external IP/DNS name of your cluster
#
# In all cases, look up the external IP of the istio-ingressgateway LoadBalancer service
# You can use either 'make -f eks.m extern' or 'make -f mk.m extern' or
# directly 'kubectl -n istio-system get service istio-ingressgateway'
#
#IGW=172.16.199.128:31413
#IGW=10.96.57.211:80
#IGW=a98fea4076a3a4627bf939196800825d-1772569567.us-west-2.elb.amazonaws.com:80
IGW=a9bf63013eb22487d965129a70a71757-831336802.us-west-2.elb.amazonaws.com:80


## Body for USER operations

USER_ID=e0038fea-f9ed-4c65-aa0e-fc189206faee

# Add User
ADD_USER = {\
"users_id": "$(USER_ID)", \
"username": "foo", \
"password": "bar", \
"users_role": "buyer", \
"disabled": "False" \
}

# Update User


UPDATE_USER = {\
"username": "foo", \
"password": "bar", \
"users_role": "buyer", \
"disabled": "True" \
}

#Body UID for login
BODY_UID= { \
"users_id": "e0038fea-f9ed-4c65-aa0e-fc189206faee", \
"password": "flash" \
}

BODY_TOKEN={ \
	"jwt": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiZTAwMzhmZWEtZjllZC00YzY1LWFhMGUtZmMxODkyMDZmYWVlIiwidGltZSI6MTY0ODMzNzM5Ny41MDg3NTE2fQ.tCDLNp5KzSnOC7561Fdo4958Mg6g-4ugkVn4vFBoAOc" \
}

# USER
# Create
cuser: # done
	echo curl --location --request POST 'http://$(IGW)/api/v1/users/create_user/' --header 'Content-Type: application/json' --data-raw '$(ADD_USER)' > $(LOG_DIR)/cuser.out
	$(CURL) --location --request POST 'http://$(IGW)/api/v1/users/create_user/' --header 'Content-Type: application/json' --data-raw '$(ADD_USER)' | tee -a $(LOG_DIR)/cuser.out

# Get
ruser: # done
	echo curl --location --request GET 'http://$(IGW)/api/v1/users/get_user/$(USER_ID)' --header 'Content-Type: application/json' > $(LOG_DIR)/ruser.out
	$(CURL) --location --request GET 'http://$(IGW)/api/v1/users/get_user/$(USER_ID)' --header 'Content-Type: application/json' | tee -a $(LOG_DIR)/ruser.out

# Update
uuser: # done
	echo curl --location --request PUT 'http://$(IGW)/api/v1/users/update_user/$(USER_ID)' --header 'Content-Type: application/json' --data-raw '$(UPDATE_USER)' > $(LOG_DIR)/uuser.out
	$(CURL) --location --request PUT 'http://$(IGW)/api/v1/users/update_user/$(USER_ID)' --header 'Content-Type: application/json' --data-raw '$(UPDATE_USER)' | tee -a $(LOG_DIR)/uuser.out

# Delete
duser: # done	
	echo curl --location --request DELETE 'http://$(IGW)/api/v1/users/delete_user/$(USER_ID)' --header 'Content-Type: application/json' > $(LOG_DIR)/duser.out
	$(CURL) --location --request DELETE 'http://$(IGW)/api/v1/users/delete_user/$(USER_ID)' --header 'Content-Type: application/json' | tee -a $(LOG_DIR)/duser.out

# LOGIN/ LOGOUT
apilogin: # done
	echo curl --location --request PUT 'http://$(IGW)/api/v1/users/login' --header 'Content-Type: application/json' --data-raw '$(BODY_UID)' > $(LOG_DIR)/apilogin.out
	$(CURL) --location --request PUT 'http://$(IGW)/api/v1/users/login' --header 'Content-Type: application/json' --data-raw '$(BODY_UID)' | tee -a $(LOG_DIR)/apilogin.out

apilogoff: # done
	echo curl --location --request PUT 'http://$(IGW)/api/v1/users/logoff' --header 'Content-Type: application/json' --data-raw '$(BODY_TOKEN)' > $(LOG_DIR)/apilogoff.out
	$(CURL) --location --request PUT 'http://$(IGW)/api/v1/users/logoff' --header 'Content-Type: application/json' --data-raw '$(BODY_TOKEN)' | tee -a $(LOG_DIR)/apilogoff.out










## Body for IMAGE operations
# Add Image

IMAGE_ID=c97dee22-7270-4fb2-ad25-8386b05d8dc2
ADD_IMAGE = {\
"images_id": "$(IMAGE_ID)", \
"users_id": "567dce7f-b7b4-4efd-b75e-2b98592abe6d" \
}

# Update Image
UPDATE_IMAGE = {\
"users_id": "3ac9644e-24eb-4436-b290-83ac8ea41fea", \
"s3_url": "http://us-west-2.s3.amazonaws.com/51b616bd-cc17-4075-b539-d8a013b6522a" \
}

# Read Image
# READ_IMAGE = {\
# "image_id": "51b616bd-cc17-4075-b539-d8a013b6522a" \
# }


# Delete Image
# DELETE_IMAGE = {\
# "image_id": "51b616bd-cc17-4075-b539-d8a013b6522a" \
# }

# IMAGE
# Create
cimage: # done
	echo curl --location --request POST 'http://$(IGW)/api/v1/images/create_image/' --header 'Content-Type: application/json' --data-raw '$(ADD_IMAGE)' > $(LOG_DIR)/cimage.out
	$(CURL) --location --request POST 'http://$(IGW)/api/v1/images/create_image/' --header 'Content-Type: application/json' --data-raw '$(ADD_IMAGE)' | tee -a $(LOG_DIR)/cimage.out

#Read
rimage: # done
	echo curl --location --request GET 'http://$(IGW)/api/v1/images/read_image/$(IMAGE_ID)' --header 'Content-Type: application/json' > $(LOG_DIR)/rimage.out
	$(CURL) --location --request GET 'http://$(IGW)/api/v1/images/read_image/$(IMAGE_ID)' --header 'Content-Type: application/json' | tee -a $(LOG_DIR)/rimage.out

#Update
uimage: # done
	echo curl --location --request PUT 'http://$(IGW)/api/v1/images/change_owner/$(IMAGE_ID)' --header 'Content-Type: application/json' --data-raw '$(UPDATE_IMAGE)' > $(LOG_DIR)/uimage.out
	$(CURL) --location --request PUT 'http://$(IGW)/api/v1/images/change_owner/$(IMAGE_ID)' --header 'Content-Type: application/json' --data-raw '$(UPDATE_IMAGE)' | tee -a $(LOG_DIR)/uimage.out

#Delete
dimage: # done
	echo curl --location --request DELETE 'http://$(IGW)/api/v1/images/delete_image/$(IMAGE_ID)' --header 'Content-Type: application/json' > $(LOG_DIR)/dimage.out
	$(CURL) --location --request DELETE 'http://$(IGW)/api/v1/images/delete_image/$(IMAGE_ID)' --header 'Content-Type: application/json' | tee -a $(LOG_DIR)/dimage.out





## Body for LOGGER operations
# Add Logs
ADD_LOGGER= {\
"user_id": "567dce7f-b7b4-4efd-b75e-2b98592abe6d",\
"service_name": "image",\
"operation_name": "add",\
"status_code": 200, \
"message": "adding image" \
}

#Get Logs
GET_LOGGER=567dce7f-b7b4-4efd-b75e-2b98592abe6d

# LOGGER
# Create
clogger: # inprogress
	echo curl --location --request POST 'http://$(IGW)/api/v1/logger/create_log/' --header 'Content-Type: application/json' --data-raw '$(ADD_LOGGER)' > $(LOG_DIR)/clogger.out
	$(CURL) --location --request POST 'http://$(IGW)/api/v1/logger/create_log/' --header 'Content-Type: application/json' --data-raw '$(ADD_LOGGER)' | tee -a $(LOG_DIR)/clogger.out

# Read
rlogger: # inprogress
	echo curl --location --request GET 'http://$(IGW)/api/v1/logger/read_log/$(GET_LOGGER)' --header 'Content-Type: application/json' > $(LOG_DIR)/rlogger.out
	$(CURL) --location --request GET 'http://$(IGW)/api/v1/logger/read_log/$(GET_LOGGER)' --header 'Content-Type: application/json' | tee -a $(LOG_DIR)/rlogger.out

showcontext:
	$(KC) config get-contexts





## Body for TRANSACTION operations
# Create Transaction
TRANSACTION_ID=0b08fc9f-ea46-4b90-b8ae-35fe856da0d8
CREATE_TRANSACTION = {\
	"transactions_id": "$(TRANSACTION_ID)", \
	"seller_id": "567dce7f-b7b4-4efd-b75e-2b98592abe6d", \
	"images_id": "51b616bd-cc17-4075-b539-d8a013b6522a" \
}

UPDATE_TRANSACTION = {\
	"buyer_id": "3ac9644e-24eb-4436-b290-83ac8ea41fea", \
	"sold": "True" \
}

# Read Transaction
# READ_TRANSACTION = {\
# 	"transaction_id": "3ac9644e-24eb-4436-b290-83ac8ea41fea" \
# }

# Delete Transaction
DELETE_TRANSACTION = {\
	"transactions_id": "3ac9644e-24eb-4436-b290-83ac8ea41fea" \
}



# Authorization token and Body token
TOKEN=Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiMDI3Yzk5ZWYtM2UxMi00ZmM5LWFhYzgtMTcyZjg3N2MyZDI0IiwidGltZSI6MTYwMTA3NDY0NC44MTIxNjg2fQ.hR5Gbw5t2VMpLcj8yDz1B6tcWsWCFNiHB_KHpvQVNls \
BODY_TOKEN={ \
"user_id": "567dce7f-b7b4-4efd-b75e-2b98592abe6d" \
}



# TRANSACTION
# Create
ctransaction: # done
	echo curl --location --request POST 'http://$(IGW)/api/v1/transaction/create_transaction/' --header 'Content-Type: application/json' --data-raw '$(CREATE_TRANSACTION)' > $(LOG_DIR)/ctransaction.out
	$(CURL) --location --request POST 'http://$(IGW)/api/v1/transaction/create_transaction/' --header 'Content-Type: application/json' --data-raw '$(CREATE_TRANSACTION)' | tee -a $(LOG_DIR)/ctransaction.out

# Read
rtransaction: # done
	echo curl --location --request GET 'http://$(IGW)/api/v1/transaction/read_transaction/$(TRANSACTION_ID)' --header 'Content-Type: application/json' > $(LOG_DIR)/rtransaction.out
	$(CURL) --location --request GET 'http://$(IGW)/api/v1/transaction/read_transaction/$(TRANSACTION_ID)' --header 'Content-Type: application/json' | tee -a $(LOG_DIR)/rtransaction.out


# Update
utransaction:
	echo curl --location --request PUT 'http://$(IGW)/api/v1/transaction/change_transaction/$(TRANSACTION_ID)' --header 'Content-Type: application/json' --data-raw '$(UPDATE_TRANSACTION)' > $(LOG_DIR)/utransaction.out
	$(CURL) --location --request PUT 'http://$(IGW)/api/v1/transaction/change_transaction/$(TRANSACTION_ID)' --header 'Content-Type: application/json' --data-raw '$(UPDATE_TRANSACTION)' | tee -a $(LOG_DIR)/utransaction.out

# Delete
dtransaction:
	echo curl --location --request DELETE 'http://$(IGW)/api/v1/transaction/delete_transaction/$(TRANSACTION_ID)' --header 'Content-Type: application/json' > $(LOG_DIR)/dtransaction.out
	$(CURL) --location --request DELETE 'http://$(IGW)/api/v1/transaction/delete_transaction/$(TRANSACTION_ID)' --header 'Content-Type: application/json' | tee -a $(LOG_DIR)/dtransaction.out

