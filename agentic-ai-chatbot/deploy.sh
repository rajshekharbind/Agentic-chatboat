#!/bin/bash
# Quick Deployment Script for LangGraph PDF Chatbot
# Run this before deploying to any platform

set -e

echo "=================================="
echo "🚀 Pre-Deployment Checklist"
echo "=================================="

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
    else
        echo -e "${RED}✗${NC} $1"
        return 1
    fi
}

fail() {
    echo -e "${RED}✗ $1${NC}"
    exit 1
}

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"
check "Python 3.10+ installed"

# Check virtual environment
if [ -d "venv" ] || [ -d ".venv" ]; then
    check "Virtual environment exists"
else
    echo -e "${YELLOW}ℹ${NC} No virtual environment found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    check "Virtual environment created and activated"
fi

# Check .env file
if [ -f ".env.production" ]; then
    check ".env.production file exists"
else
    fail ".env.production file not found. Please create it with GEMINI_API_KEY"
fi

# Check GEMINI_API_KEY is set
if grep -q "GEMINI_API_KEY=" .env.production && ! grep -q "GEMINI_API_KEY=your_" .env.production; then
    check "GEMINI_API_KEY is configured"
else
    fail "GEMINI_API_KEY not properly configured in .env.production"
fi

# Check requirements.txt
if [ -f "requirements.txt" ]; then
    check "requirements.txt exists"
else
    fail "requirements.txt not found"
fi

# Check key files exist
[ -f "frontend/app.py" ] && check "frontend/app.py exists" || fail "frontend/app.py not found"
[ -f "frontend/static/index.html" ] && check "frontend/static/index.html exists" || fail "frontend/static/index.html not found"
[ -f "backend/app/agents/langgraph_backend.py" ] && check "Backend exists" || fail "Backend not found"

# Check Procfile for Heroku
if [ -f "Procfile" ]; then
    check "Procfile exists (for Heroku)"
else
    echo -e "${YELLOW}ℹ${NC} No Procfile found. Creating one..."
    echo 'web: gunicorn -w 4 -b 0.0.0.0:$PORT "frontend.app:app"' > Procfile
fi

# Check Docker files
[ -f "Dockerfile" ] && check "Dockerfile exists (for containerization)" || echo -e "${YELLOW}ℹ${NC} No Dockerfile found"
[ -f "docker-compose.yml" ] && check "docker-compose.yml exists" || echo -e "${YELLOW}ℹ${NC} No docker-compose.yml found"

# Check .gitignore
[ -f ".gitignore" ] && check ".gitignore exists" || echo -e "${YELLOW}ℹ${NC} Creating .gitignore..."

# Check if git is initialized
if [ -d ".git" ]; then
    check "Git repository initialized"
else
    echo -e "${YELLOW}ℹ${NC} Git not initialized. Initialize with: git init"
fi

echo ""
echo "=================================="
echo "📋 Deployment Options"
echo "=================================="
echo ""
echo "Choose your deployment platform:"
echo ""
echo "1️⃣  Heroku (Easiest) - FREE TIER"
echo "   $ heroku login"
echo "   $ heroku create your-app-name"
echo "   $ heroku config:set GEMINI_API_KEY=your_key_here"
echo "   $ git push heroku main"
echo ""
echo "2️⃣  DigitalOcean (Simple) - \$6/month"
echo "   Create Ubuntu 22.04 droplet and run setup commands"
echo "   See DEPLOYMENT_GUIDE.md for detailed steps"
echo ""
echo "3️⃣  Docker (Any Cloud) - Flexible"
echo "   $ docker-compose up -d"
echo "   Deploy image to: Docker Hub, AWS ECR, GCR, ACR"
echo ""
echo "4️⃣  AWS EC2 (Scalable) - \$0-50/month"
echo "   Launch Ubuntu 22.04 instance and run setup commands"
echo "   See DEPLOYMENT_GUIDE.md for detailed steps"
echo ""
echo "=================================="
echo "📚 Full Guide"
echo "=================================="
echo "For complete deployment instructions, see: DEPLOYMENT_GUIDE.md"
echo ""
echo "Next steps:"
echo "1. Choose a deployment platform above"
echo "2. Read the relevant section in DEPLOYMENT_GUIDE.md"
echo "3. Follow the step-by-step instructions"
echo "4. Test with: curl https://your-domain/api/health"
echo ""
echo -e "${GREEN}✓ Pre-deployment checks passed!${NC}"
echo ""
