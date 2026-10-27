SHELL := /usr/bin/env bash

.PHONY: setup lint test security security-check optional-assets validate validate-repository policy-check validate-pr validate-exceptions validate-risk build-artifact verify-artifact deploy-hook rollback-hook check build baseline-guard baseline-test

setup:
	bash scripts/setup.sh

lint:
	bash scripts/lint.sh

test:
	bash scripts/test.sh

security:cd
	bash scripts/security.sh

security-check:
	bash scripts/security-check.sh

optional-assets:
	bash scripts/validate-optional-assets.sh

validate:
	bash scripts/validate.sh
	bash scripts/validate-repository.sh
	bash scripts/validate-policies.sh
	bash scripts/validate-baseline.sh
	bash scripts/test-baseline-guard.sh

validate-repository:
	bash scripts/validate-repository.sh

policy-check:
	bash scripts/validate-policies.sh

validate-pr:
	bash scripts/validate-pr.sh

validate-exceptions:
	bash scripts/validate-exceptions.sh

validate-risk:
	bash scripts/validate-risk.sh

baseline-guard:
	bash scripts/validate-baseline.sh

baseline-test:
	bash scripts/test-baseline-guard.sh

build-artifact:
	bash scripts/build-artifact.sh

verify-artifact:
	bash scripts/verify-artifact.sh

deploy-hook:
	bash scripts/deployment-hook.sh

rollback-hook:
	bash scripts/rollback-hook.sh

check: lint test security validate
	@echo "Baseline checks passed."

build:
	$(MAKE) build-artifact
