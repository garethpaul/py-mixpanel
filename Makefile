.PHONY: check docs lint test verify

docs:
	test -f docs/plans/2026-06-08-py-mixpanel-baseline.md
	grep -q "Status: Completed" docs/plans/2026-06-08-py-mixpanel-baseline.md
	grep -q "make check" docs/plans/2026-06-08-py-mixpanel-baseline.md

lint:
	python2 -c "import py_compile; py_compile.compile('mixpanel.py', cfile='/tmp/py-mixpanel-mixpanel.pyc', doraise=True)"
	python2 -c "import py_compile; py_compile.compile('test_mixpanel.py', cfile='/tmp/py-mixpanel-test_mixpanel.pyc', doraise=True)"

test:
	python2 -m unittest test_mixpanel

verify: lint test docs

check: verify
