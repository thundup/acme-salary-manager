# Deployment

Two supported targets. Both use the same code; only configuration differs.

| Target | What runs where | Data |
|---|---|---|
| **Vercel (live demo: [UI](https://acme-salary-manager-2kmr.vercel.app), [API](https://acme-salary-manager-rosy.vercel.app/docs))** | UI = static site · API = FastAPI as a Python serverless function · DB = Neon Postgres | Persistent |
| **Docker (anywhere)** | One image: FastAPI serves the API *and* the built UI · SQLite in `/data` | Seeded on start, persistent only if `/data` is a volume |

Configuration is environment variables only:

| Variable | Default | Meaning |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./acme.db` | Any SQLAlchemy URL. `postgres://` / `postgresql://` URLs from hosting providers are rewritten to the `psycopg` driver automatically |
| `STATIC_DIR` | unset | Folder with the built UI. When set, FastAPI serves it and falls back to `index.html` for client-side routes |

## Vercel + Neon (free Hobby plan, no card)

Two Vercel projects from the same GitHub repo. The UI project rewrites `/api/*` to the API
project, so the browser only ever talks to one origin (no CORS).

### 1. API project
1. vercel.com → **Add New… → Project** → import `thundup/acme-salary-manager`.
2. **Project name:** `acme-salary-manager-api` · **Root Directory:** `backend` ·
   Framework preset: **FastAPI** (auto-detected from `backend/index.py`). Deploy.
3. In the project → **Storage → Create Database → Neon (Postgres)** → connect it to this
   project. This adds `DATABASE_URL` to the project's environment variables.
4. **Deployments → ⋯ → Redeploy** so the function picks up `DATABASE_URL`.

### 2. Create the schema and seed data (once, from your machine)
Copy the Neon connection string (project → Storage → your database → `.env.local` tab), then in
**your own terminal**:

```sh
cd backend
DATABASE_URL='postgresql://…neon.tech/neondb?sslmode=require' uv run alembic upgrade head
DATABASE_URL='postgresql://…neon.tech/neondb?sslmode=require' uv run python -m app.seed
```

Both commands are idempotent, so re-running them is safe. Check:
`https://acme-salary-manager-rosy.vercel.app/api/health` → `{"status":"ok","database":"ok"}`.

### 3. UI project
1. **Add New… → Project** → the same repo again.
2. **Project name:** any free name (Vercel names are global; this deployment got
   `acme-salary-manager-2kmr.vercel.app`) · **Root Directory:** `frontend` · Framework:
   **Vite** (auto-detected). Deploy.
3. `frontend/vercel.json` rewrites `/api/*` to `https://acme-salary-manager-rosy.vercel.app`.
   If Vercel gave the API project a different domain, update that one line and push.

Every push to `main` redeploys both projects. **Schema changes need step 2 re-run** before or
right after the deploy, because migrations are not run inside the serverless function.

### Limitations of the free setup
- Serverless cold starts add ~1–2 s to the first request after idle.
- The Neon free tier suspends the database when idle; the first query after that takes ~1 s.
- The demo is open (no auth, see REQUIREMENTS) and holds synthetic data only.

## Docker

```sh
docker build -t acme-salary-manager .
docker run -p 8000:8000 -v acme-data:/data acme-salary-manager
# open http://localhost:8000
```

On start the container runs `alembic upgrade head`, the idempotent seed, then `uvicorn`.
To use Postgres instead of SQLite, pass `-e DATABASE_URL=postgresql://…`. Any host that runs
a Dockerfile (Render, Fly.io, Railway, a VM) can deploy it as-is; set `PORT` if the host requires it.
CI builds this image and smoke-tests it on every push (`docker` job).
