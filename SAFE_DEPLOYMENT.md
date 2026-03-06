# Safe Production Deployment Guide

## 🛡️ Production-Safe Architecture

This setup ensures **zero risk** of breaking production by:
1. **Never touching .env files** during deployment
2. **Separating code from configuration** completely
3. **One-time manual env setup** that persists forever

## Current Deployment Workflows

You have **two deployment workflows**:

### ❌ `.github/workflows/deploy.yml` (RISKY - should be removed)
- Creates/updates .env files during deployment
- Even with safety checks, still tries to manage secrets
- Risk of incomplete or outdated credentials

### ✅ `.github/workflows/deploy-production.yml` (SAFE - recommended)
- **Never touches .env files**
- Only syncs code files
- Builds Flutter web app
- Restarts containers with existing config
- Proper health checks

## Recommended Setup

### Step 1: One-Time Production Environment Setup

**Do this ONCE on your production server:**

```bash
# SSH into production
ssh root@161.35.38.209

# Navigate to project directory
cd ~/gps-tracker

# Create root .env file (for docker-compose)
cat > .env << 'EOF'
# Database Configuration
POSTGRES_USER=ble_user
POSTGRES_PASSWORD=YOUR_ACTUAL_DB_PASSWORD
POSTGRES_DB=ble_tracker

# MZone Client Secret
MZONE_CLIENT_SECRET=YOUR_ACTUAL_MZONE_SECRET
EOF

# Create backend .env file (for FastAPI app)
cat > backend/.env << 'EOF'
# Database
DATABASE_URL=postgresql://ble_user:YOUR_ACTUAL_DB_PASSWORD@db:5432/ble_tracker

# Security
SECRET_KEY=YOUR_ACTUAL_JWT_SECRET_MIN_32_CHARS

# SendGrid Email
SENDGRID_API_KEY=YOUR_ACTUAL_SENDGRID_KEY
FROM_EMAIL=noreply@pinplot.me

# MZone GPS API
MZONE_API_URL=https://api.myprofiler.com/oauth2/v1
MZONE_REDIRECT_URI=http://161.35.38.209/api/v1/mzone/callback
MZONE_CLIENT_ID=Tracking_GPS
MZONE_CLIENT_SECRET=YOUR_ACTUAL_MZONE_SECRET
MZONE_USERNAME=YOUR_MZONE_USERNAME
MZONE_PASSWORD=YOUR_MZONE_PASSWORD
MZONE_SCOPE=read write
MZONE_GRANT_TYPE=password
MZONE_API_BASE=https://api.myprofiler.com
MZONE_VEHICLE_GROUP_ID=YOUR_VEHICLE_GROUP_ID

# Settings
DEBUG=False
EOF

# Secure the files
chmod 600 .env backend/.env

# Verify files exist
ls -la .env backend/.env
```

### Step 2: Use Safe Deployment Workflow

**Recommended: Keep only `deploy-production.yml`**

This workflow:
- ✅ Excludes .env files from rsync
- ✅ Never creates or modifies secrets
- ✅ Only deploys code changes
- ✅ Restarts services safely

**Action items:**
```bash
# On local machine
cd /Users/carl/Documents/MobileCode/mobileGPS

# Remove the risky workflow
git rm .github/workflows/deploy.yml

# Optionally rename deploy-production.yml to deploy.yml
git mv .github/workflows/deploy-production.yml .github/workflows/deploy.yml

# Commit
git commit -m "Use safe deployment: never touch production .env files"
```

### Step 3: Deploy Code Changes

From now on, deployments are **100% safe**:

```bash
# Make code changes on develop branch
git checkout develop
# ... edit code ...
git add .
git commit -m "Your changes"
git push origin develop

# Merge to main to trigger deployment
git checkout main
git merge develop
git push origin main
```

**What happens:**
1. GitHub Actions workflow triggers
2. Syncs code files to production (excluding .env)
3. Builds Flutter web app
4. Restarts Docker containers
5. Uses existing .env files (never touched!)

## Local Development

```bash
# Copy example files
cp gps-tracker/.env.example gps-tracker/.env
cp gps-tracker/backend/.env.example gps-tracker/backend/.env

# Edit with your local credentials
nano gps-tracker/.env
nano gps-tracker/backend/.env

# Start services
cd gps-tracker
docker-compose up --build
```

## Production Updates

### To Update Code (Safe ✅)
```bash
git push origin main  # Triggers deployment
```

### To Update Environment Variables (Manual)
```bash
ssh root@161.35.38.209
cd ~/gps-tracker
nano backend/.env  # Edit as needed
docker-compose restart backend  # Apply changes
```

## Why This is Safer

| Approach | Risk Level | Issues |
|----------|-----------|---------|
| **Old deploy.yml** | 🔴 HIGH | Overwrites .env every time |
| **Fixed deploy.yml** | 🟡 MEDIUM | Only creates if missing, but still manages secrets |
| **deploy-production.yml** | 🟢 SAFE | Never touches .env, purely code deployment |

## Emergency Rollback

If deployment breaks something:

```bash
ssh root@161.35.38.209
cd ~/gps-tracker

# Check what's wrong
docker-compose logs backend

# Rollback code (if needed)
git checkout PREVIOUS_COMMIT_HASH
# ... manually copy files ...

# Restart services
docker-compose restart
```

## Verification Checklist

After deployment:
- [ ] Backend API responds: `curl http://161.35.38.209/api/health`
- [ ] Admin panel loads: `https://pinplot.me/admin`
- [ ] Customer panel loads: `https://pinplot.me/customer`
- [ ] Flutter web loads: `https://pinplot.me`
- [ ] Check logs: `ssh root@... "docker logs ble_tracker_backend"`

## Security Best Practices

1. ✅ **Never commit .env files** (already in .gitignore)
2. ✅ **Keep GitHub Secrets as backup** (for reference only)
3. ✅ **Use strong passwords** (min 32 chars for SECRET_KEY)
4. ✅ **Restrict .env file permissions** (`chmod 600`)
5. ✅ **Separate code from config** (this guide!)

## Questions?

- **"What if I need to add a new env var?"** - Add it manually on production server, not via deployment
- **"Can I update env vars via GitHub Actions?"** - No! That's the whole point - manual = safer
- **"What if .env file gets deleted?"** - Keep a secure backup, or recreate from .env.example
- **"Should I keep deploy.yml?"** - No, remove it. Use only deploy-production.yml

---

**Bottom line:** Code deployments should deploy code, not manage secrets.
