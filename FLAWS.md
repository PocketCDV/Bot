# FLAWS.md

A focused audit of the `app/` package after the recent refactor. Only verified, high-leverage findings — style, formatting, missing tests, and docstring nits are intentionally omitted.

Each entry: file:line — problem — suggested fix.

---

## CRITICAL — broken Python; will raise on first execution

### 1. `app/assets/controllers/cdv.py:81` — invalid `except` syntax

```python
except TypeError | ValueError:
    return None
```

`A | B` does not produce an exception group / tuple in an `except` clause. At runtime, when the inner block raises, Python evaluates `TypeError | ValueError` and tries to use the resulting `types.UnionType` as the caught class, which raises:

```
TypeError: catching classes that do not inherit from BaseException is not allowed
```

**Fix:** `except (TypeError, ValueError):`

### 2. `app/asgi/api/v1/auth/router.py:88` — same `except` bug on the login path

```python
except ClientConnectionError | asyncio.TimeoutError:
    raise ServerUnavailableError(...)
```

Login will return a confusing 500 (instead of `ServerUnavailableError`) every time WU times out or drops the connection.

**Fix:** `except (ClientConnectionError, asyncio.TimeoutError):`

### 3. `app/celery/crons.py:123` — variable shadowing kills the cron after one user

```python
schedule: ScheduleController = ScheduleController(cdv, database)  # line 91
...
async for user in users:
    ...
    schedule: ScheduleDayRecord = await schedule.get_home_schedule(session_id)  # line 123
```

The local rebind clobbers the controller. Iteration #2 calls `ScheduleDayRecord.get_home_schedule` and dies with `AttributeError`. The home-page-refresh cron only ever updates one user before crashing.

**Fix:** rename the local, e.g. `schedule_data: ScheduleDayRecord = await schedule.get_home_schedule(...)`, and use `schedule_data` in the branches below.

### 4. `app/celery/crons.py:43-46` and `87-90` — `CDVController` constructed with wrong type

```python
cdv: CDVController = CDVController(
    config.api_url,                       # str
    ssl_context=create_default_context(...),
)
```

`CDVController.__init__` expects `client: ClientController` (see `app/assets/controllers/cdv.py:18-23`). Both Celery tasks crash on the first request to `self._client.session()`. The ASGI lifespan does this correctly (`app/asgi/__init__.py:33-39`) — mirror that pattern:

```python
client = ClientController(base_url=config.api_url)
cdv = CDVController(client, ssl_context=create_default_context(cafile=where()))
```

### 5. `app/assets/controllers/cdv.py:57` and `:78` — `.value` on possibly-`None` cookie

```python
return response.cookies.get("WU_PHPSESSID").value
```

If WU omits the cookie (invalid creds, server hiccup, redirect quirk), `.get(...)` returns `None` and this raises `AttributeError`. Both `get_session_id` and `refresh_session_id` are documented to return `str | None`, so the contract is already there — implementation just doesn't honor it.

**Fix:**
```python
cookie = response.cookies.get("WU_PHPSESSID")
return cookie.value if cookie else None
```

---

## HIGH — security / correctness / resource leaks

### 6. `app/celery/crons.py:68-69` — silently overwriting a valid session with `None`

```python
new_session_id: str = await cdv.refresh_session_id(session_id)
await state.update_data(session_id=new_session_id)
```

`refresh_session_id` returns `None` whenever the call fails. This unconditionally writes that `None` back into FSM state, so the next request on the bot side will see no session and force the user to re-login — even after a single transient WU error.

**Fix:** only update on success:
```python
if (new_session_id := await cdv.refresh_session_id(session_id)) is not None:
    await state.update_data(session_id=new_session_id)
```

### 7. `app/asgi/__init__.py:56-61` — wide-open CORS on a credentials-handling API

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

The `/auth/login` endpoint accepts the user's WU email + password in plaintext. Any origin can issue cross-site requests; combined with no CSRF protection, this is an obvious cred-grabbing risk if a victim ever lands on a malicious page.

**Fix:** restrict `allow_origins` to the bot's WebApp origin (whatever you serve the login page from) and `allow_methods=["POST"]`.

