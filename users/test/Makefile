# Makefile for test of Music service (S2)

SERVER=`docker container inspect users --format '{{.NetworkSettings.IPAddress}}'`

build-users_test:
	docker image build -f Dockerfile -t users_test .

# Do not use '-it' options because this will run in non-TTY environment as GitHub Action
run-users_test:
	docker container run --rm --name users_test users_test python3 users_test.py $(SERVER) 30000
