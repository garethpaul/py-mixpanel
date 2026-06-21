.PHONY: check build docs lint mutations root-test test verify

override SHELL := /bin/sh
override .SHELLFLAGS := -c
ifneq ($(strip $(MAKEFILES)),)
$(error MAKEFILES must be empty; repository verification requires this Makefile to be loaded alone)
endif
override MAKEFILES :=
ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override REPO_ROOT := $(shell path='$(subst ','"'"',$(MAKEFILE_LIST))'; if [ -x /usr/bin/sed ]; then sed_path=/usr/bin/sed; elif [ -x /bin/sed ]; then sed_path=/bin/sed; else exit 1; fi; path=$$(printf '%s' "$$path" | "$$sed_path" 's/^ //'); [ -f "$$path" ] || exit 1; directory=$$(/usr/bin/dirname -- "$$path"); CDPATH= cd -- "$$directory" && /bin/pwd -P)
export REPO_ROOT
ifeq ($(strip $(REPO_ROOT)),)
$(error repository Makefile path could not be resolved)
endif
PYTHON ?= python2
ifneq ($(filter python python2,$(PYTHON)),$(PYTHON))
$(error PYTHON must be python or python2)
endif

docs:
	@cd "$$REPO_ROOT" && for plan in docs/plans/*.md; do \
		test -f "$$plan"; \
		grep -q "Status: Completed" "$$plan"; \
		grep -q "make check" "$$plan"; \
	done

lint:
	cd "$$REPO_ROOT" && $(PYTHON) -c "import py_compile; py_compile.compile('mixpanel.py', cfile='/tmp/py-mixpanel-mixpanel.pyc', doraise=True)"
	cd "$$REPO_ROOT" && $(PYTHON) -c "import py_compile; py_compile.compile('test_mixpanel.py', cfile='/tmp/py-mixpanel-test_mixpanel.pyc', doraise=True)"
	cd "$$REPO_ROOT" && $(PYTHON) -c "import py_compile; py_compile.compile('scripts/test-review-mutations.py', cfile='/tmp/py-mixpanel-mutations.pyc', doraise=True)"

test:
	cd "$$REPO_ROOT" && PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest test_mixpanel

mutations:
	cd "$$REPO_ROOT" && PYTHONDONTWRITEBYTECODE=1 $(PYTHON) scripts/test-review-mutations.py

build: test

root-test:
	cd "$$REPO_ROOT" && scripts/test-makefile-root.sh

verify: lint test build docs root-test

check: verify mutations
	cd "$$REPO_ROOT" && scripts/check-baseline.sh
