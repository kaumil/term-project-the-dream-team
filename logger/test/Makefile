# Makefile for test of Music service (S2)

SERVER=`docker container inspect logger --format '{{.NetworkSettings.IPAddress}}'`

build-logger_test:
	docker image build -f Dockerfile -t logger_test .

# Do not use '-it' options because this will run in non-TTY environment as GitHub Action
run-logger_test:
	docker container run --rm --name logger_test logger_test python3 logger_test.py $(SERVER) 30003
