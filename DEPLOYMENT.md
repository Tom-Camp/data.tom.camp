# Deployment

## Infrastructure

- **Host**: Linode 4GB (2 vCPU)
- **Database**: PostgreSQL running on the same host
- **Reverse proxy**: Nginx → Uvicorn (2 workers)
- **Container registry**: Docker Hub (`t0mc4mp/data.tom.camp`)
- **CI**: GitHub Actions builds and pushes the image on every push to `main`

---

## How startup works

The container entrypoint (`entrypoint.sh`) runs `alembic upgrade head` before Uvicorn starts. If migrations
fail, the container exits immediately — the app will never serve traffic against a stale schema.

---

## Environment variables

Copy `.env.example` to `prod.env` on the server. Required variables:


| Variable           | Description                                                            |
|--------------------|------------------------------------------------------------------------|
| `ADMIN_SECRET_KEY` | Protects admin endpoints (`X-Admin-Secret`)                            |
| `HASH_ALGORITHM`   | Hash algorithm for API keys (default: `blake2b`)                       |
| `HASH_SALT`        | Salt prepended before hashing API keys                                 |
| `POSTGRES_DB`      | Database name                                                          |
| `POSTGRES_HOST`    | Database host (use server LAN IP or `localhost` with `--network host`) |
| `POSTGRES_PORT`    | Database port (default: `5432`)                                        |
| `POSTGRES_USER`    | Database user                                                          |
| `POSTGRES_PASS`    | Database password                                                      |
| `ENVIRONMENT`      | Set to `production` to disable `create_all` on startup                 |
| `LOG_LEVEL`        | Log verbosity (default: `INFO`)                                        |
| `LOG_JSON_FORMAT`  | Set to `true` for structured JSON logs                                 |
| `CORS_ORIGINS`     | Comma-separated list of allowed origins                                |

---

## First-time deployment (fresh server)

```bash
# 1. Pull the latest image
docker compose -f docker-compose.prod.yml pull

# 2. Start the container
#    entrypoint.sh runs `alembic upgrade head` which creates all tables,
#    then starts Uvicorn
docker compose -f docker-compose.prod.yml up -d
```

---

## Routine deployment (existing server)

```bash
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

The container restarts automatically. Migrations run on startup — if there are no pending migrations,
`alembic upgrade head` is a no-op.

---

## One-time migration stamp (existing databases only)

If the database was created before Alembic was introduced (i.e. tables were created by `create_all` rather
than by running migrations), Alembic has no record of the schema being at the current revision. Running
`upgrade head` on such a database will fail because it tries to create tables that already exist.

Run this **once** to tell Alembic the database is already up to date:

```bash
docker compose -f docker-compose.prod.yml run --rm api \
  uv run alembic stamp head
```

After this, all future deployments will run migrations normally.

---

## Running migrations manually

```bash
# Apply all pending migrations
docker compose -f docker-compose.prod.yml run --rm api \
  uv run alembic upgrade head

# Check current revision
docker compose -f docker-compose.prod.yml run --rm api \
  uv run alembic current

# View migration history
docker compose -f docker-compose.prod.yml run --rm api \
  uv run alembic history
```

---

## Creating a new migration

After changing a model, generate a migration from the diff:

```bash
uv run alembic revision --autogenerate -m "describe the change"
```

Review the generated file in `alembic/versions/` before committing — autogenerate is not always complete,
particularly for server defaults, check constraints, and index changes.

---

## Local development

The `docker-compose.override.yml` is applied automatically alongside `docker-compose.yml`:

```bash
# Start app + PostgreSQL with hot reload
docker compose up -d

# Run tests (uses SQLite in-memory, no Docker required)
uv run pytest
```

---

## Nginx configuration

Nginx proxies requests from port 443 to the container on port 5000. Ensure `CORS_ORIGINS` in `prod.env`
includes any domains served through Nginx.

The `X-Request-ID` header is set on every response by the application middleware and can be forwarded or
logged by Nginx for request tracing.
