ARCH=--platform x86_64

build:
	docker build $(ARCH) -f Dockerfile -t transaction .

run:
	docker container run $(ARCH) -it --rm --detached --publish 30002:30002 --name transaction transaction