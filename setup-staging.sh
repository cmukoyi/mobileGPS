#!/bin/bash
# Setup staging environment on Digital Ocean server
# Run this ONCE before using the staging deployment workflow

set -e

echo "🚀 Setting up staging environment on server..."

ssh root@161.35.38.209 << 'EOF'
  echo "📁 Creating staging directory..."
  mkdir -p ~/gps-tracker-staging/backend

  echo "📋 Copying .env files from production..."
  if [ -f ~/gps-tracker/.env ]; then
    cp ~/gps-tracker/.env ~/gps-tracker-staging/.env
    echo "✅ Root .env copied"
  else
    echo "⚠️  Production .env not found, creating minimal version"
    echo "POSTGRES_USER=ble_user" > ~/gps-tracker-staging/.env
    echo "POSTGRES_PASSWORD=ble_password" >> ~/gps-tracker-staging/.env
    echo "POSTGRES_DB=ble_tracker_staging" >> ~/gps-tracker-staging/.env
  fi

  if [ -f ~/gps-tracker/backend/.env ]; then
    cp ~/gps-tracker/backend/.env ~/gps-tracker-staging/backend/.env
    
    echo "🔧 Updating staging backend .env..."
    # Change database name to staging
    sed -i 's|/ble_tracker|/ble_tracker_staging|g' ~/gps-tracker-staging/backend/.env
    # Ensure DEBUG is true
    sed -i 's|DEBUG=False|DEBUG=True|g' ~/gps-tracker-staging/backend/.env
    
    echo "✅ Backend .env configured for staging"
  else
    echo "❌ ERROR: Production backend .env not found!"
    echo "Please set up production environment first"
    exit 1
  fi

  echo ""
  echo "✅ Staging environment setup complete!"
  echo ""
  echo "Staging URLs:"
  echo "  Backend: http://161.35.38.209:8081/api/health"
  echo "  Web App: http://161.35.38.209:3003/"
  echo ""
  echo "You can now push to the 'develop' branch to deploy to staging"
EOF

echo ""
echo "🎉 Setup complete! Staging environment is ready."
