# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

PocketCDV is an aiogram-based Telegram bot that wraps the CDV (`wu.cdv.pl`) student schedule portal. It scrapes/fetches the upstream HTTP API using a session cookie (`WU_PHPSESSID`) on the user's behalf, organizes results into schedule records, and renders them through an inline-keyboard FSM-driven UI. A FastAPI ASGI app and a Celery worker run alongside the bot to handle the web-app login flow and periodic refresh jobs.

Stack: Python 3.14, aiogram 3, FastAPI/uvicorn, SQLAlchemy (async) + Alembic, PostgreSQL, Redis (FSM storage), RabbitMQ (Celery broker), aiogram-i18n with Fluent.

## Commands

Dependency management is via Poetry (`pyproject.toml`). All entrypoints expect a `.env` file in the project root that satisfies `Config` in `config.py`.

```bash
# Install
poetry install

# Bring up Postgres / Redis / RabbitMQ for local dev
docker compose -f compose-local.yaml up -d

# Run the bot (pick one)
poetry run python run_polling.py      # long polling, dev default
poetry run python run_webhook.py      # aiohttp webhook server, port 8080
poetry run python run_asgi.py         # FastAPI auth API on port 8000

# Celery (separate processes — both required for cron tasks)
poetry run celery -A app.celery.worker.worker worker -l info
poetry run celery -A app.celery.worker.worker beat   -l info

# Alembic migrations (DSN is pulled from .env via migrations/env.py)
poetry run alembic revision --autogenerate -m "msg"
poetry run alembic upgrade head

# One-off room-name backfill (prompts for a session cookie interactively)
poetry run python -m scripts.fetch_rooms.fetch_rooms
```

There is no test suite or linter configured.

## Architecture

### Process topology

Three deployable processes share the same `app/` package and `config.py`:

1. **Bot** (`run_polling.py` / `run_webhook.py`) — builds a `Dispatcher` via `app.bot.bot.create_dispatcher()`, which wires controllers, middlewares, routers, and scenes.
2. **ASGI auth API** (`run_asgi.py` → `app.asgi.asgi:app`) — FastAPI app serving `/api/v1/auth/*`. Validates Telegram WebApp init data and exchanges WU credentials for a session cookie that gets written into the user's Redis FSM state, so the user appears "logged in" to the bot.
3. **Celery worker + beat** (`app.celery.worker`) — runs two cron tasks defined in `app.celery.crons`: `session_refresh` (every 10 min on :05) refreshes every user's `WU_PHPSESSID`; `home_page_refresh` (every 10 min on :00) re-renders the home message in place for any user currently parked on the Home scene.

All three processes construct their own `DatabaseController`/`Redis`/`ClientController`/`CDVController` instances — the controllers are designed to be cheap to instantiate per-process.

### Layered controllers (`app/assets/controllers/`)

A two-tier controller pattern is used consistently and should be preserved:

- **`AbstractSessionController[_S]`** (`session.py`) — base for any single-session resource. Lazily creates one session per instance, validates it on each access, and recreates it on recoverable errors. `DatabaseController` and `ClientController` (aiohttp) both subclass this. Always access the underlying session via `async with controller.session() as s`.
- **`CDVController`** wraps `ClientController` to speak the CDV `wu.cdv.pl` HTTP API. Login/refresh return `WU_PHPSESSID` cookie strings; `error_code == 56` from CDV is mapped to `InvalidSessionError`.
- **`ScheduleController`** is the high-level façade used by both the bot scenes and the celery cron. It calls `CDVController` for raw entries, then resolves room/teacher names from Postgres, falling back to the CDV API + insert-on-miss for unknown teachers.

When adding a new external integration, follow the same pattern: low-level session controller, then a higher-level controller that combines it with the database.

### Schedule data model (`app/assets/models/records/`)

Plain Pydantic record models, **not** SQLAlchemy models:

- `RawClassRecord` — raw row from CDV `get-student-plan`.
- `ClassRecord` — enriched single class with resolved room/teacher names.
- `DailyScheduleRecord` — list of `ClassRecord` for one day; renders itself to an HTML string.
- `ScheduleRecord` — `Dict[date, DailyScheduleRecord]`; has `to_json`/`from_json` so it can round-trip through aiogram FSM state.

