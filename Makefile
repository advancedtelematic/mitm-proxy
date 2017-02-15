.PHONY: help run test
.DEFAULT_GOAL := help

help:  ## Print this help message and exit
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%8s\033[0m : %s\n", $$1, $$2}' $(MAKEFILE_LIST)

run:  ## Run the app
	@./app/tuf-mitm-proxy "$(RUNARGS)"

test:  ## Run the full test suite
	@./app/test.sh
