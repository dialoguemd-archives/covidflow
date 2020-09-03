FROM rasa/rasa:2.0.0a4-full
EXPOSE 8080

COPY poetry.lock poetry.lock
COPY pyproject.toml pyproject.toml

USER root
ARG POETRY_VERSION="1.0.0"
ENV \
  PYTHONFAULTHANDLER=TRUE \
  PYTHONUNBUFFERED=TRUE \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_NO_CACHE_DIR=off
RUN \
  pip install --upgrade pip \
  && pip install "poetry==${POETRY_VERSION}" \
  && poetry config virtualenvs.create false
RUN poetry install

USER 1001

COPY credentials.yml endpoints.yml ./
COPY models models
COPY core core

CMD [ "run", "--port", "8080", "--enable-api", "--cors", "*" ]
