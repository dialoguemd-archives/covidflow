FROM python:3.7

EXPOSE 8089
WORKDIR /app

# install poetry

ARG POETRY_VERSION="1.0.0"
RUN \
  pip install --upgrade pip \
  && pip install "poetry==${POETRY_VERSION}" \
  && poetry config virtualenvs.create false

COPY load-tests .
COPY integration-tests-en integration-tests
RUN poetry install -vvv --no-dev

ENV INTEGRATION_TEST_PATH "integration-tests"

ENTRYPOINT ["./run.sh", "socketio"]
CMD ["--no-web", "-c", "5", "-r", "5", "--run-time", "1200s"]
