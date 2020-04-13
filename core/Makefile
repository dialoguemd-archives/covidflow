.PHONY: init install install-dev install-rasa-sdk clean lint format test train-en train-fr shell-en shell-fr

# include source code in any python subprocess
export PYTHONPATH = .

VENV_LOCATION=.venv
ACTIVATE_VENV=test -d ${VENV_LOCATION} \
  && echo "Using .venv" \
  && . ${VENV_LOCATION}/bin/activate;

RASA_VERSION=1.9.4
RASA_SDK_VERSION=1.9.0

SOURCE_FOLDER=core
TESTS_FOLDER=tests
ENV_VARS=`grep -v '^\#' .env | grep -Eo '\w+=\S+'`

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
	${ACTIVATE_VENV} pylama ${SOURCE_FOLDER} ${TESTS_FOLDER}
	${ACTIVATE_VENV} mypy ${SOURCE_FOLDER} ${TESTS_FOLDER}
	${ACTIVATE_VENV} black --check ${SOURCE_FOLDER} ${TESTS_FOLDER}

format:
	${ACTIVATE_VENV} black ${SOURCE_FOLDER} ${TESTS_FOLDER}

test:
	${ACTIVATE_VENV} py.test "${TESTS_FOLDER}/${TEST_FILE}" \
		--cov-report term-missing:skip-covered \
		--cov-report html \
		--cov-fail-under=80 \
		--cov ${SOURCE_FOLDER}

train-en:
	sh scripts/prepare-training-data.sh en
	docker run \
	    -v ${PWD}:/app \
		--user ${UID}:${GID} \
		rasa/rasa:${RASA_VERSION}-full train \
		--out models/en \
		--augmentation 0

train-fr:
	sh scripts/prepare-training-data.sh fr
	docker run \
	    -v ${PWD}:/app \
		--user ${UID}:${GID} \
		rasa/rasa:${RASA_VERSION}-full train \
		--out models/fr \
		--augmentation 0

shell-en:
	docker run \
		--rm -it \
		-v ${PWD}:/app \
		--env ACTION_SERVER_ENDPOINT=http://actions:8080/webhook \
		--env TRACKER_STORE_ENDPOINT=tracker_store \
		--network rasa-covid19_default \
		rasa/rasa:${RASA_VERSION}-full shell \
		--model models/en
		--debug

shell-fr:
	docker run \
		--rm -it \
		-v ${PWD}:/app \
		--env ACTION_SERVER_ENDPOINT=http://actions:8080/webhook \
		--env TRACKER_STORE_ENDPOINT=tracker_store \
		--network rasa-covid19_default \
		rasa/rasa:${RASA_VERSION}-full shell \
		--model models/fr
		--debug
