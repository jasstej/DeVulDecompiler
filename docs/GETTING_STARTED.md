# DeVul — Getting Started

This guide shows how to set up, start, restart, and troubleshoot DeVul locally using Docker Compose.

## Prerequisites
- Docker and Docker Compose plugin installed
- Internet access for image builds
- Python 3.10+ and Pipenv (only if running the helper script on the host). Otherwise use the Docker-only init below.

## One-time initialization
From the repo root, pick ONE of the following:

Option A — Host (Pipenv):
```zsh
pipenv install
pipenv run python scripts/dce.py init
```

Option B — Docker-only (no Pipenv on host):
```zsh
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm explorer python scripts/dce.py init
```

## Start the stack (dev)
Start core services:
```zsh
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d explorer database memcached
```

Start runners (pick any subset; see docker-compose.dev.yml for all available service names):
```zsh
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d angr snowman retdec ghidra
```

Visit http://127.0.0.1:8000

Admin login (auto-created on first boot) shows in explorer service logs:
```zsh
docker compose -f docker-compose.yml -f docker-compose.dev.yml logs --since=10m explorer | sed -n '/Successfully created admin user/,+4p'
```

## Verify decompilers
```zsh
curl -fsS http://127.0.0.1:8000/api/decompilers/
```

## Restart workflow
1) Restart only explorer (template/static changes):
```zsh
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart explorer
```

2) Rebuild a runner after code change (e.g., angr):
```zsh
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d angr
```

3) Full clean restart (fix weird state):
```zsh
# Stop and remove containers + volumes
docker compose -f docker-compose.yml -f docker-compose.dev.yml down -v
# Clear caches on host (optional)
rm -rf staticfiles media/__pycache__
find . -type d -name '__pycache__' -prune -exec rm -rf {} +
find . -name '*.pyc' -delete
# Start core and runners again
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d explorer database memcached
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d angr snowman retdec ghidra
```

## Common issues & fixes
- Port 8000 not responding:
  - Ensure explorer is running:
    ```zsh
    docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
    docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d explorer
    ```

- PermissionError during collectstatic (staticfiles):
  - Fix host dir perms:
    ```zsh
    sudo chown -R $(id -u):$(id -g) staticfiles media
    sudo chmod -R u+rwX,g+rwX staticfiles media
    docker compose -f docker-compose.yml -f docker-compose.dev.yml restart explorer
    ```

- Runners not appearing in UI:
  - Check API:
    ```zsh
    curl -fsS http://127.0.0.1:8000/api/decompilers/
    ```
  - Tail runner logs (replace service name):
    ```zsh
    docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f angr
    ```

- angr timeouts on large binaries:
  - Increase angr runner timeout:
    ```zsh
    DECOMPILER_TIMEOUT_ANGR=300 DECOMPILER_EXTENDED_TIMEOUT_ANGR=1200 \
    docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d angr
    ```
  - Limit scope:
    ```zsh
    ANGR_FUNCTION_NAME=main ANGR_MAX_FUNCTIONS=10 \
    docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d angr
    ```

## Updating static/branding
- Static assets are under `static/`; templates under `templates/`.
- After changes, restart explorer and hard-refresh the browser:
```zsh
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart explorer
```

## Where to look
- Explorer logs: `docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f explorer`
- Runner logs: `docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f <runner>`
- API endpoints: `/api/`, `/api/decompilers/`, `/api/binaries/`

## One-click local live (access from same network)

If you want the app reachable from other devices on your LAN without a domain, use:

```zsh
bash scripts/live_local.sh
```

This starts the dev stack and prints a URL like `http://192.168.1.42:8000` you can open from phones/laptops on the same Wi‑Fi. Set custom runners:

```zsh
RUNNERS="angr snowman retdec" bash scripts/live_local.sh
```