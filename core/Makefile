.PHONY: init install install-dev clean lint format test test-integration-en test-integration-fr train-en train-fr shell-en shell-fr

# include source code in any python subprocess
export PYTHONPATH = .

RASA_VERSION=2.0.0a2

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
	@echo "    train-en"
	@echo "        Train English Rasa models"
	@echo "    train-fr"
	@echo "        Train French Rasa models"
	@echo "    shell-en"
	@echo "        Start a Rasa shell using English models"
	@echo "    shell-fr"
	@echo "        Start a Rasa shell using French models"
	@echo "    test-integration-en"
	@echo "        Run integration tests in English"
	@echo "    test-integration-fr"
	@echo "        Run integration tests in French"

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

train-en:
	sh scripts/prepare-training-data.sh en
	docker run -it \
		--rm -v ${PWD}:/app \
		--user ${UID}:${GID} \
		rasa/rasa:${RASA_VERSION}-full train \
		--out models/en \
		--augmentation 0

train-fr:
	sh scripts/prepare-training-data.sh fr
	docker run \
		--rm -v ${PWD}:/app \
		--user ${UID}:${GID} \
		rasa/rasa:${RASA_VERSION}-full train \
		--out models/fr \
		--augmentation 0

test-integration-en:
	CORE_ENDPOINT_URL=http://localhost:5005 INTEGRATION_TESTS_REMINDER_ID_PROFILE_1=v9ZaeZyE INTEGRATION_TESTS_REMINDER_ID_PROFILE_2=JvmKA31V poetry run python -m rasa_integration_testing ../integration-tests-en

test-integration-fr:
	CORE_ENDPOINT_URL=http://localhost:5006 INTEGRATION_TESTS_REMINDER_ID_PROFILE_1=v9ZaeZyE INTEGRATION_TESTS_REMINDER_ID_PROFILE_2=JvmKA31V poetry run python -m rasa_integration_testing ../integration-tests-fr
