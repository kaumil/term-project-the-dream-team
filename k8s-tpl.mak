#
# Front-end to bring some sanity to the litany of tools and switches
# for working with a k8s cluster. Note that this file exercise core k8s
# commands that's independent of the cluster vendor.
#
# All vendor-specific commands are in the make file for that vendor:
# az.mak, eks.mak, gcp.mak, mk.mak
#
# This file addresses APPPLing the Deployment, Service, Gateway, and VirtualService
#
# Be sure to set your context appropriately for the log monitor.
#
# The intended approach to working with this makefile is to update select
# elements (body, id, IP, port, etc) as you progress through your workflow.
# Where possible, stodout outputs are tee into .out files for later review.

# These will be filled in by template processor
CREG=ZZ-CR-ID
REGID=ZZ-REG-ID
AWS_REGION=ZZ-AWS-REGION
JAVA_HOME=ZZ-JAVA-HOME
GAT_DIR=ZZ-GAT-DIR

# Keep all the logs out of main directory
LOG_DIR=logs

# These should be in your search path
KC=kubectl
DK=docker
AWS=aws
IC=istioctl

# Application versions
# Override these by environment variables and `make -e`
APP_VER_TAG=v1
LOADER_VER=v1

# Gatling parameters to be overridden by environment variables and `make -e`
SIM_NAME=ReadUserSim
USERS=1

# Gatling parameters that most of the time will be unchanged
# but which you might override as projects become sophisticated
SIM_FILE=ReadTables.scala
SIM_PACKAGE=proj756
GATLING_OPTIONS=

# Other Gatling parameters---you should not have to change these
GAT=$(GAT_DIR)/bin/gatling.sh
SIM_DIR=gatling/simulations
RES_DIR=gatling/resources
SIM_PACKAGE_DIR=$(SIM_DIR)/$(SIM_PACKAGE)
SIM_FULL_NAME=$(SIM_PACKAGE).$(SIM_NAME)

# Kubernetes parameters that most of the time will be unchanged
# but which you might override as projects become sophisticated
APP_NS=c756marketplacens
ISTIO_NS=istio-system

# this is used to switch M1 Mac to x86 for compatibility with x86 instances/students
ARCH=--platform x86_64


# ----------------------------------------------------------------------------------------
# -------  Targets to be invoked directly from command line                        -------
# ----------------------------------------------------------------------------------------

# ---  templates:  Instantiate all template files
#
# This is the only entry that *must* be run from k8s-tpl.mak
# (because it creates k8s.mak)
templates:
	tools/process-templates.sh

# --- provision: Provision the entire stack
# This typically is all you need to do to install the sample application and
# all its dependencies
#
# Preconditions:
# 1. Templates have been instantiated (make -f k8s-tpl.mak templates)
# 2. Current context is a running Kubernetes cluster (make -f {az,eks,gcp,mk}.mak start)
#
#  Nov 2021: Kiali is causing problems so do not deploy
#provision: istio prom kiali deploy
provision: istio prom kiali deploy

# --- deploy: Deploy and monitor the three microservices
# Use `provision` to deploy the entire stack (including Istio, Prometheus, ...).
# This target only deploys the sample microservices
deploy: appns gw logger users images transaction db monitoring
	$(KC) -n $(APP_NS) get gw,vs,deploy,svc,pods

# --- rollout: Rollout new deployments of all microservices
rollout: rollout-users rollout-images rollout-transaction rollout-db rollout-logger

# rollout-users: users
# 	$(KC) rollout -n $(APP_NS) restart deployment/users

# rollout-images: images
# 	$(KC) rollout -n $(APP_NS) restart deployment/images

# rollout-transaction: transaction
# 	$(KC) rollout -n $(APP_NS) restart deployment/transaction

# rollout-logger: logger
# 	$(KC) rollout -n $(APP_NS) restart deployment/logger
rollout-users: $(LOG_DIR)/users.repo.log  cluster/users-dpl.yaml
	$(KC) -n $(APP_NS) apply -f cluster/users-dpl.yaml | tee $(LOG_DIR)/rollout-users.log
	$(KC) rollout -n $(APP_NS) restart deployment/users | tee -a $(LOG_DIR)/rollout-users.log

