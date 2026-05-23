#!/bin/bash
# Deploy to Heroku - Quick Script
# Usage: ./deploy-heroku.sh your-app-name

if [ -z "$1" ]; then
    echo "Usage: ./deploy-heroku.sh your-app-name"
    echo "Example: ./deploy-heroku.sh langgraph-pdf-chatbot"
    exit 1
fi

APP_NAME=$1

echo "🚀 Deploying to Heroku: $APP_NAME"
echo ""

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found. Install from: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Login to Heroku
echo "1️⃣  Logging in to Heroku..."
heroku login

# Create app
echo "2️⃣  Creating Heroku app..."
heroku create $APP_NAME

# Set environment variables
echo "3️⃣  Setting environment variables..."
echo "Enter your GEMINI_API_KEY (it will be hidden):"
read -s GEMINI_KEY
heroku config:set GEMINI_API_KEY=$GEMINI_KEY --app $APP_NAME
heroku config:set FLASK_ENV=production --app $APP_NAME
heroku config:set SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))") --app $APP_NAME

# Initialize git if needed
if [ ! -d ".git" ]; then
    echo "4️⃣  Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit for Heroku deployment"
fi

# Add Heroku remote
echo "5️⃣  Adding Heroku remote..."
heroku git:remote -a $APP_NAME

# Deploy
echo "6️⃣  Deploying to Heroku..."
git push heroku main 2>/dev/null || git push heroku master

# View logs
echo ""
echo "✅ Deployment initiated!"
echo ""
echo "📊 View logs:"
echo "   heroku logs --tail --app $APP_NAME"
echo ""
echo "🌐 Open app:"
echo "   heroku open --app $APP_NAME"
echo ""
