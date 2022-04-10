ARCH=--platform x86_64

build:
	docker build $(ARCH) -f Dockerfile -t users .

run:
	docker container run $(ARCH) --rm --detach --publish 30000:30000 --name users users