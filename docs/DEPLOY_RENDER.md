# Deploy to Render

This repo includes a `render.yaml` so you can spin up a hosted instance on Render in minutes.

## What you get
- Web service running Django + Gunicorn in Docker
- Managed Postgres database (Render)
- Private Memcached service for caching
- Automated migrations and collectstatic executed by the container entrypoint

## One‑time setup
1. Push this repository to GitHub (private or public).
2. On Render, click New → Blueprint and point to your repo.
3. Review resources from `render.yaml`:
   - Web service: `decompiler-explorer`
   - Database: `dce-postgres`
   - Private service: `dce-memcached`
4. Create the Blueprint. Render will provision infra and start your first deploy.

## Configuration
The web service uses these environment variables (set automatically by the blueprint unless noted):
- DJANGO_SETTINGS_MODULE=decompiler_explorer.settings.docker
- PORT=8000 (Render provides `PORT` automatically too)
- DATABASE_URL (wired from the managed Postgres)
- MEMCACHED_HOST (wired from `dce-memcached`)
- MEMCACHED_PORT=11211
- SECRET_KEY (auto-generated)
- WORKER_AUTH_TOKEN (auto-generated)
- ALLOWED_HOSTS (default `*`; set to your Render hostname for stricter security)
- DJANGO_DEBUG=False

Optional for S3-compatible storage (recommended for large media):
- DJANGO_FILE_STORAGE=storages.backends.s3boto3.S3Boto3Storage
- AWS_STORAGE_BUCKET_NAME=your-bucket
- AWS_S3_ENDPOINT_URL=https://s3.your-provider.tld
- AWS_S3_REGION_NAME=us-east-1
- (Optionally) provide `s3_access_key_id` and `s3_secret_access_key` via secrets or env.

## Deploy flow
- Build uses the repo `Dockerfile`.
- On container start, `entrypoint.sh` will:
  - run Django system checks with retries
  - run `manage.py migrate`
  - run `manage.py collectstatic --noinput`
  - ensure an admin account exists
  - start Gunicorn and listen on `$PORT`

## Notes on decompiler runners
This blueprint deploys only the web app, DB, and cache. The heavy decompiler runner containers (angr, Snowman, RetDec, etc.) are not included by default as they are CPU/memory intensive on PaaS.

Options:
- Minimal: Keep only the web app; upload small binaries and use lighter backends.
- Add runners: Create additional Private Services for specific runners and wire their URLs + auth into the app (future enhancement). You can start with Snowman/RetDec if desired.
- External workers: Run runners on separate machines/VMs and connect over private networking with the `X-Auth-Token` header.

## Troubleshooting
- Health check: We use `/api/decompilers/` which is public; if it fails, open Logs to see Django startup errors.
- Database errors: Ensure `DATABASE_URL` is present (Render wires it automatically).
- Static files: If you see missing assets, confirm `collectstatic` postdeploy step succeeded. For large static/media, consider S3.
- Worker API calls returning 403: Set WORKER_AUTH_TOKEN in both the web service and the workers, and ensure requests include the `X-Auth-Token` header.

## Next steps
- Lock down `ALLOWED_HOSTS` to your exact Render domain.
- Add a CDN for static/media if traffic grows.
- Add monitoring and error reporting (Sentry) as needed.
