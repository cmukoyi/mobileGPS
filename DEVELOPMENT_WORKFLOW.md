# Development and Deployment Workflow

## Overview
This document describes the proper workflow for developing, testing, and deploying changes to the mobileGPS project.

## Branch Strategy

- **`main`** - Production branch
  - Always deployable
  - Automatically deploys to production server via GitHub Actions
  - Protected - requires pull requests or careful merging
  
- **`develop`** - Development branch
  - Active development happens here
  - Test locally before merging to main
  - All feature work should be done on develop

## Local Development Workflow

### 1. Make Changes on Develop Branch

```bash
# Ensure you're on develop
git checkout develop
git pull origin develop

# Make your changes
# Edit files...

# Test locally (see Testing section below)
```

### 2. Test Locally with Docker Compose

```bash
cd gps-tracker

# Ensure you have a .env file (see .env.example)
cp backend/.env.example backend/.env
# Edit backend/.env with your local credentials

# Start all services
docker-compose up --build

# Services will be available at:
# - Backend API: http://localhost:8000
# - Admin Dashboard: http://localhost:3000
# - Customer Dashboard: http://localhost:3001  
# - Flutter Web: http://localhost:8080
# - PostgreSQL: localhost:5432
```

### 3. Commit and Push Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "Description of changes"

# Push to develop
git push origin develop
```

### 4. Deploy to Production

**Option A: Merge via Pull Request (Recommended)**
```bash
# Create PR from develop to main on GitHub
# Review changes
# Merge PR
```

**Option B: Direct Merge (Use with caution)**
```bash
# Switch to main
git checkout main
git pull origin main

# Merge develop
git merge develop

# Push to trigger deployment
git push origin main
```

## GitHub Actions Deployment

When code is pushed to `main`, the deployment workflow automatically:

1. ✅ Checks out code
2. ✅ Copies files to production server via rsync
3. ✅ Creates `.env` files with secrets from GitHub Secrets
4. ✅ Builds Flutter web application  
5. ✅ Restarts Docker containers on production
6. ✅ Runs database migrations

### Monitoring Deployment

- View deployment status: https://github.com/cmukoyi/mobileGPS/actions
- Check logs in GitHub Actions UI
- SSH to server to verify: `docker ps` and check service health

## Production Server

- **Server**: 161.35.38.209 (ubuntu-s-1vcpu-512mb-10gb-lon1-01)
- **URL**: https://pinplot.me
- **Location**: ~/gps-tracker
- **Access**: SSH as root (use DO_SSH_PRIVATE_KEY from GitHub Secrets)

### Manual Production Commands (Emergency Use Only)

```bash
# SSH into production
ssh root@161.35.38.209

# Check running containers
docker ps

# View logs
docker logs ble_tracker_backend
docker logs ble_tracker_db

# Restart services
cd ~/gps-tracker
docker-compose restart backend

# Full rebuild (use with caution)
docker-compose down
docker-compose up -d --build
```

## Testing Checklist

Before merging to main:

- [ ] Backend API starts without errors
- [ ] Database migrations run successfully  
- [ ] Authentication endpoints work (register/login/verify)
- [ ] Admin dashboard loads
- [ ] Customer dashboard loads
- [ ] Flutter web app loads
- [ ] Check browser console for JavaScript errors
- [ ] Test critical user flows (login, view data, etc.)

## Common Issues and Solutions

### Issue: "Port already in use"
```bash
# Find and kill process using the port
lsof -ti:8000 | xargs kill -9
```

### Issue: Database connection errors
```bash
# Ensure PostgreSQL is running
docker ps | grep postgres

# Check database logs
docker logs ble_tracker_db

# Verify .env has correct DATABASE_URL
cat backend/.env | grep DATABASE_URL
```

### Issue: Changes not reflecting in browser
```bash
# Clear browser cache
# Or use incognito/private window
# For Flutter web, do full rebuild:
cd gps-tracker/mobile-app/ble_tracker_app
flutter clean
flutter pub get
flutter build web --release
```

## Important Notes

- ⚠️ **Never commit secrets** - Use .env files and GitHub Secrets
- ⚠️ **Test locally first** - Don't push untested code to main
- ⚠️ **Watch GitHub Actions** - Verify deployment succeeds
- ⚠️ **Keep develop and main in sync** - Merge regularly
- ✅ **Use descriptive commit messages** - Helps track changes
- ✅ **Document new features** - Update PROJECT_STRUCTURE.md

## Recent Changes

### Redis Removal (Latest)
- **What**: Removed Redis service completely
- **Why**: Security risk (exposed port 6379), not used in application
- **Impact**: No functional impact, improved security
- **Files Changed**: docker-compose.yml, .env.example, deploy.yml, admin dashboard

### Staging Removal  
- **What**: Removed non-functional staging environment setup
- **Why**: Not working, complicated workflow unnecessarily
- **Impact**: Simplified deployment, clearer workflow
- **Files Removed**: deploy-staging.yml, setup-staging.sh, STAGING_SETUP.md

## Questions?

Check PROJECT_STRUCTURE.md for detailed architecture documentation.
