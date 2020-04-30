.PHONY: init install install-dev install-rasa-sdk clean lint format test test-integration

# include source code in any python subprocess
export PYTHONPATH = .

VENV_LOCATION=.venv

UID:=$(shell id -u)
GID:=$(shell id -g)

help:
	@echo "    init"
	@echo "        Initialize virtual environment"
	@echo "    install"
	@echo "        Install dependencies"
	@echo "    install-dev"
	@echo "        Install dev dependencies"
	@echo "    clean"
	@echo "        Remove Python artifacts"
	@echo "    lint"
	@echo "        Check style with pylama, mypy and black"
	@echo "    format"
	@echo "        Format code with black"
	@echo "    test"
	@echo "        Run py.test (use TEST_FILE variable to test a single file)"
	@echo "    test-integration"
	@echo "        Run integration tests"

init:
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python

install:
	poetry install

install-dev:
	poetry install --no-root

lint:
	poetry run pylama
	poetry run mypy .
	poetry run black --check .
	poetry run isort --check

format:
	poetry run black .
	poetry run isort

test:
	poetry run py.test \
		--cov-report term-missing:skip-covered \
		--cov-report html

test-integration:
	python -m rasa_integration_testing ../integration-tests
