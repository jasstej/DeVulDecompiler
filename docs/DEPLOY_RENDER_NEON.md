# Deploy to Render with Neon (no card)

This guide deploys only a single Render Web Service (Docker) and uses a free external Neon Postgres. No Blueprint or credit card required.

## 1) Create a Neon Postgres database
1. Go to https://neon.tech and create a free account/project.
2. Create a database and copy the connection string (DATABASE_URL). It looks like:
   `postgresql://USER:PASSWORD@HOST:PORT/DB?sslmode=require`

## 2) Prepare repository (already set)
- Dockerfile runs Gunicorn and now binds to `$PORT` with a default of 8000.
- `entrypoint.sh` runs migrations and collectstatic automatically at container start.
- Settings read DATABASE_URL, SECRET_KEY, ALLOWED_HOSTS, etc. from env.

## 3) Create a Render Web Service
1. In Render, click New → Web Service.
2. Connect your GitHub repo.
3. Environment: Docker.
4. Root directory: repository root (where `decompiler-explorer/Dockerfile` exists). If Render asks for Dockerfile path, set `decompiler-explorer/Dockerfile`.
5. Set Environment Variables:
   - DJANGO_SETTINGS_MODULE = decompiler_explorer.settings.docker
   - SECRET_KEY = generate-a-random-long-string
   - WORKER_AUTH_TOKEN = generate-a-random-long-string (used if you add remote workers)
   - DJANGO_DEBUG = False
   - ALLOWED_HOSTS = your-service.onrender.com
   - DATABASE_URL = paste the Neon connection string
   - (optional) DJANGO_FILE_STORAGE, AWS_* for S3 if you want persistent media

You do NOT need MEMCACHED_HOST/PORT — the app will fall back to in-memory cache.

## 4) First deploy
Render will build your Docker image and start the container. On boot, the entrypoint will:
- run Django system checks with retries
- run `manage.py migrate`
- run `manage.py collectstatic --noinput`
- ensure an admin account exists
- start Gunicorn on `$PORT`

Visit the Render URL and verify `/api/decompilers/` returns data.

## 5) Notes and tips
- Static and media: Local disk on PaaS is ephemeral. For anything beyond a demo, set up S3.
- Admin user: The entrypoint ensures admin; check logs for the auto-created credentials or set your own via environment or a management command.
- Logs: Use Render’s Logs to diagnose startup issues (DB connectivity, migrations, etc.).
- Scaling: Keep the free/low-tier instance; runners are not deployed in this path.

## 6) Optional: Add HTTPS custom domain
- You can later add a custom domain in Render. Update `ALLOWED_HOSTS` accordingly.
