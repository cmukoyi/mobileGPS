# Staging Environment Setup

## One-Time Setup on Server

Before running the staging deployment workflow, you need to set up the staging environment on the server:

```bash
ssh root@161.35.38.209

# Create staging directory
mkdir -p ~/gps-tracker-staging/backend

# Copy production .env files as templates for staging
cp ~/gps-tracker/.env ~/gps-tracker-staging/.env
cp ~/gps-tracker/backend/.env ~/gps-tracker-staging/backend/.env

# Edit staging backend .env to use staging database
nano ~/gps-tracker-staging/backend/.env
```

**Change in `~/gps-tracker-staging/backend/.env`:**
```bash
# Change this line:
DATABASE_URL=postgresql://ble_user:PASSWORD@db:5432/ble_tracker

# To this:
DATABASE_URL=postgresql://ble_user:PASSWORD@db:5432/ble_tracker_staging

# And ensure DEBUG is True:
DEBUG=True
```

Save and exit (Ctrl+X, Y, Enter).

## Testing Staging Environment

After setup, test that containers can start:

```bash
cd ~/gps-tracker-staging

# Try to start containers
docker-compose up -d

# Check status
docker-compose ps

# Check logs if there are issues
docker-compose logs backend
docker-compose logs flutter-web
```

## Accessing Staging

Once working:
- **Backend**: `http://161.35.38.209:8081/api/health`
- **Web App**: `http://161.35.38.209:3003/`
- **Database**: Port 5433 (separate from production)
- **Redis**: Port 6380 (separate from production)

## Automated Deployments

After manual setup is complete, GitHub Actions will automatically:
1. Build Flutter web app
2. Deploy code to `~/gps-tracker-staging`
3. Rebuild and restart containers
4. Run health checks

## Troubleshooting

If staging fails to start:

```bash
ssh root@161.35.38.209
cd ~/gps-tracker-staging

# Check what's running
docker ps -a | grep staging

# View logs
docker-compose logs -f

# Restart from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check specific service
docker-compose logs backend
docker logs ble_tracker_backend_staging
```
