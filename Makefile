.PHONY: help sync verify test test-functional test-performance lint wiki-sync

help:           ## Show this help
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

sync:           ## Regenerate platform mirrors from knowledge/
	cd v2/implementation && node scripts/sync.mjs

verify:         ## Verify generated mirrors match knowledge/
	cd v2/implementation && node scripts/verify.mjs

test:           ## Run all functional + performance tests
	python3 tests/run.py -v

test-functional:    ## Run functional tests only
	python3 tests/run.py --suite functional -v

test-performance:   ## Run performance / team-health tests only
	python3 tests/run.py --suite performance -v

wiki-sync:      ## Sync docs/wiki/*.md to GitLab Wiki (requires WIKI_TOKEN)
	CI_PROJECT_ID=82070979 python3 scripts/sync-wiki.py
