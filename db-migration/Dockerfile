FROM python:3.6.8-slim-stretch

# install poetry

ARG POETRY_VERSION="1.0.5"
ENV \
  PYTHONFAULTHANDLER=TRUE \
  PYTHONUNBUFFERED=TRUE \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_NO_CACHE_DIR=off
RUN \
  pip install --upgrade pip \
  && pip install "poetry==${POETRY_VERSION}" \
  && poetry config virtualenvs.create false

# install dependencies

COPY pyproject.toml poetry.lock ./
RUN poetry install -vvv --no-dev

# copy project

WORKDIR /app

# add wait-for-it (used in dev)
COPY scripts/wait-for-it.sh wait-for-it.sh 
RUN chmod +x wait-for-it.sh

COPY . .