### 8. `app/asgi/limiter.py:10-13` — `X-Forwarded-For` trusted unconditionally → rate-limit bypass

```python
forwarded_for = request.headers.get("X-Forwarded-For")
if forwarded_for:
    return forwarded_for.split(",")[0].strip()
```

Any client can set this header. The `5/minute` limit on `/auth/login` is bypassable by rotating the header value per request → unlimited credential-stuffing.

**Fix:** only honor the header when the request actually came through a trusted reverse proxy. In practice: drop this function and rely on `request.client.host` plus uvicorn's `--forwarded-allow-ips` (or starlette's `ProxyHeadersMiddleware`) so the proxy hop is what rewrites `client.host`.

### 9. `app/asgi/api/v1/auth/router.py:105-109` — new `Bot` per request, never closed

```python
state: FSMContext = get_state(
    redis,
    Bot(token=config.telegram_bot_token.get_secret_value()),
    user.telegram_id,
)
```

Each `Bot(...)` opens its own aiohttp client session. None of them are closed. Under steady login traffic this leaks file descriptors and aiohttp connector instances until the process is restarted.

**Fix:** stash a single `Bot` on `app.state` in `lifespan` (alongside `cdv`/`redis`) and inject it via a dependency, exactly like the other resources.

### 10. `app/asgi/__init__.py:47-49` — DB engine never disposed on shutdown

```python
yield
await redis.close()
```

Redis is closed but the SQLAlchemy `AsyncEngine` created by `DatabaseController.from_dsn` is left dangling — connections in the pool are never returned to PG cleanly on shutdown.

**Fix:** add a `close()` method to `DatabaseController` that calls `await self._engine.dispose()`, and call it after Redis.

---

## MEDIUM — easy wins / smaller correctness issues

### 11. `app/assets/controllers/session.py:70-81` — TOCTOU race in `_ensure_session`

The `if self._session is not None and await self._validate_session()` check happens **outside** the lock. Two coroutines can both fail validation, both acquire the lock in sequence, and the second one closes the session that the first just created. Under contention this thrashes sessions and breaks any consumer that's mid-request on the just-closed session.

**Fix:** re-check `_validate_session()` inside the lock before deciding to recreate.

### 12. `app/asgi/api/v1/auth/router.py:100-109` — unguarded `User | None` deref

```python
user: User | None = await database_session.scalar(...)
state: FSMContext = get_state(redis, Bot(...), user.telegram_id)
```

In practice the row is always there (we just inserted with `on_conflict_do_nothing`), but the type annotation is honest and a future change could make it really return `None`. One-liner guard is cheap insurance.

**Fix:** `if user is None: raise InvalidCredentialsError(...)` immediately after the `select`. (And drop the redundant select altogether: use `RETURNING` on the insert, or just trust `telegram_init_data.user.id`.)

### 13. `app/asgi/api/v1/auth/router.py:112-116` — pointless `asyncio.to_thread` around `.delay`

```python
await asyncio.to_thread(
    set_successful_login_message.delay,
    telegram_id=user.telegram_id,
    locale=user.locale,
)
```

`Celery.Task.delay` is a thin RPC to the broker — non-blocking enough to call directly from async code. Wrapping it in `to_thread` adds a thread-pool hop for no reason.

**Fix:** `set_successful_login_message.delay(telegram_id=..., locale=...)`.

### 14. `app/asgi/api/v1/auth/router.py:85-87` — PII logged at INFO on every login

```python
logger.info(f"User {telegram_init_data.user.id} logged in successfully.")
```

Every successful login writes a Telegram user ID into the application log. Depending on where logs are shipped this is mild PII leakage. Either drop it, lower to `debug`, or hash the ID.

---

## Out of scope / intentionally not flagged

- `app/assets/controllers/session.py:77,92` — bare `except Exception: pass` around `_close_session` is defensible during cleanup; not worth churning.
- `app/bot/middlewares/user_message.py` — looked OK; aiogram guarantees `state` and `bot` are present in `data` for the events this middleware sees.
- Docstrings, type hints, formatting, test coverage — explicitly out of scope.