rollout-images: $(LOG_DIR)/images.repo.log  cluster/images-dpl.yaml
	$(KC) -n $(APP_NS) apply -f cluster/images-dpl.yaml | tee $(LOG_DIR)/rollout-images.log
	$(KC) rollout -n $(APP_NS) restart deployment/images | tee -a $(LOG_DIR)/rollout-images.log

rollout-transaction: $(LOG_DIR)/transaction.repo.log  cluster/transaction-dpl.yaml
	$(KC) -n $(APP_NS) apply -f cluster/transaction-dpl.yaml | tee $(LOG_DIR)/rollout-transaction.log
	$(KC) rollout -n $(APP_NS) restart deployment/transaction | tee -a $(LOG_DIR)/rollout-transaction.log

rollout-logger: $(LOG_DIR)/logger.repo.log  cluster/logger-dpl.yaml
	$(KC) -n $(APP_NS) apply -f cluster/logger-dpl.yaml | tee $(LOG_DIR)/rollout-logger.log
	$(KC) rollout -n $(APP_NS) restart deployment/logger | tee -a $(LOG_DIR)/rollout-logger.log

rollout-db: db
	$(KC) rollout -n $(APP_NS) restart deployment/cmpt756marketplacedb


# --- rollout-s2: Rollout a new deployment of S2
# rollout-s2: $(LOG_DIR)/s2-$(S2_VER).repo.log  cluster/s2-dpl-$(S2_VER).yaml
# 	$(KC) -n $(APP_NS) apply -f cluster/s2-dpl-$(S2_VER).yaml | tee $(LOG_DIR)/rollout-s2.log
# 	$(KC) rollout -n $(APP_NS) restart deployment/cmpt756s2-$(S2_VER) | tee -a $(LOG_DIR)/rollout-s2.log

# --- rollout-db: Rollout a new deployment of DB
# rollout-db: db
# 	$(KC) rollout -n $(APP_NS) restart deployment/cmpt756marketplacedb


health-off:
	$(KC) -n $(APP_NS) apply -f cluster/users-nohealth.yaml
	$(KC) -n $(APP_NS) apply -f cluster/images-nohealth.yaml
	$(KC) -n $(APP_NS) apply -f cluster/transaction-nohealth.yaml
	$(KC) -n $(APP_NS) apply -f cluster/logger-nohealth.yaml
	$(KC) -n $(APP_NS) apply -f cluster/db-nohealth.yaml

# --- scratch: Delete the microservices and everything else in application NS
scratch: clean
	$(KC) delete -n $(APP_NS) deploy --all
	$(KC) delete -n $(APP_NS) svc    --all
	$(KC) delete -n $(APP_NS) gw     --all
	$(KC) delete -n $(APP_NS) dr     --all
	$(KC) delete -n $(APP_NS) vs     --all
	$(KC) delete -n $(APP_NS) se     --all
	$(KC) delete -n $(ISTIO_NS) vs monitoring --ignore-not-found=true
	$(KC) get -n $(APP_NS) deploy,svc,pods,gw,dr,vs,se
	$(KC) get -n $(ISTIO_NS) vs

# --- clean: Delete all the application log files
clean:
	/bin/rm -f $(LOG_DIR)/{logger,users,images,transaction,db,gw,monvs}*.log $(LOG_DIR)/rollout*.log

# --- dashboard: Start the standard Kubernetes dashboard
# NOTE:  Before invoking this, the dashboard must be installed and a service account created
dashboard: showcontext
	echo Please follow instructions at https://docs.aws.amazon.com/eks/latest/userguide/dashboard-tutorial.html
	echo Remember to 'pkill kubectl' when you are done!
	$(KC) proxy &
	open http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/#!/login

