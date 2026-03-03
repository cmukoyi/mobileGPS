# PinPlot.me - Production Configuration

Production deployment configuration for PinPlot GPS Tracker application.

## 🌐 Server Details

- **Server IP**: `161.35.38.209`
- **Domain**: `pinplot.me` (HTTPS)
- **Provider**: Digital Ocean
- **OS**: Ubuntu 22.04 LTS (recommended)

## 🚀 Quick Deployment Guide

### 1. DNS Configuration

Point your domain to the server:

```
A Record:  pinplot.me          → 161.35.38.209
A Record:  www.pinplot.me      → 161.35.38.209
A Record:  api.pinplot.me      → 161.35.38.209  (optional - for API subdomain)
```

**DNS Propagation**: May take 1-48 hours

Check DNS propagation:
```bash
dig pinplot.me +short
nslookup pinplot.me
```

### 2. GitHub Secrets Configuration

Go to: `GitHub Repository → Settings → Secrets and variables → Actions`

Add these secrets:

| Secret Name | Value |
|------------|-------|
| `DO_SERVER_IP` | `161.35.38.209` |
| `DO_USER` | `root` (or your SSH user) |
| `DO_SSH_PRIVATE_KEY` | Your SSH private key (see below) |
| `SECRET_KEY` | Generate: `openssl rand -hex 32` |
| `DATABASE_URL` | `postgresql://gpsuser:CHANGE_THIS_PASSWORD@postgres:5432/gpsdb` |
| `SENDGRID_API_KEY` | Get from SendGrid dashboard |
| `FROM_EMAIL` | `noreply@pinplot.me` (verify in SendGrid first) |
| `MZONE_CLIENT_ID` | Your MZone credentials |
| `MZONE_CLIENT_SECRET` | Your MZone credentials |
| `MPROFILER_USERNAME` | Your MProfiler username |
| `MPROFILER_PASSWORD` | Your MProfiler password |

### 3. Setup Server

SSH into your server:
```bash
ssh root@161.35.38.209
```

Run the setup script:
```bash
curl -o setup.sh https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/deploy/setup-digital-ocean.sh
chmod +x setup.sh
./setup.sh
```

Or manually:
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Configure firewall
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

### 4. Configure SSH for GitHub Actions

On your server:
```bash
ssh-keygen -t rsa -b 4096 -C "github-actions" -f ~/.ssh/github_actions -N ""
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys
cat ~/.ssh/github_actions
```

Copy the private key output to GitHub Secret: `DO_SSH_PRIVATE_KEY`

### 5. Setup SSL Certificate (Let's Encrypt)

After first deployment, setup SSL:

```bash
ssh root@161.35.38.209

# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d pinplot.me -d www.pinplot.me

# Auto-renewal is configured automatically by certbot
```

### 6. Update Nginx Configuration for Domain

SSH to server and edit nginx config:

```bash
ssh root@161.35.38.209
cd ~/gps-tracker/gps-tracker/nginx
nano nginx.conf
```

Update server_name:
```nginx
server {
    listen 80;
    server_name pinplot.me www.pinplot.me;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name pinplot.me www.pinplot.me;
    
    ssl_certificate /etc/letsencrypt/live/pinplot.me/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/pinplot.me/privkey.pem;
    
    # Backend API
    location /api/ {
        proxy_pass http://backend:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Admin Dashboard
    location /admin/ {
        proxy_pass http://admin-dashboard:3000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Customer Dashboard
    location / {
        proxy_pass http://customer-dashboard:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Restart nginx:
```bash
docker-compose restart nginx
```

### 7. Deploy Application

Push to GitHub main branch (automatic deployment via GitHub Actions):

```bash
cd /Users/carl/Documents/MobileCode/mobileGPS
git push origin main
```

Or manual deployment:
```bash
cd /Users/carl/Documents/MobileCode/mobileGPS/deploy
./deploy-manual.sh 161.35.38.209 root
```

### 8. Update Mobile App Backend URL

Edit Flutter app configuration:

**File**: `gps-tracker/mobile-app/ble_tracker_app/lib/services/auth_service.dart`

```dart
class AuthService {
  // Production URL
  static const String baseUrl = 'https://pinplot.me/api';
  
  // Or if using API subdomain:
  // static const String baseUrl = 'https://api.pinplot.me';
```

Rebuild mobile app:
```bash
cd gps-tracker/mobile-app/ble_tracker_app
flutter clean
flutter pub get
flutter build apk --release  # Android
flutter build ios --release   # iOS
```

## 🔗 Service URLs

After deployment:

| Service | URL | Description |
|---------|-----|-------------|
| **Customer Dashboard** | https://pinplot.me | Main user interface |
| **Admin Dashboard** | https://pinplot.me/admin | Administrator panel |
| **Backend API** | https://pinplot.me/api | REST API endpoint |
| **API Documentation** | https://pinplot.me/api/docs | Swagger/OpenAPI docs |
| **Health Check** | https://pinplot.me/api/health | Backend health status |

## 📱 Mobile App Configuration

Update these files with production URLs:

1. **Backend API URL**:
   - File: `lib/services/auth_service.dart`
   - Change: `baseUrl = 'https://pinplot.me/api'`

2. **Location Service URL**:
   - File: `lib/services/location_service.dart`
   - Change: `baseUrl = 'https://pinplot.me/api'`

3. **POI Service URL**:
   - File: `lib/services/poi_service.dart`
   - Change: `baseUrl = 'https://pinplot.me/api'`

After updating, rebuild and redistribute the app.

## 🔒 Security Checklist

- [ ] DNS configured and propagated
- [ ] SSH key authentication setup
- [ ] Firewall enabled (ports 22, 80, 443 only)
- [ ] SSL certificate installed (Let's Encrypt)
- [ ] `DEBUG=False` in production `.env`
- [ ] Strong `SECRET_KEY` generated
- [ ] Database password changed from default
- [ ] SendGrid API key configured
- [ ] CORS properly configured (not `*` in production)
- [ ] All GitHub secrets added
- [ ] SSH password authentication disabled
- [ ] Regular backups scheduled

## 📊 Monitoring

### Check Service Status
```bash
ssh root@161.35.38.209
cd ~/gps-tracker/gps-tracker
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f admin-dashboard
docker-compose logs -f customer-dashboard
docker-compose logs -f nginx
```

### Check Resource Usage
```bash
ssh root@161.35.38.209
htop
df -h
docker stats
```

### Monitor Email Delivery
- SendGrid Dashboard: https://app.sendgrid.com
- Activity Feed: Real-time email status
- Stats: Delivery metrics

## 🔄 Updates & Maintenance

### Update Application
```bash
# Automatic via GitHub Actions
git push origin main

# Or manual
cd /Users/carl/Documents/MobileCode/mobileGPS/deploy
./deploy-manual.sh 161.35.38.209 root
```

### Backup Database
```bash
ssh root@161.35.38.209
cd ~/gps-tracker/gps-tracker
docker-compose exec postgres pg_dump -U gpsuser gpsdb > backup_$(date +%Y%m%d_%H%M%S).sql

# Download backup to local machine
scp root@161.35.38.209:~/gps-tracker/gps-tracker/backup_*.sql ./backups/
```

### Restore Database
```bash
# Upload backup to server
scp backup_file.sql root@161.35.38.209:~/gps-tracker/gps-tracker/

# Restore on server
ssh root@161.35.38.209
cd ~/gps-tracker/gps-tracker
cat backup_file.sql | docker-compose exec -T postgres psql -U gpsuser gpsdb
```

### Restart Services
```bash
ssh root@161.35.38.209
cd ~/gps-tracker/gps-tracker
docker-compose restart
```

### Update SSL Certificate
```bash
# Certificates auto-renew, but to renew manually:
ssh root@161.35.38.209
sudo certbot renew
docker-compose restart nginx
```

## 🐛 Troubleshooting

### Site not accessible
```bash
# Check DNS
dig pinplot.me +short

# Check if server is responding
curl -I http://161.35.38.209

# Check nginx
ssh root@161.35.38.209
docker-compose logs nginx
```

### SSL certificate issues
```bash
ssh root@161.35.38.209
sudo certbot certificates
sudo certbot renew --dry-run
```

### Backend API not working
```bash
ssh root@161.35.38.209
cd ~/gps-tracker/gps-tracker
docker-compose logs backend

# Check if backend container is running
docker-compose ps backend

# Restart backend
docker-compose restart backend
```

### Database connection issues
```bash
ssh root@161.35.38.209
cd ~/gps-tracker/gps-tracker

# Check PostgreSQL container
docker-compose logs postgres

# Check connection
docker-compose exec postgres psql -U gpsuser gpsdb -c "SELECT 1;"
```

## 📞 Support & Resources

- **Documentation**: `/Users/carl/Documents/MobileCode/mobileGPS/`
- **SendGrid Setup**: `SENDGRID_SETUP.md`
- **General Deployment**: `DEPLOYMENT.md`
- **Server IP**: `161.35.38.209`
- **Domain**: `pinplot.me`

## ✅ Pre-Launch Checklist

- [ ] Server provisioned and accessible
- [ ] DNS configured and propagated
- [ ] SSL certificate installed
- [ ] GitHub repository setup with all secrets
- [ ] SendGrid account created and sender verified
- [ ] Environment variables configured
- [ ] Application deployed successfully
- [ ] Health checks passing
- [ ] Test user registration (PIN email received)
- [ ] Test geofence alert (email received)
- [ ] Mobile app updated with production URL
- [ ] Mobile app tested with production backend
- [ ] Backups configured
- [ ] Monitoring setup

---

**Production URL**: https://pinplot.me  
**Server IP**: 161.35.38.209  
**Last Updated**: March 3, 2026
