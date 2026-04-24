FROM python:3.14.3-slim
ENV POETRY_VIRTUALENVS_IN_PROJECT=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --only main --no-interaction

COPY . .

RUN poetry run pybabel compile -d locales -D messages

RUN adduser --disabled-password appuser && chown -R appuser .
USER appuser
