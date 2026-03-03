#!/bin/bash

# BLE Tracker - Quick Setup Script
# This script creates the initial project structure

set -e  # Exit on error

echo "🚀 BLE Tracker - Project Setup"
echo "================================"
echo ""

# Create main project directory
PROJECT_NAME="ble-tracker"
echo "📁 Creating project structure..."

# Create directories
mkdir -p $PROJECT_NAME/{backend,admin-dashboard,customer-dashboard,mobile-app,nginx,scripts}
mkdir -p $PROJECT_NAME/backend/{app,tests,alembic}
mkdir -p $PROJECT_NAME/backend/app/{api,core,db,models,schemas,services}
mkdir -p $PROJECT_NAME/backend/app/api/{v1,deps}
mkdir -p $PROJECT_NAME/backend/app/api/v1/endpoints

cd $PROJECT_NAME

echo "✅ Directory structure created"

# Initialize git
echo ""
echo "🔧 Initializing git repository..."
git init
echo "✅ Git initialized"

# Create .gitignore
echo ""
echo "📝 Creating .gitignore..."
cat > .gitignore << 'EOF'
# Environment variables
.env
.env.local
.env.production

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*
.next/
out/
dist/

# Flutter
.dart_tool/
.flutter-plugins
.flutter-plugins-dependencies
.packages
build/
*.iml

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Docker
*.log

# Database
*.db
*.sqlite
postgres_data/

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log
EOF
echo "✅ .gitignore created"

# Create root .env template
echo ""
echo "📝 Creating .env template..."
cat > .env.example << 'EOF'
# Database
POSTGRES_USER=ble_user
POSTGRES_PASSWORD=CHANGE_THIS_PASSWORD
POSTGRES_DB=ble_tracker

# Backend
DATABASE_URL=postgresql://ble_user:CHANGE_THIS_PASSWORD@db:5432/ble_tracker
REDIS_URL=redis://redis:6379/0
JWT_SECRET_KEY=CHANGE_THIS_SECRET_KEY_TO_SOMETHING_SECURE
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# External API (update with your actual values)
EXTERNAL_BLE_API_URL=https://api.example.com
EXTERNAL_BLE_API_KEY=your-external-api-key

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:80

# Node Environment
NODE_ENV=development
EOF

# Copy to actual .env
cp .env.example .env
echo "✅ .env files created (remember to update with actual values!)"

# Create docker-compose.yml
echo ""
echo "🐳 Creating docker-compose.yml..."
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: ble_tracker_db
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-ble_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-ble_password}
      POSTGRES_DB: ${POSTGRES_DB:-ble_tracker}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - ble_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ble_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: ble_tracker_redis
    ports:
      - "6379:6379"
    networks:
      - ble_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: ble_tracker_backend
    env_file:
      - .env
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - ble_network
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data:

networks:
  ble_network:
    driver: bridge
EOF
echo "✅ docker-compose.yml created"

# Create README
echo ""
echo "📚 Creating README.md..."
cat > backend/README.md << 'EOF'
# BLE Tracker Backend

FastAPI-based REST API for BLE tag tracking system.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run database migrations:
```bash
alembic upgrade head
```

3. Start development server:
```bash
uvicorn app.main:app --reload
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc
EOF
echo "✅ Backend README created"

echo ""
echo "✅ Project setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. cd $PROJECT_NAME"
echo "   2. Update .env file with your actual credentials"
echo "   3. Follow IMPLEMENTATION_STEPS.md to build the backend"
echo "   4. Run 'docker-compose up -d' to start services"
echo ""
echo "Happy coding! 🎉"
