# 🔧 Environment Management Guide

## Automatic Configuration (Recommended Setup)

Your app now uses **Flutter's built-in build mode detection** - no manual configuration needed!

## How It Works

### Automatic Mode Selection

```dart
// lib/config/environment.dart automatically selects:

if (kDebugMode) {
  // Debug builds → localhost:8000
} else {
  // Release builds → https://pinplot.me
}
```

**You never need to manually change configuration files!**

## Local Development Workflow

### Running Locally

```bash
cd gps-tracker/mobile-app/ble_tracker_app

# Run on web (uses localhost:8000 automatically)
flutter run -d chrome

# Run on mobile emulator (uses localhost:8000)
flutter run

# Run on physical device (uses localhost:8000)
flutter run -d <device-id>
```

**Debug mode automatically detects and uses `http://localhost:8000`**

### Viewing Logs

The app prints which environment it's using:

```
🛠️  DEBUG MODE: Using development server → http://localhost:8000
```

## Production Deployment Workflow

### Building for Production

```bash
cd gps-tracker/mobile-app/ble_tracker_app

# Build web release (uses https://pinplot.me automatically)
flutter build web --release

# Build Android release
flutter build apk --release

# Build iOS release
flutter build ios --release
```

**Release builds automatically use production URL `https://pinplot.me`**

### Viewing Build Logs

Release builds show:

```
🚀 RELEASE MODE: Using production server → https://pinplot.me
```

## Configuration Files (Both Safe to Commit)

### Development Configuration
**File**: `lib/config/environment.dart`
```dart
static const String _developmentUrl = 'http://localhost:8000';
```
✅ **Safe to commit** - Only active in debug mode  
✅ **Team-friendly** - Everyone gets same dev config  
✅ **No secrets** - Just localhost URL

### Production Configuration
**File**: `lib/config/environment.dart`
```dart
static const String _productionUrl = 'https://pinplot.me';
```
✅ **Safe to commit** - Public production URL  
✅ **Always used for releases** - No accidental localhost deployments  
✅ **No secrets** - Just domain name

## Testing Production Config Locally

Sometimes you want to test against production API from your local machine:

```bash
# Option 1: Build release and serve it
flutter build web --release
python3 -m http.server 8080 --directory build/web

# Option 2: Use profile mode (uses production URL)
flutter run --profile -d chrome
```

## Docker Compose Local Testing

Your backend runs in Docker with automatic environment detection:

```bash
cd gps-tracker

# Start all services (backend uses local .env)
docker compose up -d

# Check logs
docker compose logs backend

# Backend runs on: http://localhost:8000
# Admin dashboard: http://localhost:3000
# Customer dashboard: http://localhost:3001
# Flutter web: http://localhost:3002
```

## Backend Environment Files

### Local Development
**File**: `gps-tracker/backend/.env`
```bash
DATABASE_URL=postgresql://ble_user:ble_password@db:5432/ble_tracker
SECRET_KEY=dev-secret-key-local-only
SENDGRID_API_KEY=SG.your_key_here
```
⚠️ **Never commit** - Contains real secrets  
✅ **In .gitignore** - Protected from accidental commits  
✅ **Use .env.example as template**

### Production Deployment
**File**: Docker Compose on server uses environment variables
```bash
# Set via hosting platform (Digital Ocean, AWS, etc.)
export DATABASE_URL="postgresql://user:pass@production-db:5432/db"
export SECRET_KEY="production-secret-key-from-env"
export SENDGRID_API_KEY="SG.production_key"
```
✅ **Never in code** - Environment variables only  
✅ **Managed by platform** - Digital Ocean Secrets, AWS Secrets Manager  
✅ **Rotatable** - Change without code deployment

## Preventing Accidents

### Git Hooks (Pre-commit)

Installed at: `.githooks/pre-commit`

Automatically blocks commits with:
- `localhost` in Dart files
- `192.168.x.x` private IPs
- `127.0.0.1` loopback
- `http://10.0.0.x` local networks

```bash
# If you try to commit localhost URLs:
❌ ERROR: Found localhost/development URL: localhost:8000
   Development URLs should NEVER be committed to main branch!
```

### Flutter Build Verification

Add to CI/CD pipeline (GitHub Actions):

```yaml
# .github/workflows/deploy.yml
- name: Verify Production Build
  run: |
    cd gps-tracker/mobile-app/ble_tracker_app
    
    # Build for production
    flutter build web --release
    
    # Verify production URL is in build
    if ! grep -q "https://pinplot.me" build/web/main.dart.js; then
      echo "❌ Production URL not found in build"
      exit 1
    fi
    
    # Verify localhost is NOT in build
    if grep -q "localhost" build/web/main.dart.js; then
      echo "❌ localhost found in production build!"
      exit 1
    fi
    
    echo "✅ Production build verified"
```

## Common Scenarios

### Scenario 1: Local Development

```bash
# 1. Start backend
cd gps-tracker
docker compose up -d

# 2. Run Flutter app
cd mobile-app/ble_tracker_app
flutter run -d chrome

# Result: App connects to http://localhost:8000 ✅
```

### Scenario 2: Production Deployment

```bash
# 1. Build Flutter app
cd gps-tracker/mobile-app/ble_tracker_app
flutter build web --release

# 2. Deploy to server
scp -r build/web/* user@pinplot.me:/var/www/html/

# Result: App connects to https://pinplot.me ✅
```

### Scenario 3: Testing on Physical Device

```bash
# Option A: Use ngrok to expose localhost
ngrok http 8000
# Update _developmentUrl to ngrok URL temporarily

# Option B: Use local network IP
# Update _developmentUrl to http://192.168.1.100:8000
```

### Scenario 4: Team Collaboration

```bash
# Developer 1 commits Flutter changes
git add lib/
git commit -m "Add feature"
git push

# Developer 2 pulls changes
git pull

# Both developers get same config ✅
# flutter run → localhost:8000 (automatic)
# flutter build → pinplot.me (automatic)
```

## Troubleshooting

### Problem: "Failed to load vehicles" in local dev

**Solution**: Backend not running

```bash
cd gps-tracker
docker compose ps  # Check if backend is up
docker compose logs backend  # Check for errors
docker compose restart backend  # Restart if needed
```

### Problem: App connects to wrong environment

**Check current mode**:
```dart
// Add to any screen to debug
print('Environment: ${Environment.environmentDescription}');
print('API URL: ${Environment.apiBaseUrl}');
print('Is Debug: ${Environment.isDevelopment}');
```

**Force release mode**:
```bash
flutter run --release -d chrome  # Uses production URL
```

### Problem: Localhost URL appears in production build

**This should be impossible** with automatic mode detection, but if it happens:

1. Check if you hardcoded URLs anywhere:
```bash
grep -r "localhost" lib/services/
grep -r "192.168" lib/services/
```

2. Run pre-commit hook manually:
```bash
.githooks/pre-commit
```

3. Verify Environment.dart is being used:
```bash
grep -r "Environment.apiBaseUrl" lib/services/
```

## Migration from Old Setup

If you had manual URL configuration before:

### Old Code (Manual):
```dart
// ❌ BAD: Manual URL that needs changing
class AuthService {
  static const String baseUrl = 'http://localhost:8000';  // Must change before deploy!
}
```

### New Code (Automatic):
```dart
// ✅ GOOD: Automatic based on build mode
import 'package:ble_tracker_app/config/environment.dart';

class AuthService {
  static String get baseUrl => Environment.apiBaseUrl;  // Auto-selects!
}
```

## Benefits of This Approach

✅ **Zero Configuration** - No flags, no manual changes, no confusion  
✅ **Team-Friendly** - Everyone gets same experience  
✅ **Deploy-Safe** - Impossible to accidentally deploy localhost  
✅ **Fast Context Switching** - `flutter run` for dev, `flutter build` for prod  
✅ **CI/CD Ready** - Build pipeline just runs `flutter build web --release`  
✅ **Both Configs in Repo** - Team sees both localhost and production URLs  
✅ **No Secrets in Code** - Only public URLs, no API keys or passwords  
✅ **Standard Flutter Practice** - Uses built-in kDebugMode, kReleaseMode  

## Summary

| Command | Mode | URL Used | When |
|---------|------|----------|------|
| `flutter run` | Debug | `localhost:8000` | Local development |
| `flutter run --profile` | Profile | `pinplot.me` | Test prod config locally |
| `flutter build web --release` | Release | `pinplot.me` | Production deployment |
| `flutter build apk --release` | Release | `pinplot.me` | Android production |
| `flutter build ios --release` | Release | `pinplot.me` | iOS production |

**You never need to edit configuration files manually!**
