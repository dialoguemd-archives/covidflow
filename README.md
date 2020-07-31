# covidflow

Copy of the Rasa backend for Dialogue's covid-19 assessment, navigation and follow-ups available at https://covid19.dialogue.co.
This version is not deployed, used for development purposes only.

## Development

### Prerequisites

We expect the following to be installed on the developer workstation:
- Poetry  (see `make init` task below)
- Make
- Docker
  - _Windows_: [Docker Desktop](https://www.docker.com/products/docker-desktop) 2.1.0.5 is recommended
  - _Linux_: docker version >= 19.03.5
- Docker Compose
  - _Windows_: Docker Compose is included as part of Docker Desktop
  - _Linux_: docker-compose version >= 1.24.0

### Setup

To run the application locally, you will need to setup environment variables expected by the application on boot. From the root of the repository, copy the `.env.example` to `.env`, then provide the required values.

- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` and `TWILIO_NUMBER` are used to send SMS notifications for daily check-in reminders.
- `GOOGLE_GEOCODING_API_KEY` is used to translate the user's postal-code into GPS coordinates. The coordinates are in turn used to query the Clinia API (when searching for covid-19 testing locations). (see [Google's Geocoding API](https://developers.google.com/maps/documentation/geocoding/start))
- `GOOGLE_MAPS_API_KEY` and `GOOGLE_MAPS_URL_SIGN_SECRET` are used to produce static google maps image URL, passed on to the frontend. (see [Google's Maps Static API](https://developers.google.com/maps/documentation/maps-static/intro))

### Folder Structure

This repo is like a monorepo in that it contains multiple codebases. Here is an overview of the main folders content:

- The `actions-server` and `core` folders contain the main components of covidflow, and they deploy together.
- The `integration-tests-*` folders contain integration tests which are based on the Nu Echo's rasa-integration-testing framework (not open source yet, but available on pypi).
- The `load-tests` folder contains a small integration of Locust with the rasa-integration-testing tools, allowing us to run load-tests using our test scenarios along with Locust.
- **Apart from this project** but important to mention is the [covid-19](https://github.com/dialoguemd/covid-19) project, which contains the frontend that is connecting to covidflow.

A special note about the `actions-server` project: aside from serving as rasa actions-server, this project also contains:

- `action-server/covidflow/jobs/send_reminders.py`: This script is used inside a helm-job for the purpose of sending daily assessment reminders by SMS. See `job.yml` for more details.
- `action-server/alembic`: This is where the SQL migrations are located. See below for more details about the covidflow tables.

### Makefile tasks

Common tasks:
- `init`: installs poetry.
- `install`: installs project's dependencies using poetry.
- `install-dev`: Same as `install` but with `--no-root` option, which avoid installing the project's package itself.
- `lint`: runs several linter.
- `format`: autofix black and isort errors.
- `test`: runs unit-tests.

Specific to `core`:
- `train-en` and `train-fr`: train the rasa models using docker, and drop the result in `models/en` and `models/fr`.
- `test-integration-en`* and `test-integration-fr`*: run integration testing using the scenario located within the `integration-tests-en` and `integration-tests-fr` folders.

Specific to `load-tests`:
- `locust-rasa`*: runs load tests.

Note that tasks marked with an asterisk will run against a locally running covidflow environment. See below for details.

## Instructions for running the bot

### Train, Build and Run

Within `core`, run the following commands to train the rasa models:

```
make train-en
make train-fr
```

From the root of the repository, build the docker images with:

```
docker-compose build
```

Then run the services using:

```
docker-compose up
```

This will start the following services:

- _core-en_ (`localhost:5005`): The Rasa application with the English model.
- _core-fr_ (`localhost:5006`): The Rasa application with the French model.
- _action_server_ (`localhost:5055`): The Rasa action server that executes forms and custom code.
- _tracker_store_ (`localhost:5432`): The PostgreSQL backed Rasa tracker store.
- _db-migration_: Ephemeral service that runs alembic migration on boot.

### Try it using the frontend

To try it from the frontend, checkout the [Covid-19](https://github.com/dialoguemd/covid-19) repository and:

1. Change the `.env.development` file to assign the following values:
  - `REACT_APP_RASA_SOCKET_ENDPOINT_EN=localhost:5005`
  - `REACT_APP_RASA_SOCKET_ENDPOINT_FR=localhost:5006`
2. Follow the "Running locally" steps on the Covid-19 repository.
3. Once the page opens, click on "Get Started" or navitage to [/chat](http://localhost:3000/#/chat).

### Try it using rasa shell

You can also start services and access the bot using `rasa shell` by starting the application like this:

`docker-compose run core-en shell --debug` or `docker-compose run core-fr shell --debug`

To see the tracker-store and action-server logs:

`docker-compose logs -ft`

## Tests

Aside from the unit tests (which can be run using the `make test` command), one can also run integration tests and load tests which are described below.

### Integration tests

To execute the integration tests locally, first, start the services using `docker-compose up` and, from the core folder, run `make test-integration`. Don't forget to train rasa models beforehand if you made any changes to stories and such.

### Locust load tests

Load tests can be run locally from the load-test package. Run `make init` and `make install` to install poetry and the project dependencies. Simply run `make locust-rasa`. You will need to source the environment variables, an example is in `load-tests/.env.example`.

Load tests can be run and parameterized from its Docker image. Use the root of this project as the build context and run:

`docker build -f load-tests/Dockerfile -t rasa-load-tests .`

The Docker image needs a env-file source for its target URL, an example is in `load-tests/.env.example`. Then, run the image like so.

`docker run -p 8089:8089/tcp --env-file load-tests/.env rasa-load-tests`

If run against localhost, you will need to add the `--network="host"` parameter.

## Database

The actions-server project adds two tables to the tracker-store database (as part of the alembic migration scripts):

- `reminder`: used to store daily assessment reminders. The `send_reminders` helm job uses that table to retrieve any due (and active) reminders.
- `assessment`: used to store all daily assessment results.

While those tables contain a certain amount of standard database columns, the data that is purely related to covid-19 and the dialogue itself is stored in a JSONB column. For instance, the `reminder` table contains (among others) the `last_reminded_at` and `is_canceled` columns, but the JSONB column is responsible for storing the fields `age_over_65` and `has_preconditions` (which are related to covid-19 more specifically).

For more details about the tables and the content of the `JSONB` fields, see the following files:

- `action-server/covidflow/db/assessment.py`
- `action-server/covidflow/db/reminder.py`
