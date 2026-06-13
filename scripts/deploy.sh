#!/bin/bash
# deploy.sh — Personalizes config files with your username and deploys
# Run from the repo root: ./scripts/deploy.sh

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

ACTUAL_USER=$(whoami)
ACTUAL_HOME=$(eval echo ~$ACTUAL_USER)
REPO_PATH="$ACTUAL_HOME/rest-api-mastery"
SERVER_PATH="$REPO_PATH/server"
VENV_GUNICORN="$SERVER_PATH/venv/bin/gunicorn"

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════╗"
echo "║   REST API Mastery — Deployment Script    ║"
echo "╚═══════════════════════════════════════════╝"
echo -e "${NC}"

# ── Checks ────────────────────────────────────────────────────
echo -e "${YELLOW}[1/6] Checking prerequisites...${NC}"

if [ ! -f "$VENV_GUNICORN" ]; then
    echo -e "${RED}❌ Gunicorn not found at $VENV_GUNICORN${NC}"
    echo "   Run: cd server && source venv/bin/activate && pip install gunicorn"
    exit 1
fi
echo -e "${GREEN}✓ Gunicorn found: $VENV_GUNICORN${NC}"

if ! command -v systemctl &>/dev/null; then
    echo -e "${RED}❌ systemd not available on this system${NC}"
    exit 1
fi
echo -e "${GREEN}✓ systemd available${NC}"

# ── Patch gunicorn.conf.py ─────────────────────────────────────
echo -e "${YELLOW}[2/6] Patching gunicorn.conf.py with your username...${NC}"
sed -i "s|/home/YOUR_USERNAME|$ACTUAL_HOME|g" "$SERVER_PATH/gunicorn.conf.py"
echo -e "${GREEN}✓ gunicorn.conf.py updated: chdir = $SERVER_PATH${NC}"

# ── Patch .service file ───────────────────────────────────────
echo -e "${YELLOW}[3/6] Patching service file with your username...${NC}"
TEMP_SERVICE="/tmp/rest-api-mastery.service"
sed "s|YOUR_USERNAME|$ACTUAL_USER|g; s|/home/$ACTUAL_USER|$ACTUAL_HOME|g" \
    "$REPO_PATH/deploy/rest-api-mastery.service" > "$TEMP_SERVICE"
echo -e "${GREEN}✓ Service file patched${NC}"

# ── Copy to systemd ───────────────────────────────────────────
echo -e "${YELLOW}[4/6] Installing service file to /etc/systemd/system/...${NC}"
sudo cp "$TEMP_SERVICE" /etc/systemd/system/rest-api-mastery.service
sudo systemctl daemon-reload
echo -e "${GREEN}✓ Service file installed and daemon reloaded${NC}"

# ── Enable + Start ────────────────────────────────────────────
echo -e "${YELLOW}[5/6] Enabling service (start on boot)...${NC}"
sudo systemctl enable rest-api-mastery
echo -e "${GREEN}✓ Service enabled${NC}"

echo -e "${YELLOW}[6/6] Starting service...${NC}"
sudo systemctl restart rest-api-mastery
sleep 2

# ── Verify ────────────────────────────────────────────────────
if sudo systemctl is-active --quiet rest-api-mastery; then
    echo -e "${GREEN}✓ Service is running!${NC}"
else
    echo -e "${RED}❌ Service failed to start. Check logs:${NC}"
    echo "   sudo journalctl -u rest-api-mastery -n 30"
    exit 1
fi

# Health check
sleep 1
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health 2>/dev/null || echo "000")
if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✓ Health check passed (HTTP 200)${NC}"
else
    echo -e "${YELLOW}⚠️  Health check returned: $HTTP_STATUS (server may still be starting)${NC}"
fi

echo ""
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════╗"
echo "║       Deployment Complete! 🚀             ║"
echo "╚══════════════════════════════════════════╝"
echo -e "${NC}"
echo "Useful commands:"
echo -e "  ${BLUE}sudo systemctl status rest-api-mastery${NC}       ← is it running?"
echo -e "  ${BLUE}sudo journalctl -u rest-api-mastery -f${NC}       ← live logs"
echo -e "  ${BLUE}sudo systemctl restart rest-api-mastery${NC}      ← restart"
echo -e "  ${BLUE}curl http://localhost:5000/health${NC}             ← test it"
