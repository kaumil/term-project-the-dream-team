# Makefile for test of Music service (S2)

SERVER=`docker container inspect db --format '{{.NetworkSettings.IPAddress}}'`

build-db_test:
	docker image build -f Dockerfile -t db_test .

# Do not use '-it' options because this will run in non-TTY environment as GitHub Action
run-db_test:
	docker container run --rm --name db_test db_test python3 db_test.py $(SERVER) 30004
