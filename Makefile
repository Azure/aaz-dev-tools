.PHONY: help mcp mcp-install venv

VENV ?= .venv
PYTHON ?= python3
ACTIVATE := . $(VENV)/bin/activate

help:
	@echo "Available targets:"
	@echo "  make venv         Create the local Python virtualenv ($(VENV))"
	@echo "  make mcp-install  Install aaz-dev-tools + aaz-dev-mcp into $(VENV)"
	@echo "  make mcp          Start the aaz-dev MCP server over stdio"

$(VENV)/bin/activate:
	$(PYTHON) -m venv $(VENV)

venv: $(VENV)/bin/activate

mcp-install: venv
	$(ACTIVATE) && pip install -e . && pip install -e src/aaz_dev_mcp

mcp: venv
	@if [ ! -x "$(VENV)/bin/aaz-dev-mcp" ]; then \
		echo "aaz-dev-mcp not installed; run 'make mcp-install' first." >&2; \
		exit 1; \
	fi
	$(ACTIVATE) && aaz-dev-mcp
