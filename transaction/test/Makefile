# Makefile for test of Music service (S2)

SERVER=`docker container inspect transaction --format '{{.NetworkSettings.IPAddress}}'`

build-transaction_test:
	docker image build -f Dockerfile -t transaction_test .

# Do not use '-it' options because this will run in non-TTY environment as GitHub Action
run-transaction_test:
	docker container run --rm --name transaction_test transaction_test python3 transaction_test.py $(SERVER) 30002