# --- extern: Display status of Istio ingress gateway
# Especially useful for Minikube, if you can't remember whether you invoked its `lb`
# target or directly ran `minikube tunnel`
extern: showcontext
	$(KC) -n $(ISTIO_NS) get svc istio-ingressgateway

# --- log-X: show the log of a particular service
log-users:
	$(KC) -n $(APP_NS) logs deployment/users --container users

log-images:
	$(KC) -n $(APP_NS) logs deployment/images --container images

log-transaction:
	$(KC) -n $(APP_NS) logs deployment/transaction --container transaction

log-logger:
	$(KC) -n $(APP_NS) logs deployment/logger --container logger

log-db:
	$(KC) -n $(APP_NS) logs deployment/cmpt756marketplacedb --container cmpt756marketplacedb


# --- shell-X: hint for shell into a particular service
shell-users:
	@echo Use the following command line to drop into the users service:
	@echo   $(KC) -n $(APP_NS) exec -it deployment/users --container users -- bash

shell-images:
	@echo Use the following command line to drop into the images service:
	@echo   $(KC) -n $(APP_NS) exec -it deployment/images --container images -- bash

shell-transaction:
	@echo Use the following command line to drop into the transaction service:
	@echo   $(KC) -n $(APP_NS) exec -it deployment/transaction --container transaction -- bash

shell-logger:
	@echo Use the following command line to drop into the logger service:
	@echo   $(KC) -n $(APP_NS) exec -it deployment/logger --container logger -- bash

shell-db:
	@echo Use the following command line to drop into the db service:
	@echo   $(KC) -n $(APP_NS) exec -it deployment/cmpt756marketplacedb --container cmpt756marketplacedb -- bash



# --- lsa: List services in all namespaces
lsa: showcontext
	$(KC) get svc --all-namespaces

# --- ls: Show deploy, pods, vs, and svc of application ns
ls: showcontext
	$(KC) get -n $(APP_NS) gw,vs,svc,deployments,pods

# --- lsd: Show containers in pods for all namespaces
lsd:
	$(KC) get pods --all-namespaces -o=jsonpath='{range .items[*]}{"\n"}{.metadata.name}{":\t"}{range .spec.containers[*]}{.image}{", "}{end}{end}' | sort

# --- reinstate: Reinstate provisioning on a new set of worker nodes
# Do this after you do `up` on a cluster that implements that operation.
# AWS implements `up` and `down`; other cloud vendors may not.
reinstate: istio
	$(KC) create ns $(APP_NS) | tee $(LOG_DIR)/reinstate.log
	$(KC) label ns $(APP_NS) istio-injection=enabled | tee -a $(LOG_DIR)/reinstate.log

# --- showcontext: Display current context
showcontext:
	$(KC) config get-contexts

# --- dynamodb-init: set up our DynamoDB tables
#
dynamodb-init: $(LOG_DIR)/dynamodb-init.log

# Start DynamoDB at the default read and write rates
$(LOG_DIR)/dynamodb-init.log: cluster/cloudformationdynamodb.json
	@# "|| true" suffix because command fails when stack already exists
	@# (even with --on-failure DO_NOTHING, a nonzero error code is returned)
	$(AWS) cloudformation create-stack --stack-name db --template-body file://$< || true | tee $(LOG_DIR)/dynamodb-init.log
	# Must give DynamoDB time to create the tables before running the loader
	sleep 20

# --- dynamodb-stop: Stop the AWS DynamoDB service
#
dynamodb-clean:
	$(AWS) cloudformation delete-stack --stack-name db || true | tee $(LOG_DIR)/dynamodb-clean.log
	@# Rename DynamoDB log so dynamodb-init will force a restart but retain the log
	/bin/mv -f $(LOG_DIR)/dynamodb-init.log $(LOG_DIR)/dynamodb-init-old.log || true

# --- ls-tables: List the tables and their read/write units for all DynamodDB tables
ls-tables:
	@tools/list-dynamodb-tables.sh $(AWS) $(AWS_REGION)

