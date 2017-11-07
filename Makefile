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
		--volume $(CURDIR)/src:/pipenv/src \
		$(DOCKER_IMG):$(DOCKER_TAG)

SSH_HOST := root@localhost
SSH_OPTS := -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null
SSH := ssh -p $(QEMU_PORT) $(SSH_OPTS) $(SSH_HOST)
SCP := scp -P $(QEMU_PORT) $(SSH_OPTS)


.PHONY: help test image start ssh
.DEFAULT_GOAL := help

help: ## Print this message and exit
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%10s\033[0m : %s\n", $$1, $$2}' $(MAKEFILE_LIST)

env_%: # Check that an environment variable is set
	@: $(if ${${*}},,$(error Set the '$*' environment variable))

init: ## Install pipenv and the project dependencies.
	@command -v pipenv >/dev/null || pip install pipenv
	@pipenv install --dev

test: ## Run the local test suite.
	@pipenv run mypy --strict --config-file setup.cfg src/
	@pipenv run py.test --cov=src --flake8

clean: ## Delete python cache files.
	@find src -type d -name "*cache*" -print0 | xargs -0 rm -f

image: ## Build the docker image
	@docker build --tag $(DOCKER_IMG):$(DOCKER_TAG) .

start: image env_IMAGE_DIR ## Start the docker image
	@$(DOCKER_RUN)

ssh: ## SSH into qemu running inside docker
	@$(SSH)
