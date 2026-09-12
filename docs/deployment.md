# Deployment

## Option A — Docker Compose (recommended for evaluation)

```bash
cd deploy
export POSTGRES_PASSWORD=$(openssl rand -hex 16)
export AEGISTRACE_BOOTSTRAP_KEY=at_$(openssl rand -hex 24)
docker compose up --build
```

- Backend: http://localhost:8420 (OpenAPI at /docs)
- Console: http://localhost:3000
- The admin API key is the `AEGISTRACE_BOOTSTRAP_KEY` you set — sign in with it.

Status: **compose stack not yet run end-to-end on the dev machine** (Docker
daemon unavailable during the build session) — treat as UNVERIFIED until a run
passes; individual Dockerfiles follow the standard patterns for their stacks.

## Option B — Local processes

Backend (SQLite by default; set `DATABASE_URL` for PostgreSQL):

```bash
python -m venv .venv && source .venv/Scripts/activate   # Windows Git Bash
pip install -e ./backend -e ./sdk
export AEGISTRACE_BOOTSTRAP_KEY=at_...        # or let it print a random one
uvicorn backend.app.main:app --port 8420
```

Frontend:

```bash
cd frontend && npm install && npm run build && npm start   # :3000
```

## Configuration (env, prefix AEGISTRACE_)

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///backend/data/aegistrace.db` | PostgreSQL: `postgresql+psycopg://user:pass@host/db` |
| `SIGNING_KEY_PATH` | `backend/keys/at_ed25519.pem` | Ed25519 private key (created 0600 on first start) |
| `BOOTSTRAP_KEY` | random (printed once) | first admin API key |
| `ALLOW_CONTENT` | `false` | permit raw content events (keep false) |
| `RATE_LIMIT_PER_MINUTE` | `600` | per-key token bucket |
| `CORS_ORIGINS` | localhost:3000 | allowed browser origins |
| `RETENTION_DAYS` | 365 | documented retention target |

## Migrations

Alembic manages the schema: `cd backend && alembic upgrade head`.
The API also runs `create_all` on startup for dev convenience — production must
use migrations (the initial migration is verified drift-free against the models).

## Operational notes

- Health: `/healthz`, `/readyz`; counters: `/metrics`.
- Back up `backend/keys/` (signing key) and the database together; the key
  verifies all historical certificates.
- Rotate keys by generating a new key and updating `AEGISTRACE_` config;
  verification accepts the configured key only in v1 (multi-key ring: future).
