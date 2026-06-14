.PHONY: check build docs lint test verify

override REPO_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

docs:
	@cd "$(REPO_ROOT)" && for plan in docs/plans/*.md; do \
		test -f "$$plan"; \
		grep -q "Status: Completed" "$$plan"; \
		grep -q "make check" "$$plan"; \
	done

lint:
	cd "$(REPO_ROOT)" && python2 -c "import py_compile; py_compile.compile('mixpanel.py', cfile='/tmp/py-mixpanel-mixpanel.pyc', doraise=True)"
	cd "$(REPO_ROOT)" && python2 -c "import py_compile; py_compile.compile('test_mixpanel.py', cfile='/tmp/py-mixpanel-test_mixpanel.pyc', doraise=True)"

test:
	cd "$(REPO_ROOT)" && PYTHONDONTWRITEBYTECODE=1 python2 -m unittest test_mixpanel

build: test

verify: lint test build docs

check: verify
	cd "$(REPO_ROOT)" && scripts/check-baseline.sh