# --- registry-login: Login to the container registry
#
registry-login:
	@/bin/sh -c 'cat cluster/${CREG}-token.txt | $(DK) login $(CREG) -u $(REGID) --password-stdin'

# --- Variables defined for URL targets
# Utility to get the hostname (AWS) or ip (everyone else) of a load-balanced service
# Must be followed by a service
IP_GET_CMD=tools/getip.sh $(KC) $(ISTIO_NS)

# This expression is reused several times
# Use back-tick for subshell so as not to confuse with make $() variable notation
INGRESS_IP=`$(IP_GET_CMD) svc/istio-ingressgateway`

# --- kiali-url: Print the URL to browse Kiali in current cluster
kiali-url:
	@/bin/sh -c 'echo http://$(INGRESS_IP)/kiali'

# --- grafana-url: Print the URL to browse Grafana in current cluster
grafana-url:
	@# Use back-tick for subshell so as not to confuse with make $() variable notation
	@/bin/sh -c 'echo http://`$(IP_GET_CMD) svc/grafana-ingress`:3000/'

# --- prometheus-url: Print the URL to browse Prometheus in current cluster
prometheus-url:
	@# Use back-tick for subshell so as not to confuse with make $() variable notation
	@/bin/sh -c 'echo http://`$(IP_GET_CMD) svc/prom-ingress`:9090/'


# ----------------------------------------------------------------------------------------
# ------- Targets called by above. Not normally invoked directly from command line -------
# ------- Note that some subtargets are in `obs.mak`                               -------
# ----------------------------------------------------------------------------------------

# Install Prometheus stack by calling `obs.mak` recursively
prom:
	make -f obs.mak init-helm --no-print-directory
	make -f obs.mak install-prom --no-print-directory

# Install Kiali operator and Kiali by calling `obs.mak` recursively
# Waits for Kiali to be created and begin running. This wait is required
# before installing the three microservices because they
# depend upon some Custom Resource Definitions (CRDs) added
# by Kiali
kiali:
	make -f obs.mak install-kiali
	# Kiali operator can take awhile to start Kiali
	tools/waiteq.sh 'app=kiali' '{.items[*]}'              ''        'Kiali' 'Created'
	tools/waitne.sh 'app=kiali' '{.items[0].status.phase}' 'Running' 'Kiali' 'Running'

# Install Istio
istio:
	$(IC) install -y --set profile=demo --set hub=gcr.io/istio-release | tee -a $(LOG_DIR)/mk-reinstate.log

# Create and configure the application namespace
appns:
	# Appended "|| true" so that make continues even when command fails
	# because namespace already exists
	$(KC) create ns $(APP_NS) || true
	$(KC) label namespace $(APP_NS) --overwrite=true istio-injection=enabled

# Update monitoring virtual service and display result
monitoring: monvs
	$(KC) -n $(ISTIO_NS) get vs

# Update monitoring virtual service
monvs: cluster/monitoring-virtualservice.yaml
	$(KC) -n $(ISTIO_NS) apply -f $< > $(LOG_DIR)/monvs.log

# Update service gateway
gw: cluster/service-gateway.yaml
	$(KC) -n $(APP_NS) apply -f $< > $(LOG_DIR)/gw.log



logger: rollout-logger cluster/logger-svc.yaml cluster/logger-sm.yaml cluster/logger-vs.yaml
	$(KC) -n $(APP_NS) apply -f cluster/logger-svc.yaml | tee $(LOG_DIR)/logger.log
	$(KC) -n $(APP_NS) apply -f cluster/logger-sm.yaml | tee -a $(LOG_DIR)/logger.log
	$(KC) -n $(APP_NS) apply -f cluster/logger-vs.yaml | tee -a $(LOG_DIR)/logger.log