Persistence in Postgres is intentionally narrow — `Base`, `User`, `Room`, `Teacher` live in `app/assets/models/database/` (one class per file, re-exported from `database/__init__.py`). Schedules themselves are never stored, only fetched on demand and cached in FSM state.

### Bot UI: scenes + middlewares

- **Scenes** (`app/bot/scenes/`) extend `BaseScene` (`scenes/base.py`), which provides generic `BackAction` / `SwitchSceneAction` callback-query handlers using a `_prepare_coroutine` helper that filters kwargs by the target coroutine's signature — handlers can declare only the kwargs they want and the rest are dropped silently. Use `self.wizard.goto(...)` / `self.wizard.back()` to navigate; pass scene-specific data as kwargs (e.g. `goto("detail", class_record=...)`).
- **Callback actions** (`app/bot/actions/`) all inherit `BaseAction` (a `CallbackData` subclass). Add new actions there rather than encoding raw strings in callback data.
- **Keyboards** are pure builder functions in `app/bot/keyboards/` that take an `I18nContext` and return `InlineKeyboardMarkup`.
- **Middlewares** (`app/bot/middlewares/`) registered as outer middlewares on `dispatcher.update`, in this order: `DatabaseMiddleware` → `UserMiddleware` (upserts the `User` row) → `SessionIDMiddleware` (validates/refreshes `WU_PHPSESSID` from FSM state, sets it to `None` if invalid) → `UserMessageMiddleware`. After the chain, `aiogram-i18n` is set up with a custom `LocaleManager` that reads/writes locale from the `users` table.
- **`UserMessage`** (`middlewares/user_message.py`) is the abstraction for the bot's "active" message. **Always edit/replace via `user_message.edit(...)` / `user_message.new(...)`** instead of calling `message.edit_text` directly — it transparently falls back to send+delete when editing fails, and persists the new message ID into FSM state. `edit_login` / `new_login` are the canonical way to bounce a user back to the login keyboard when their session is invalid.
- **FSM strategy** is `GLOBAL_USER` with Redis storage and `with_destiny=True` keys, so a single user has one shared state across chats.

### i18n

Fluent (`.ftl`) catalogs in `locales/{en,kk,pl,ru,uk}/`. Always go through `i18n.get("key", ...)` — never hardcode user-facing strings. Adding a new key requires updating every locale directory.

### Time handling

The CDV portal is in Warsaw; timezone is configurable via `Config.timezone` (default `Europe/Warsaw`). Use `app.bot.utils.now_local()` / `today_local()` for any user-facing date logic — never `datetime.now()` / `date.today()` directly. (See commit `7175b62 Fix timezone bug` — this was a real footgun.)

## Code style preferences observed in this repo

Follow these when adding code so it stays consistent with what's already there:

- **Type-annotate aggressively, including local variables.** Existing code writes `dispatcher: Dispatcher = ...`, `coroutines: List[Coroutine] = [...]`, etc. Match that density.
- **Docstrings on every class, public method, and most private methods**, in the `:param:` / `:return:` / `:raises:` reST style. Module-level constants get a docstring on the line below.
- **Keyword-only arguments** for constructors with multiple optionals (`*,` separator), e.g. `DatabaseController.__init__`, `CDVController.__init__`.
- **`from_*` classmethods** as the conventional alternate constructor (`DatabaseController.from_dsn`, `ClassRecord.from_entry`, `ScheduleRecord.from_json`).
- Imports use full paths from `app.…` — no relative imports.
- `PEP 604` unions (`str | None`) over `Optional[str]`.
- aiogram handlers receive injected dependencies as kwargs (`schedule_controller`, `session_id`, `user_message`, `i18n`, `bot`, `state`); the dispatcher is constructed with these as workflow data and middlewares add the per-request ones. Don't reach for module-level singletons inside handlers.
- Windows-specific `SelectorEventLoop` setup is done in every entrypoint — copy that block when adding a new one.
- `# noqa` is used sparingly to silence intentional bare-except for cleanup paths in `AbstractSessionController` only.

## Deployment

`.github/workflows/deploy.yml` builds a Docker image to GHCR and SSH-pulls it on the server on `main*` tag pushes. Image is built from `Dockerfile` (Python 3.14-slim + Poetry main-only install, runs as `appuser`). The compose file on the server (not in this repo) is expected to set `BOT_IMAGE` and run all three processes (bot, ASGI, celery).
