.PHONY: check build docs lint test verify

docs:
	@for plan in docs/plans/*.md; do \
		test -f "$$plan"; \
		grep -q "Status: Completed" "$$plan"; \
		grep -q "make check" "$$plan"; \
	done

lint:
	python2 -c "import py_compile; py_compile.compile('mixpanel.py', cfile='/tmp/py-mixpanel-mixpanel.pyc', doraise=True)"
	python2 -c "import py_compile; py_compile.compile('test_mixpanel.py', cfile='/tmp/py-mixpanel-test_mixpanel.pyc', doraise=True)"

test:
	python2 -m unittest test_mixpanel

build: test

verify: lint test build docs

check: verify
