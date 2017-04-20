.PHONY: docker help
.DEFAULT_GOAL := help

docker: ## Build the docker image
	@docker build -t advancedtelematic/tuf-mitm-proxy:latest .

help: ## Print this message and exit
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%16s\033[0m : %s\n", $$1, $$2}' $(MAKEFILE_LIST)
