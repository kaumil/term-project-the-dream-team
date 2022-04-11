#
# Janky front-end to bring some sanity (?) to the litany of tools and switches
# in setting up, tearing down and validating your Minikube cluster for working
# with k8s and istio.
#
# This file covers off building the Docker images and optionally running them
#
# The intended approach to working with this makefile is to update select
# elements (body, id, IP, port, etc) as you progress through your workflow.
# Where possible, stodout outputs are tee into .out files for later review.
#
# Switch to alternate container registry by setting CREG accordingly.
#
# This script is set up for Github's newly announced (and still beta) container
# registry to side-step DockerHub's throttling of their free accounts.
# If you wish to switch back to DockerHub, CREG=docker.io
#
# TODO: You must run the template processor to fill in the template variables "ZZ-*"
#

CREG=ghcr.io
REGID=krp30

DK=docker

# Keep all the logs out of main directory
LOG_DIR=logs

all: users images transaction logger db

deploy: users images transaction db logger
	$(DK) run -t --publish 30000:30000 --detach --name users $(CREG)/$(REGID)/users:e3 | tee users.svc.log
	$(DK) run -t --publish 30001:30001 --detach --name images $(CREG)/$(REGID)/images:e3 | tee images.svc.log
	$(DK) run -t --publish 30002:30002 --detach --name transaction $(CREG)/$(REGID)/transaction:e3 | tee transaction.svc.log
	$(DK) run -t --publish 30003:30003 --detach --name logger $(CREG)/$(REGID)/logger:e3 | tee logger.svc.log
	$(DK) run -t \
		-e AWS_REGION="us-west-2" \
		-e AWS_ACCESS_KEY_ID="AKIAIB3X6A7VLFNGSVUQ" \
		-e AWS_SECRET_ACCESS_KEY="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" \
		-e AWS_SESSION_TOKEN="" \
            --publish 30004:30004 --detach --name db $(CREG)/$(REGID)/cmpt756marketplacedb:e3 | tee db.svc.log

scratch:
	$(DK) stop `$(DK) ps -a -q --filter name="db"` | tee db.stop.log
	$(DK) stop `$(DK) ps -a -q --filter name="logger"` | tee logger.stop.log
	$(DK) stop `$(DK) ps -a -q --filter name="users"` | tee product.stop.log
	$(DK) stop `$(DK) ps -a -q --filter name="images"` | tee cart.stop.log
	$(DK) stop `$(DK) ps -a -q --filter name="transaction"` | tee customer.stop.log

clean:
	rm $(LOG_DIR)/{images,db,logger,transaction,users}.{img,repo,svc}.log

images: $(LOG_DIR)/images.repo.log

logger: $(LOG_DIR)/logger.repo.log

db: $(LOG_DIR)/db.repo.log

transaction: $(LOG_DIR)/transaction.repo.log

users: $(LOG_DIR)/users.repo.log

$(LOG_DIR)/images.repo.log: images/app.py images/Dockerfile
	$(DK) build -t $(CREG)/$(REGID)/images:e3 images | tee $(LOG_DIR)/images.img.log
	$(DK) push $(CREG)/$(REGID)/images:e3 | tee $(LOG_DIR)/images.repo.log

$(LOG_DIR)/logger.repo.log: logger/app.py logger/Dockerfile
	$(DK) build -t $(CREG)/$(REGID)/logger:e3 logger | tee $(LOG_DIR)/logger.img.log
	$(DK) push $(CREG)/$(REGID)/logger:e3 | tee $(LOG_DIR)/logger.repo.log

$(LOG_DIR)/db.repo.log: db/Dockerfile
	$(DK) build -t $(CREG)/$(REGID)/cmpt756marketplacedb:e3 db | tee $(LOG_DIR)/db.img.log
	$(DK) push $(CREG)/$(REGID)/cmpt756marketplacedb:e3 | tee $(LOG_DIR)/db.repo.log

$(LOG_DIR)/transaction.repo.log: transaction/app.py transaction/Dockerfile
	$(DK) build -t $(CREG)/$(REGID)/transaction:e3 cart | tee $(LOG_DIR)/transaction.img.log
	$(DK) push $(CREG)/$(REGID)/transaction:e3 | tee $(LOG_DIR)/transaction.repo.log

$(LOG_DIR)/users.repo.log: users/app.py users/Dockerfile
	$(DK) build -t $(CREG)/$(REGID)/users:e3 users | tee $(LOG_DIR)/users.img.log
	$(DK) push $(CREG)/$(REGID)/users:e3 | tee $(LOG_DIR)/users.repo.log
