# 🧪 Environment Testing Guide

## Quick Test Commands

### 1️⃣ Test Local Development Mode

```bash
cd gps-tracker/mobile-app/ble_tracker_app

# Run Flutter in debug mode
flutter run -d chrome

# Expected output in console:
# 🛠️  DEBUG MODE: Using development server → http://localhost:8000
```

**What to verify:**
- [ ] Console shows "DEBUG MODE: Using development server → http://localhost:8000"
- [ ] App loads at http://localhost:[port]
- [ ] Network tab shows requests to `http://localhost:8000/api/v1/`
- [ ] Can login and see dashboard
- [ ] Backend logs show incoming API requests

### 2️⃣ Test Production Build Mode

```bash
cd gps-tracker/mobile-app/ble_tracker_app

# Build for production
flutter build web --release

# Check the build output
echo "Checking production build..."
grep -r "localhost" build/web/*.js && echo "❌ FAIL: localhost found in build!" || echo "✅ PASS: No localhost in build"
grep -r "pinplot.me" build/web/*.js && echo "✅ PASS: Production URL found" || echo "❌ FAIL: Production URL missing"
```

**What to verify:**
- [ ] No "localhost" in build files
- [ ] "pinplot.me" found in build files
- [ ] Build completes without errors
- [ ] Build size is reasonable (~5-20MB for Flutter web)

### 3️⃣ Test Git Hook Protection

```bash
cd gps-tracker/mobile-app/ble_tracker_app

# Create test file with localhost URL (should be blocked)
cat > lib/test_bad_url.dart << 'EOF'
class TestService {
  static const String badUrl = 'http://localhost:8000/api';
}
EOF

# Try to commit it
git add lib/test_bad_url.dart
git commit -m "Test git hook"

# Expected output:
# ❌ ERROR: Found localhost/development URL: localhost:8000
# Development URLs should NEVER be committed to main branch!

# Clean up
git reset HEAD lib/test_bad_url.dart
rm lib/test_bad_url.dart
```

**What to verify:**
- [ ] Git hook blocks the commit
- [ ] Error message explains the problem
- [ ] Provides helpful suggestions
- [ ] Normal commits (without localhost) work fine

### 4️⃣ Test Backend Connection

```bash
# Check backend health
curl http://localhost:8000/health

# Expected: {"status":"healthy"}

# Check database connection
docker compose logs backend | grep -i "database\|connected\|error" | tail -20

# Test API endpoint
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

**What to verify:**
- [ ] Health endpoint returns `{"status":"healthy"}`
- [ ] Backend logs show no database errors
- [ ] API endpoints respond (even if auth fails, should get proper error)
- [ ] No OperationalError or connection timeout

### 5️⃣ End-to-End Test

```bash
# 1. Start all services
cd gps-tracker
docker compose up -d

# 2. Check all services healthy
docker compose ps

# 3. Run Flutter app
cd mobile-app/ble_tracker_app
flutter run -d chrome

# 4. Test in browser:
# - Login with your credentials
# - Check map loads
# - Verify vehicles appear
# - Check console for errors (F12 → Console)
# - Check network requests (F12 → Network)
```

**What to verify:**
- [ ] All Docker containers running
- [ ] Flutter app compiles without errors
- [ ] Browser shows no console errors
- [ ] Login works
- [ ] Map displays
- [ ] Vehicles load from backend
- [ ] All API calls succeed

### 6️⃣ Test Environment Detection

Create a test widget to display environment info:

```bash
cd gps-tracker/mobile-app/ble_tracker_app

# Add this temporarily to lib/screens/map_screen.dart
# Inside the Scaffold, add:
```

```dart
// Add to top of map_screen.dart imports
import 'package:ble_tracker_app/config/environment.dart';

// Add as first widget in Scaffold body (temporarily for testing)
Container(
  color: Colors.red.withOpacity(0.9),
  padding: EdgeInsets.all(8),
  child: Text(
    'ENV: ${Environment.environmentDescription}\n'
    'API: ${Environment.apiBaseUrl}\n'
    'Debug: ${Environment.isDevelopment}',
    style: TextStyle(color: Colors.white, fontSize: 12),
  ),
),
```

**What to verify:**
- [ ] Debug mode shows: "Development (localhost:8000)"
- [ ] Release build shows: "Production (pinplot.me)"
- [ ] API URL changes based on mode
- [ ] isDevelopment is true/false correctly

## 🎯 Quick Verification Script

Run this all-in-one test:

```bash
#!/bin/bash
cd /Users/carl/Documents/MobileCode/mobileGPS

echo "🧪 Running Environment Tests..."
echo "================================"

