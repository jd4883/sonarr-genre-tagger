IMAGE_NAME := sonarr-genre-tagger
VERSION := latest
REGISTRY_ADDR := jb6magic

.SILENT:clean
.PHONY: clean

push: tag
	docker push $(REGISTRY_ADDR)/$(IMAGE_NAME):$(VERSION)

tag: build
	docker tag $(IMAGE_NAME):$(VERSION) $(REGISTRY_ADDR)/$(IMAGE_NAME):$(VERSION)

build: Dockerfile
	docker build --no-cache --rm -t $(IMAGE_NAME):$(VERSION) -f Dockerfile .

clean:
	docker container prune -f
	docker image prune -f
	docker volume prune -f
