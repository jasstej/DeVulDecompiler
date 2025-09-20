# DeVul — Getting Started

This guide shows how to set up, start, restart, and troubleshoot DeVul locally using Docker Compose.

## Prerequisites
- Docker and Docker Compose plugin installed
- Internet access for image builds

## One-time initialization
```zsh
# From the repo root
pipenv install
python scripts/dce.py init
```
This creates required secrets and local data folders.

## Start the stack (dev)
Start core services and open-source runners:
```zsh
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d explorer database memcached
# Start runners (pick any)
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
- After changes, restart explorer:
```zsh
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart explorer
```

## Where to look
- Explorer logs: `docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f explorer`
- Runner logs: `docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f <runner>`
- API endpoints: `/api/`, `/api/decompilers/`, `/api/binaries/`