# Test 1: Check for localhost URLs
echo ""
echo "1️⃣  Checking for hardcoded localhost URLs..."
if grep -rn "localhost\|192\.168\|127\.0\.0\.1" gps-tracker/mobile-app/ble_tracker_app/lib/services/*.dart | grep -v environment.dart; then
  echo "   ❌ FAIL: Found hardcoded localhost URLs"
else
  echo "   ✅ PASS: No hardcoded localhost URLs"
fi

# Test 2: Verify environment.dart exists
echo ""
echo "2️⃣  Checking environment.dart configuration..."
if [ -f "gps-tracker/mobile-app/ble_tracker_app/lib/config/environment.dart" ]; then
  echo "   ✅ PASS: environment.dart exists"
  
  # Check for kDebugMode usage
  if grep -q "kDebugMode" gps-tracker/mobile-app/ble_tracker_app/lib/config/environment.dart; then
    echo "   ✅ PASS: Uses automatic build mode detection"
  else
    echo "   ⚠️  WARNING: Not using kDebugMode detection"
  fi
else
  echo "   ❌ FAIL: environment.dart missing"
fi

# Test 3: Check services use Environment
echo ""
echo "3️⃣  Checking services use Environment..."
SERVICES="auth_service.dart api_service.dart location_service.dart poi_service.dart"
for service in $SERVICES; do
  if grep -q "Environment.apiBaseUrl" gps-tracker/mobile-app/ble_tracker_app/lib/services/$service; then
    echo "   ✅ $service"
  else
    echo "   ❌ $service (not using Environment)"
  fi
done

# Test 4: Check git hooks installed
echo ""
echo "4️⃣  Checking git hooks..."
if [ "$(git config core.hooksPath)" = ".githooks" ]; then
  echo "   ✅ PASS: Git hooks configured"
  
  if [ -x ".githooks/pre-commit" ]; then
    echo "   ✅ PASS: Pre-commit hook executable"
  else
    echo "   ⚠️  WARNING: Pre-commit hook not executable"
  fi
else
  echo "   ❌ FAIL: Git hooks not configured"
fi

# Test 5: Check backend health
echo ""
echo "5️⃣  Checking backend health..."
if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
  echo "   ✅ PASS: Backend responding"
else
  echo "   ❌ FAIL: Backend not responding (is Docker running?)"
fi

# Test 6: Check Docker services
echo ""
echo "6️⃣  Checking Docker services..."
cd gps-tracker
RUNNING=$(docker compose ps --format json 2>/dev/null | grep -c '"State":"running"')
if [ "$RUNNING" -ge 4 ]; then
  echo "   ✅ PASS: $RUNNING services running"
else
  echo "   ⚠️  WARNING: Only $RUNNING services running"
fi

echo ""
echo "================================"
echo "🏁 Tests Complete!"
echo ""
echo "Next steps:"
echo "  1. Run: flutter run -d chrome"
echo "  2. Check console for: 🛠️  DEBUG MODE: Using development server"
echo "  3. Test login and map loading"
echo "  4. Run: flutter build web --release"
echo "  5. Verify no localhost in build/web/"
```

Save this as `test-environment.sh` and run:

```bash
chmod +x test-environment.sh
./test-environment.sh
```

## 📊 Expected Results Summary

| Test | Debug Mode | Release Mode |
|------|------------|--------------|
| Environment.apiBaseUrl | `http://localhost:8000` | `https://pinplot.me` |
| Environment.isDevelopment | `true` | `false` |
| Environment.buildMode | `"debug"` | `"release"` |
| Console output | 🛠️  DEBUG MODE | 🚀 RELEASE MODE |
| Network requests | localhost:8000 | pinplot.me |
| Build contains localhost | N/A | ❌ Should be NO |

## 🐛 Troubleshooting

### Problem: Backend not responding

```bash
# Check backend logs
docker compose logs backend --tail=50

# Restart backend
docker compose restart backend

# Check database password
docker compose exec backend env | grep DATABASE_URL
```

### Problem: Flutter build errors

```bash
# Clean and rebuild
flutter clean
flutter pub get
flutter build web --release
```

### Problem: Git hook not working

```bash
# Reinstall hooks
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit

# Test manually
.githooks/pre-commit
```

### Problem: Wrong URL being used

```bash
# Add debug logging to environment.dart
print('Environment: ${Environment.environmentDescription}');
print('API URL: ${Environment.apiBaseUrl}');
print('Is Debug: ${Environment.isDevelopment}');
print('Build Mode: ${Environment.buildMode}');
```

## ✅ Definition of Done

All tests pass when:

- ✅ No hardcoded localhost URLs in service files
- ✅ Environment.dart uses kDebugMode for automatic detection
- ✅ All service files import and use Environment.apiBaseUrl
- ✅ Git hooks block commits with localhost URLs
- ✅ Backend health endpoint responds
- ✅ Debug mode uses localhost:8000
- ✅ Release build uses pinplot.me
- ✅ Release build contains NO localhost references
- ✅ End-to-end test: login, map, vehicles all work
- ✅ Console shows correct environment on startup

Good luck! 🚀
