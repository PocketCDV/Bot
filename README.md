# PocketCDV Telegram Bot

A Telegram bot that puts the Collegium Da Vinci timetable in your pocket. Students log in once through a Telegram Web App, and the bot fetches their schedule from the university portal (wu.cdv.pl) on their behalf, shows it day by day and reminds them about upcoming classes.

## Features

- **Timetable browsing** through an inline-keyboard interface built on aiogram FSM scenes: home page, schedule by day, class details, settings.
- **Login via Telegram Web App**: a FastAPI service handles the portal login and stores the user's session.
- **Notifications**: a daily summary of classes and a reminder before each upcoming class.
- **Background jobs** on Celery with RabbitMQ: session refresh, home page refresh, notification planning and dispatch.
- **Localization** in English and Ukrainian (Fluent).
- **Rate limiting** on the auth API.
- **CI/CD**: GitHub Actions builds a Docker image, pushes it to GHCR and deploys it to a VPS over SSH.

## Stack

Python 3.14 · aiogram 3 · FastAPI · SQLAlchemy 2 (async) · Alembic · PostgreSQL · Redis · Celery · RabbitMQ · aiohttp · BeautifulSoup · Docker

## Running locally

Requirements: Python 3.14, Poetry, Docker.

```bash
# Postgres, Redis and RabbitMQ
docker compose -f compose-local.yaml up -d

poetry install
# Fill .env: telegram_bot_token, database_dsn, redis_dsn, rabbitmq_dsn, api_url, web_app_url
alembic upgrade head

poetry run python run_polling.py      # the bot (long polling)
poetry run python run_asgi.py         # the auth API on :8000
poetry run celery -A app.celery.worker.worker worker -l info
poetry run celery -A app.celery.worker.worker beat -l info
```

The Web App frontend lives in [PocketCDV/Frontend](https://github.com/PocketCDV/Frontend).
