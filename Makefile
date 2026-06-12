.PHONY: check build docs lint test verify

docs:
	@for plan in docs/plans/*.md; do \
		test -f "$$plan"; \
		grep -q "Status: Completed" "$$plan"; \
		grep -q "make check" "$$plan"; \
	done

lint:
	@if command -v python2 >/dev/null 2>&1; then \
		python2 -c "import py_compile; py_compile.compile('mixpanel.py', cfile='/tmp/py-mixpanel-mixpanel.pyc', doraise=True)"; \
		python2 -c "import py_compile; py_compile.compile('test_mixpanel.py', cfile='/tmp/py-mixpanel-test_mixpanel.pyc', doraise=True)"; \
	else \
		echo "Skipping legacy Python 2 syntax checks: python2 is not installed."; \
	fi

test:
	@if command -v python2 >/dev/null 2>&1; then \
		PYTHONDONTWRITEBYTECODE=1 python2 -m unittest test_mixpanel; \
	else \
		echo "Skipping legacy Python 2 Mixpanel tests: python2 is not installed."; \
	fi

build: test

verify: lint test build docs

check: verify
	scripts/check-baseline.sh
