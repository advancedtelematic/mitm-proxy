QEMU_PORT ?= 2222

DOCKER_IMG := advancedtelematic/tuf-mitm-proxy
DOCKER_TAG := latest
DOCKER_RUN := \
	docker run \
		--rm \
		--interactive \
		--tty \
		--privileged \
		--publish 2222:$(QEMU_PORT) \
		--volume $(IMAGE_DIR):/qemu \
		$(DOCKER_IMG):$(DOCKER_TAG)

SSH_HOST := root@localhost
SSH_OPTS := -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=quiet
SSH := ssh -p $(QEMU_PORT) $(SSH_OPTS) $(SSH_HOST)
SCP := scp -P $(QEMU_PORT) $(SSH_OPTS)


.PHONY: help image run ssh
.DEFAULT_GOAL := help

help: ## Print this message and exit
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%10s\033[0m : %s\n", $$1, $$2}' $(MAKEFILE_LIST)

env_%: # Check that an environment variable is set
	@: $(if ${${*}},,$(error Set the '$*' environment variable))

image: ## Build the docker image
	@docker build --tag $(DOCKER_IMG):$(DOCKER_TAG) .

run: image env_IMAGE_DIR ## Start the docker image
	@$(DOCKER_RUN)

ssh: ## SSH into the qemu image
	@$(SSH)
