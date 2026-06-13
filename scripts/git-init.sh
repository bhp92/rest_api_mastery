#!/bin/bash
# ============================================================
# git-init.sh — Initialize the repo and push to GitHub
# Run: chmod +x scripts/git-init.sh && ./scripts/git-init.sh
# ============================================================

set -e

YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Initializing REST API Mastery Git repo...${NC}"

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*.egg-info/
.eggs/
dist/
build/
*.egg

# Virtual environment
venv/
env/
.venv/

# Database
*.db
*.sqlite
*.sqlite3

# Environment variables
.env
.env.local
.env.*.local

# Uploads
server/uploads/

# Test/coverage
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF

echo -e "${GREEN}✓ .gitignore created${NC}"

# Init git
git init
git add .
git commit -m "🚀 Initial commit: REST API Mastery course"

echo ""
echo -e "${GREEN}✅ Git repo initialized!${NC}"
echo ""
echo -e "${YELLOW}Next steps to push to GitHub:${NC}"
echo ""
echo "  1. Create a new repo on GitHub: https://github.com/new"
echo "     Name it: rest-api-mastery"
echo "     Make it PUBLIC (so others can learn too!)"
echo ""
echo "  2. Connect and push:"
echo -e "     ${BLUE}git remote add origin https://github.com/YOUR_USERNAME/rest-api-mastery.git${NC}"
echo -e "     ${BLUE}git branch -M main${NC}"
echo -e "     ${BLUE}git push -u origin main${NC}"
echo ""
echo "  3. Share the repo URL and start studying! 🎓"
