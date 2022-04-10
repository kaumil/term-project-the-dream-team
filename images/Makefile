ARCH=--platform x86_64

build:
	docker build $(ARCH) -f Dockerfile -t images .

run:
	docker container run $(ARCH) --rm --detach --publish 30001:30001 --name images images