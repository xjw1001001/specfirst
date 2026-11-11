# Commands for the Linux environment (see env/README.md).
# Every recipe first sources scripts/env.sh, which finds the Python
# environment, the R library and the fetch cache of this checkout.
SHELL := /bin/bash
.DEFAULT_GOAL := help
ENV := . scripts/env.sh &&
WP ?= base-0

.PHONY: help install doctor fetch test evidence pilot methods defects lint ascii gate lock

help:  ## list the targets
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | sed -E 's/:.*## +/: /'

install:  ## create the Python environment and the R library from the lock files
	bash env/install.sh

doctor:  ## compare the environment with the lock files
	$(ENV) specfirst doctor

fetch:  ## clone the pinned sources into the cache and verify them
	$(ENV) specfirst fetch

test:  ## unit tests (fast, no cache needed)
	$(ENV) python -m pytest -m "not evidence" -q

evidence:  ## rerun the evidence spikes (about 7 minutes, needs `make fetch`)
	$(ENV) SPECFIRST_STRICT=1 python -m pytest tests/evidence -m evidence -s -q

pilot:  ## the tests behind ADR-001 on the pilot kit (about 1 minute, needs `make fetch`)
	$(ENV) SPECFIRST_STRICT=1 python -m pytest tests/pilot -m evidence -s -q

methods:  ## the method vectors in Python and in R, and registry.json (a few seconds, needs R)
	$(ENV) specfirst methods && SPECFIRST_STRICT=1 python -m pytest tests/methods -s -q

defects:  ## planted defects on the pilot kit, both engines (about 2 minutes, needs `make fetch` and R)
	$(ENV) SPECFIRST_STRICT=1 python -m pytest tests/defects -s -q

lint:  ## ruff
	$(ENV) python -m ruff check .

ascii:  ## the ASCII check (rule R10)
	$(ENV) python -m specfirst.asciicheck

gate:  ## run the gate of a work package: make gate WP=base-0
	$(ENV) specfirst gate $(WP)

lock:  ## rewrite the lock files (on purpose only; commit the result)
	bash env/lock.sh
