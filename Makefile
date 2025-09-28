# Copyright (c) 2025 The Suckless Solana Python developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

# Declare phony targets to avoid conflicts with files of the same name
# and to improve make performance.
.PHONY: setup-venv clean-setup-venv setup-mypy static-check \
	clean-static-check setup-pycodestyle pycodestyle-check setup-pytest \
	pytest-check clean-pytest-check clean-pycache clean-all

# Directory where the virtual Python environment will be created.
VENV_DIR ?= $(CURDIR)/.venv

# Execution prefix for activation of the virtual Python environment.
VENV_RUN := $(if $(VENV_DIR),. $(VENV_DIR)/bin/activate &&)

# Create virtual Python environment if it does not already exist.
setup-venv:
ifeq (,$(wildcard $(VENV_DIR)))
ifneq (,$(VENV_DIR))
	@echo "The venv directory ($(VENV_DIR)) does not exist. Creating..."
	@python3 -m venv $(VENV_DIR)
endif
	@$(VENV_RUN) pip install -r $(CURDIR)/requirements.txt
endif

# Remove virtual Python environment directory.
clean-setup-venv:
	@rm -rf $(VENV_DIR)

# Version of Mypy, a static type checker for Python.
MYPY_VERSION ?= 1.15.0

# Install Mypy to enable static type checking.
setup-mypy: setup-venv
	@$(VENV_RUN) if ! pip show mypy &>/dev/null; then \
		pip install mypy==$(MYPY_VERSION); \
	fi

# Directory where Mypy should store its cache.
MYPY_CACHE_DIR ?= $(CURDIR)/.mypy_cache

# Directory containing the Python files to be checked by MyPy.
STATIC_CHECK_DIR ?= $(CURDIR)/solana/

# Run static type checking on all Python files in the project using Mypy.
static-check: setup-mypy
	@$(VENV_RUN) mypy --cache-dir $(MYPY_CACHE_DIR) $(STATIC_CHECK_DIR)

# Remove the Mypy cache directory.
clean-static-check:
	@rm -rf $(MYPY_CACHE_DIR)

# Version of Pycodestyle, a tool to check Python code
# against PEP 8 style conventions.
PYCODESTYLE_VERSION ?= 2.13.0

# Install Pycodestyle to check code against PEP 8 style conventions.
setup-pycodestyle: setup-venv
	@$(VENV_RUN) if ! pip show pycodestyle &>/dev/null; then \
		pip install pycodestyle==$(PYCODESTYLE_VERSION); \
	fi

# Directory containing the Python files to be checked by Pycodestyle.
PYCODESTYLE_DIR ?= $(CURDIR)/solana/

# Comma-separated list of Pycodestyle errors and warnings to ignore.
PYCODESTYLE_IGNORE ?= W391

# Check all Python files in the specified directory
# for PEP 8 compliance using Pycodestyle.
pycodestyle-check: setup-pycodestyle
	@$(VENV_RUN) pycodestyle --ignore=$(PYCODESTYLE_IGNORE) $(PYCODESTYLE_DIR)

# Version of Pytest, the Python framework makes it easy to write small tests.
PYTEST_VESRION ?= 8.3.4

# Version of Pytest AsyncIO plugin, that facilitates testing of code
# that uses the asyncio library.
PYTEST_ASYNCIO_VESRION ?= 0.25.3

# Setup Pytest to provide a unit-test capabilities.
setup-pytest: setup-venv
	@$(VENV_RUN) if ! pip show pytest &>/dev/null; then \
		pip install pytest==$(PYTEST_VESRION); \
	fi
	@$(VENV_RUN) if ! pip show pytest-asyncio &>/dev/null; then \
		pip install pytest-asyncio==$(PYTEST_ASYNCIO_VESRION); \
	fi

# Path to the directory where all tests should be stored.
PYTEST_DIR ?= $(CURDIR)/solana/

# Path to the Pytest configuration ".ini" file.
PYTEST_CONFIG ?= $(CURDIR)/.pytest.ini

# Target cache directory for Pytest.
PYTEST_CACHE_DIR ?= $(CURDIR)/.pytest_cache

# Runs all unit tests provided in the repository.
pytest-check: setup-pytest
	@$(VENV_RUN) pytest $(PYTEST_DIR) -c $(PYTEST_CONFIG) \
		-o cache-dir=$(PYTEST_CACHE_DIR)

# Remove the Pytest cache directory.
clean-pytest-check:
	@rm -rf $(PYTEST_CACHE_DIR)

# Name of the directories where Python stores compiled bytecode files.
PYCACHE_DIR_NAME ?= "__pycache__"

# Remove all __pycache__ directories in the project.
clean-pycache:
	@find . -type d -name $(PYCACHE_DIR_NAME) -exec rm -rf {} +

# Clean up all artifacts, including the virtual environment,
# Mypy cache, and Python cache directories.
clean-all: clean-setup-venv clean-static-check clean-pytest-check clean-pycache
	@echo "All artifacts cleaned."

# vim: set ts=4 sw=4 noexpandtab:

