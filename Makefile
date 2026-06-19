.PHONY: check build docs lint test mutations verify

override REPO_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
PYTHON ?= python2

docs:
	@cd "$(REPO_ROOT)" && for plan in docs/plans/*.md; do \
		test -f "$$plan"; \
		grep -q "Status: Completed" "$$plan"; \
		grep -q "make check" "$$plan"; \
	done

lint:
	cd "$(REPO_ROOT)" && $(PYTHON) -c "import py_compile; py_compile.compile('mixpanel.py', cfile='/tmp/py-mixpanel-mixpanel.pyc', doraise=True)"
	cd "$(REPO_ROOT)" && $(PYTHON) -c "import py_compile; py_compile.compile('test_mixpanel.py', cfile='/tmp/py-mixpanel-test_mixpanel.pyc', doraise=True)"
	cd "$(REPO_ROOT)" && $(PYTHON) -c "import py_compile; py_compile.compile('scripts/test-review-mutations.py', cfile='/tmp/py-mixpanel-mutations.pyc', doraise=True)"

test:
	cd "$(REPO_ROOT)" && PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest test_mixpanel

mutations:
	cd "$(REPO_ROOT)" && PYTHONDONTWRITEBYTECODE=1 $(PYTHON) scripts/test-review-mutations.py

build: test

verify: lint test build docs

check: verify mutations
	cd "$(REPO_ROOT)" && scripts/check-baseline.sh
