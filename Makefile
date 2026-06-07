.PHONY: help sync verify test test-functional test-performance lint wiki-sync install

help:           ## Show this help
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

sync:           ## Regenerate platform mirrors from knowledge/
	node implementation/scripts/sync.mjs --root implementation

verify:         ## Verify generated mirrors match knowledge/
	node implementation/scripts/sync.mjs --root implementation --check

install:        ## Install into a project (see: make install TARGET=... PLATFORM=cursor)
	@test -n "$(TARGET)" || (echo "Usage: make install TARGET=<dir> [PLATFORM=all|cursor|github|gemini|opencode|pi]" && exit 1)
	bash scripts/install.sh --target "$(TARGET)" --platform "$(or $(PLATFORM),all)"

test:           ## Run all functional + performance tests
	python3 tests/run.py -v

test-functional:    ## Run functional tests only
	python3 tests/run.py --suite functional -v

test-performance:   ## Run performance / team-health tests only
	python3 tests/run.py --suite performance -v

wiki-sync:      ## Sync docs/wiki/*.md to GitLab Wiki (requires WIKI_TOKEN)
	CI_PROJECT_ID=82070979 python3 scripts/sync-wiki.py
