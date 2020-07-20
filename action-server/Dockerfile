FROM rasa/rasa:2.0.0a1 as base
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

# add wait-for-it (used to run db-migrations in dev)
COPY scripts/wait-for-it.sh wait-for-it.sh
RUN chmod +x wait-for-it.sh

USER 1001

FROM base as final

COPY alembic alembic
COPY alembic.ini alembic.ini

COPY covidflow covidflow

ENTRYPOINT [ ]
CMD [ "rasa", "run", "actions", "--actions", "covidflow.actions", "--port", "8080" ]
