#!/usr/bin/env bash
# GreenWeave — one-command demo launcher (Linux/Mac)
# Checks Docker, resets containers cleanly, rebuilds, and waits for a
# healthy elastic_router before handing control back to the presenter.

set -euo pipefail

BLUE='\033[0;34m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
info()  { echo -e "${BLUE}[GreenWeave]${NC} $1"; }
ok()    { echo -e "${GREEN}[GreenWeave]${NC} $1"; }
warn()  { echo -e "${YELLOW}[GreenWeave]${NC} $1"; }
fail()  { echo -e "${RED}[GreenWeave]${NC} $1"; exit 1; }

cd "$(dirname "$0")"

# ── 1. Docker present & running ────────────────────────────────────
command -v docker >/dev/null 2>&1 || fail "Docker is not installed. Install Docker Desktop and try again."
docker info >/dev/null 2>&1 || fail "Docker is installed but not running. Start Docker Desktop and try again."

if docker compose version >/dev/null 2>&1; then
    COMPOSE="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE="docker-compose"
else
    fail "Neither 'docker compose' nor 'docker-compose' was found."
fi
ok "Docker is running (using: $COMPOSE)"

# ── 2. .env check ───────────────────────────────────────────────────
if [ ! -f .env ]; then
    warn ".env not found — copying .env.example. Edit .env and add your API keys before routing real traffic."
    cp .env.example .env
fi

# ── 3. Clean restart ─────────────────────────────────────────────────
info "Stopping any existing GreenWeave containers..."
$COMPOSE down --remove-orphans

info "Building and starting the stack (this can take a few minutes on first run)..."
$COMPOSE up --build -d

# ── 4. Health check ──────────────────────────────────────────────────
info "Waiting for the Elastic Router to become healthy..."
ATTEMPTS=30
for i in $(seq 1 $ATTEMPTS); do
    if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
        ok "Elastic Router is healthy!"
        break
    fi
    if [ "$i" -eq "$ATTEMPTS" ]; then
        warn "Elastic Router did not report healthy after $((ATTEMPTS*3))s."
        warn "Check logs with: $COMPOSE logs elastic_router"
    fi
    sleep 3
done

echo ""
ok "GreenWeave is up:"
echo "    Dashboard:      http://localhost:8501"
echo "    Elastic Router: http://localhost:8000/health"
echo "    Redis:          localhost:6379"
echo ""
info "Tail logs with: $COMPOSE logs -f"
info "Stop the stack with: $COMPOSE down"
