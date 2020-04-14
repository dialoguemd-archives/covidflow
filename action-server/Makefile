.PHONY: init install install-dev install-rasa-sdk clean lint format test

# include source code in any python subprocess
export PYTHONPATH = .

VENV_LOCATION=.venv
ACTIVATE_VENV=test -d ${VENV_LOCATION} \
  && echo "Using .venv" \
  && . ${VENV_LOCATION}/bin/activate;

RASA_VERSION=1.9.4
RASA_SDK_VERSION=1.9.0

SOURCE_FOLDER=actions
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
