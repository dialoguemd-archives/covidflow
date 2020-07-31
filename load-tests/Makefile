.PHONY: init install lint format test locust-rasa

RASA_VERSION=2.0.0a1

UID:=$(shell id -u)
GID:=$(shell id -g)

help:
	@echo "    init"
	@echo "        Initialize virtual environment"
	@echo "    install"
	@echo "        Install dependencies"
	@echo "    lint"
	@echo "        Check style with pylama, mypy and black"
	@echo "    format"
	@echo "        Format code with black"
	@echo "    test"
	@echo "        Run py.test (use TEST_FILE variable to test a single file)"
	@echo "    locust-rasa"
	@echo "        Execute locust file, starting the locust web server"

init:
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python

install:
	poetry install

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

locust-rasa:
	poetry run locust -f load_tests/socketio_locustfile.py --no-web -c 5 -r 5 --run-time 30s
