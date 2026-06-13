#!/bin/bash
# ============================================================
# REST API Mastery — One-shot VM Setup Script
# Run: chmod +x scripts/setup.sh && ./scripts/setup.sh
# ============================================================

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════╗"
echo "║   REST API Mastery — Environment Setup   ║"
echo "╚══════════════════════════════════════════╝"
echo -e "${NC}"

# ── Check Python ──────────────────────────────────────────────
echo -e "${YELLOW}[1/6] Checking Python...${NC}"
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}Python3 not found. Installing...${NC}"
    sudo apt-get update -qq && sudo apt-get install -y python3 python3-pip python3-venv
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓ $PYTHON_VERSION found${NC}"

# ── Check Git ─────────────────────────────────────────────────
echo -e "${YELLOW}[2/6] Checking Git...${NC}"
if ! command -v git &>/dev/null; then
    sudo apt-get install -y git
fi
echo -e "${GREEN}✓ Git $(git --version | awk '{print $3}') found${NC}"

# ── Create virtualenv ─────────────────────────────────────────
echo -e "${YELLOW}[3/6] Creating virtual environment...${NC}"
cd server
python3 -m venv venv
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment created${NC}"

# ── Install dependencies ──────────────────────────────────────
echo -e "${YELLOW}[4/6] Installing server dependencies...${NC}"
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo -e "${GREEN}✓ Server dependencies installed${NC}"

# ── Install test/exercise dependencies ───────────────────────
echo -e "${YELLOW}[5/6] Installing study dependencies...${NC}"
pip install --quiet pytest pytest-cov httpx faker requests pydantic
echo -e "${GREEN}✓ Study dependencies installed${NC}"

# ── Seed the database ─────────────────────────────────────────
echo -e "${YELLOW}[6/6] Seeding practice database...${NC}"
python seed.py
echo -e "${GREEN}✓ Database seeded with practice data${NC}"

cd ..

echo ""
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════╗"
echo "║          Setup Complete! 🎉               ║"
echo "╚══════════════════════════════════════════╝"
echo -e "${NC}"
echo -e "Next steps:"
echo -e "  ${BLUE}1. Start the server:${NC}  cd server && source venv/bin/activate && python app.py"
echo -e "  ${BLUE}2. Test it works:${NC}     curl http://localhost:5000/health"
echo -e "  ${BLUE}3. Begin studying:${NC}    open course/week-01-foundations/README.md"
echo ""
echo -e "${YELLOW}Happy learning! 🚀${NC}"