users: rollout-users cluster/users-svc.yaml cluster/users-sm.yaml cluster/users-vs.yaml
	$(KC) -n $(APP_NS) apply -f cluster/users-svc.yaml | tee $(LOG_DIR)/users.log
	$(KC) -n $(APP_NS) apply -f cluster/users-sm.yaml | tee -a $(LOG_DIR)/users.log
	$(KC) -n $(APP_NS) apply -f cluster/users-vs.yaml | tee -a $(LOG_DIR)/users.log

images: rollout-images cluster/images-svc.yaml cluster/images-sm.yaml cluster/images-vs.yaml
	$(KC) -n $(APP_NS) apply -f cluster/images-svc.yaml | tee $(LOG_DIR)/images.log
	$(KC) -n $(APP_NS) apply -f cluster/images-sm.yaml | tee -a $(LOG_DIR)/images.log
	$(KC) -n $(APP_NS) apply -f cluster/images-vs.yaml | tee -a $(LOG_DIR)/images.log

transaction: rollout-transaction cluster/transaction-svc.yaml cluster/transaction-sm.yaml cluster/transaction-vs.yaml
	$(KC) -n $(APP_NS) apply -f cluster/transaction-svc.yaml | tee $(LOG_DIR)/transaction.log
	$(KC) -n $(APP_NS) apply -f cluster/transaction-sm.yaml | tee -a $(LOG_DIR)/transaction.log
	$(KC) -n $(APP_NS) apply -f cluster/transaction-vs.yaml | tee -a $(LOG_DIR)/transaction.log

# Update DB and associated monitoring, rebuilding if necessary
db: $(LOG_DIR)/db.repo.log cluster/awscred.yaml cluster/dynamodb-service-entry.yaml cluster/db.yaml cluster/db-sm.yaml cluster/db-vs.yaml
	$(KC) -n $(APP_NS) apply -f cluster/awscred.yaml | tee $(LOG_DIR)/db.log
	$(KC) -n $(APP_NS) apply -f cluster/dynamodb-service-entry.yaml | tee -a $(LOG_DIR)/db.log
	$(KC) -n $(APP_NS) apply -f cluster/db.yaml | tee -a $(LOG_DIR)/db.log
	$(KC) -n $(APP_NS) apply -f cluster/db-sm.yaml | tee -a $(LOG_DIR)/db.log
	$(KC) -n $(APP_NS) apply -f cluster/db-vs.yaml | tee -a $(LOG_DIR)/db.log

# Build & push the images up to the CR
cri: $(LOG_DIR)/logger.repo.log $(LOG_DIR)/users.repo.log $(LOG_DIR)/images.repo.log $(LOG_DIR)/transaction.repo.log $(LOG_DIR)/db.repo.log




$(LOG_DIR)/logger.repo.log: logger/Dockerfile logger/app.py logger/requirements.txt
	make -f k8s.mak --no-print-directory registry-login
	$(DK) build $(ARCH) -t $(CREG)/$(REGID)/logger:$(APP_VER_TAG) logger | tee $(LOG_DIR)/logger.img.log
	$(DK) push $(CREG)/$(REGID)/logger:$(APP_VER_TAG) | tee $(LOG_DIR)/logger.repo.log

$(LOG_DIR)/users.repo.log: users/Dockerfile users/app.py users/requirements.txt
	make -f k8s.mak --no-print-directory registry-login
	$(DK) build $(ARCH) -t $(CREG)/$(REGID)/users:$(APP_VER_TAG) users | tee $(LOG_DIR)/users.img.log
	$(DK) push $(CREG)/$(REGID)/users:$(APP_VER_TAG) | tee $(LOG_DIR)/users.repo.log

$(LOG_DIR)/images.repo.log: images/Dockerfile images/app.py images/requirements.txt
	make -f k8s.mak --no-print-directory registry-login
	$(DK) build $(ARCH) -t $(CREG)/$(REGID)/images:$(APP_VER_TAG) images | tee $(LOG_DIR)/images.img.log
	$(DK) push $(CREG)/$(REGID)/images:$(APP_VER_TAG) | tee $(LOG_DIR)/images.repo.log

