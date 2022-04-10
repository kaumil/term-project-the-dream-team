# Makefile for test of Music service (S2)

SERVER=`docker container inspect images --format '{{.NetworkSettings.IPAddress}}'`

build-images_test:
	docker image build -f Dockerfile -t images_test .

# Do not use '-it' options because this will run in non-TTY environment as GitHub Action
run-images_test:
	docker container run --rm --name images_test images_test python3 images_test.py $(SERVER) 30001
