# Troubleshooting

## Backend

**`BOOTSTRAP ADMIN API KEY` not shown** — it prints only on first start of an
empty database. Delete the SQLite file to re-bootstrap, or set
`AEGISTRACE_BOOTSTRAP_KEY`.

**`401 invalid or revoked API key`** — keys are hashed at rest and unrecoverable;
create a new one (`POST /api/v1/auth/keys`, admin role) or reuse the bootstrap key.

**`429 rate limit exceeded`** — per-key token bucket (600/min default, in-process).

**Database locked / migration drift** — dev uses `create_all`; for schema
changes run `cd backend && alembic upgrade head`. Never hand-edit the SQLite file.

**Signing key errors** — `AEGISTRACE_SIGNING_KEY_PATH` must contain an Ed25519
PEM; the file is created automatically if missing. Losing it invalidates
verification of old certificates (document in deployment notes).

## SDK

**Events not arriving** — check `client.pending()`; transport failures requeue
locally. Executions without delivered events stay UNKNOWN server-side.

**`RuntimeError: aegistrace.init() was not called`** — call `init()` before `@trace`.

**422 `unknown execution`** — steps must follow their `execution.started`;
batch events in order.

## Frontend

**"Backend unreachable" banner** — the console talks to `AEGISTRACE_API_URL`
(default `http://127.0.0.1:8420`); start the backend first, then reload.

**Login rejects a valid-looking key** — keys start with `at_`; verify with
`curl -X POST localhost:8420/api/v1/auth/verify -H "X-API-Key: ..."`.

**Port 3000/8420 in use (Windows)** — `netstat -ano | findstr :3000` then
`taskkill /F /PID <pid>`; stale node/uvicorn processes survive shell exits.

## Benchmarks

**AttackBench regression (recall < 1.0)** — a new baseline/ingest change broke
a detection contract; see `docs/benchmarks/attackbench-results.json` scenario
rows for the missed fixture, fix the engine, never the fixture.
