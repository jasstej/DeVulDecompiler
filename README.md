# DeVul

DeVul is a web frontend to multiple [decompilers](/runners/decompiler). It lets you compare outputs of different engines on small executables, side by side.

Project repo: https://github.com/jasstej/DeVulDecompiler


![Decompiler Explorer](/static/img/preview.png)

## Prerequisites

- python >= 3.8
- pipenv
- docker
- docker-compose


## Installation

```
pipenv install
python scripts/dce.py init
```


## Setting up decompilers
See the instructions [here](runners/decompiler/tools/README.md)

## Getting Started / Troubleshooting
See docs/GETTING_STARTED.md for quick start, restart, and common fixes.

## Quick Start

```zsh
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d explorer database memcached
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d angr snowman retdec ghidra
open http://127.0.0.1:8000
```

If explorer fails to serve, see docs/GETTING_STARTED.md for permissions fixes and full clean restart steps.

## Screenshots

Homepage with 3 panes (angr, Snowman, RetDec):

![3-pane](docs/img/homepage-3-pane.png)

Homepage with 4 panes (adds Ghidra):

![4-pane](docs/img/homepage-4-pane.png)

## Supported decompilers (OSS quick start)

- angr
- Snowman
- RetDec

Start open-source runners in dev:

```zsh
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d angr snowman retdec
```

Verify they’re registered:

```zsh
curl -fsS http://127.0.0.1:8000/api/decompilers/
```

### angr timeouts and scope

angr is computationally intensive. Large binaries may exceed default timeouts. Use Snowman or RetDec for faster decompilation. To give angr more time, increase its runner timeout:

```zsh
DECOMPILER_TIMEOUT_ANGR=300 DECOMPILER_EXTENDED_TIMEOUT_ANGR=1200 \
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d angr
```

You can also limit angr’s scope using environment variables passed to the angr container:

- `ANGR_FUNCTION_NAME`: decompile only a specific function name
- `ANGR_MAX_FUNCTIONS`: limit the number of functions analyzed

Example:

```zsh
ANGR_FUNCTION_NAME=main ANGR_MAX_FUNCTIONS=10 \
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d angr
```


## Running in docker (dev)

```shell
pipenv install
python scripts/dce.py init

# Build all decompilers with valid keys
python scripts/dce.py build
# If you want to exclude certain decompilers
# python scripts/dce.py --without-reko build

python scripts/dce.py start
# UI now accessible on port 80/443 (via Traefik)
```


## Running in docker (production)

```shell
python scripts/dce.py start --prod --replicas 2 --acme-email=<your email>
```


## Running in docker (production with s3 storage)

```shell
python scripts/dce.py start --prod --replicas 2 --acme-email=<your email> --s3 --s3-bucket=<s3 bucket name> --s3-endpoint=<s3 compatible endpoint> --s3-region=<s3 region>
```


## Starting dev server (outside Docker)

> This won't start any decompilers, just the frontend

```shell
pipenv run python manage.py migrate
pipenv run python manage.py runserver 0.0.0.0:8000
```


## Starting decompiler for dev server

```shell
export EXPLORER_URL=http://172.17.0.1:8000

docker-compose up binja --build --force-recreate --remove-orphans
```
