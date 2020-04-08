.PHONY: init install install-dev install-rasa-sdk clean lint format test train-en train-fr shell-en shell-fr

# include source code in any python subprocess
export PYTHONPATH = .

VENV_LOCATION=.venv
ACTIVATE_VENV=poetry run

RASA_VERSION=1.9.4
RASA_SDK_VERSION=1.9.0

UID:=$(shell id -u)
GID:=$(shell id -g)

help:
	@echo "    init"
	@echo "        Initialize virtual environment"
	@echo "    install"
	@echo "        Install dependencies"
	@echo "    install-dev"
	@echo "        Install dev dependencies"
	@echo "    install-rasa-sdk"
	@echo "        Install Rasa SDK"
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

init:
	python3 -m venv ${VENV_LOCATION}
	${ACTIVATE_VENV} pip install --upgrade pip

install:
	${ACTIVATE_VENV} pip install -r requirements.txt

install-dev:
	${ACTIVATE_VENV} pip install -r requirements-dev.txt

install-rasa-sdk:
	${ACTIVATE_VENV} pip install rasa-sdk==${RASA_SDK_VERSION}

lint:
	${ACTIVATE_VENV} pylama
	${ACTIVATE_VENV} mypy .
	${ACTIVATE_VENV} black --check .
	${ACTIVATE_VENV} isort --check

format:
	${ACTIVATE_VENV} black .
	${ACTIVATE_VENV} isort

test:
	${ACTIVATE_VENV} py.test \
		--cov-report term-missing:skip-covered \
		--cov-report html

train-en:
	sh scripts/prepare-training-data.sh en
	docker run \
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
