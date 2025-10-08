#!/usr/bin/env bash

set -Eeuo pipefail

# Go to repo root (this script is in scripts/)
cd -- "$(dirname "$0")/.."

COMPOSE_FILES=("-f" "docker-compose.yml" "-f" "docker-compose.dev.yml")

# Default runners: keep it fast; override with RUNNERS env (e.g., "angr snowman retdec")
RUNNERS_DEFAULT=(snowman retdec)
if [[ -n "${RUNNERS:-}" ]]; then
  # shellcheck disable=SC2206
  RUNNERS_LIST=(${RUNNERS})
else
  RUNNERS_LIST=("${RUNNERS_DEFAULT[@]}")
fi

echo "[live_local] Initializing secrets and data directories..."
python3 scripts/dce.py init

echo "[live_local] Starting core services (explorer, database, memcached) and runners: ${RUNNERS_LIST[*]}"
docker compose "${COMPOSE_FILES[@]}" up --build -d explorer database memcached "${RUNNERS_LIST[@]}" 2>&1 | sed 's/^/[docker] /'

echo "[live_local] Waiting for explorer on localhost:8000 to become ready..."
ATTEMPTS=0
until curl -fsS http://127.0.0.1:8000/api/decompilers/ >/dev/null 2>&1; do
  ATTEMPTS=$((ATTEMPTS+1))
  if [[ $ATTEMPTS -ge 60 ]]; then
    echo "[live_local] Timed out waiting for explorer. Check logs:"
    echo "  docker compose -f docker-compose.yml -f docker-compose.dev.yml logs --since=10m explorer"
    exit 1
  fi
  sleep 2
done

pick_lan_ip() {
  # Prefer non-loopback, non-docker, non-bridge IPv4 address
  # Works on most Linux distros
  while IFS= read -r line; do
    iface=$(awk '{print $2}' <<<"$line")
    cidr=$(awk '{print $4}' <<<"$line")
    ip=${cidr%/*}
    case "$iface" in
      lo|docker*|br-*|veth*|tun*|tap*) continue ;;
    esac
    [[ "$ip" == 127.* ]] && continue
    echo "$ip"
    return 0
  done < <(ip -o -4 addr show up scope global)

  # Fallbacks
  if command -v hostname >/dev/null 2>&1; then
    for ip in $(hostname -I 2>/dev/null || true); do
      [[ "$ip" == 127.* ]] && continue
      echo "$ip"; return 0
    done
  fi
  echo "127.0.0.1"
}

LAN_IP=$(pick_lan_ip)

cat <<EOF

==============================================
DeVul is live on your local network

  URL:  http://${LAN_IP}:8000

Open this from any device on the same LAN.

Next steps:
- Add more runners (heavier):
    RUNNERS="angr snowman retdec" bash scripts/live_local.sh
- View admin creation info in logs:
    docker compose -f docker-compose.yml -f docker-compose.dev.yml logs --since=10m explorer | sed -n '/Successfully created admin user/,+4p'
- Stop stack:
    docker compose -f docker-compose.yml -f docker-compose.dev.yml down
==============================================
EOF

exit 0
