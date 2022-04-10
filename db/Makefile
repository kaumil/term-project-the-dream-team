ARCH=--platform x86_64

build:
	docker build $(ARCH) -f Dockerfile -t db .

run:
	docker container run $(ARCH) --rm --detach --publish 30004:30004 --name db db