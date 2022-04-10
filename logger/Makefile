ARCH=--platform x86_64

build:
	docker build $(ARCH) -f Dockerfile -t logger .

run:
	docker container run $(ARCH) --rm --detach --publish 30003:30003 --name logger logger