$(LOG_DIR)/transaction.repo.log: transaction/Dockerfile transaction/app.py transaction/requirements.txt
	make -f k8s.mak --no-print-directory registry-login
	$(DK) build $(ARCH) -t $(CREG)/$(REGID)/transaction:$(APP_VER_TAG) transaction | tee $(LOG_DIR)/transaction.img.log
	$(DK) push $(CREG)/$(REGID)/transaction:$(APP_VER_TAG) | tee $(LOG_DIR)/transaction.repo.log

# Build the db service
$(LOG_DIR)/db.repo.log: db/Dockerfile db/app.py db/requirements.txt
	make -f k8s.mak --no-print-directory registry-login
	$(DK) build $(ARCH) -t $(CREG)/$(REGID)/cmpt756marketplacedb:$(APP_VER_TAG) db | tee $(LOG_DIR)/db.img.log
	$(DK) push $(CREG)/$(REGID)/cmpt756marketplacedb:$(APP_VER_TAG) | tee $(LOG_DIR)/db.repo.log

# Build the loader
$(LOG_DIR)/loader.repo.log: loader/app.py loader/requirements.txt loader/Dockerfile registry-login
	$(DK) build $(ARCH) -t $(CREG)/$(REGID)/cmpt756loader:$(LOADER_VER) loader  | tee $(LOG_DIR)/loader.img.log
	$(DK) push $(CREG)/$(REGID)/cmpt756loader:$(LOADER_VER) | tee $(LOG_DIR)/loader.repo.log

# Push all the container images to the container registry
# This isn't often used because the individual build targets also push
# the updated images to the registry
cr: registry-login
	$(DK) push $(CREG)/$(REGID)/logger:$(APP_VER_TAG) | tee $(LOG_DIR)/logger.repo.log
	$(DK) push $(CREG)/$(REGID)/users:$(APP_VER_TAG) | tee $(LOG_DIR)/users.repo.log
	$(DK) push $(CREG)/$(REGID)/images:$(APP_VER_TAG) | tee $(LOG_DIR)/images.repo.log
	$(DK) push $(CREG)/$(REGID)/transaction:$(APP_VER_TAG) | tee $(LOG_DIR)/transaction.repo.log	
	$(DK) push $(CREG)/$(REGID)/cmpt756marketplacedb:$(APP_VER_TAG) | tee $(LOG_DIR)/db.repo.log


# The following may not even work.
#
# General Gatling target: Specify CLUSTER_IP, USERS, and SIM_NAME as environment variables. Full output.
run-gatling:
	JAVA_HOME=$(JAVA_HOME) $(GAT) -rsf $(RES_DIR) -sf $(SIM_DIR) -bf $(GAT_DIR)/target/test-classes -s $(SIM_FULL_NAME) -rd "Simulation $(SIM_NAME)" $(GATLING_OPTIONS)

# The following should probably not be used---it starts the job but under most shells
# this process will not be listed by the `jobs` command. This makes it difficult
# to kill the process when you want to end the load test
gatling-music:
	@/bin/sh -c 'CLUSTER_IP=$(INGRESS_IP) USERS=$(USERS) SIM_NAME=ReadMusicSim JAVA_HOME=$(JAVA_HOME) $(GAT) -rsf $(RES_DIR) -sf $(SIM_DIR) -bf $(GAT_DIR)/target/test-classes -s $(SIM_FULL_NAME) -rd "Simulation $(SIM_NAME)" $(GATLING_OPTIONS) $(GAT_SUFFIX)'

# Different approach from gatling-music but the same problems. Probably do not use this.
gatling-user:
	@/bin/sh -c 'CLUSTER_IP=$(INGRESS_IP) USERS=$(USERS) SIM_NAME=ReadUserSim make -e -f k8s.mak run-gatling $(GAT_SUFFIX)'


# ---------------------------------------------------------------------------------------
# Handy bits for exploring the container images... not necessary
image: showcontext registry-login
	$(DK) image ls | tee __header | grep $(REGID) > __content
	head -n 1 __header
	cat __content
	rm __content __header
