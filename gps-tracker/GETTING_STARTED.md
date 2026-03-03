# Quick Start - BLE Tracker Foundation

## ✅ What's Been Created

1. **Backend API (FastAPI)** - `/backend`
   - Demo data endpoints for tags and locations
   - Health check endpoint
   - CORS enabled for mobile/web access

2. **Flutter Mobile App** - `/mobile-app/ble_tracker_app`
   - Connects to backend API
   - Displays list of BLE tags
   - Shows tag locations
   - Pull-to-refresh functionality

## 🚀 Quick Start (Local Testing)

### Step 1: Start the Backend

```bash
# Navigate to backend directory
cd /Users/carl/Documents/MobileCode/mobileGPS/ble-tracker/backend

# Install dependencies (if you have Python 3.11+)
pip install -r requirements.txt

# Start the backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at: **http://localhost:8000**

Test it:
```bash
# Health check
curl http://localhost:8000/health

# Get tags
curl http://localhost:8000/api/v1/tags

# Get tag location
curl http://localhost:8000/api/v1/tags/tag-001/location
```

### Step 2: Start the Flutter App

```bash
# Navigate to Flutter app
cd /Users/carl/Documents/MobileCode/mobileGPS/ble-tracker/mobile-app/ble_tracker_app

# Run on connected device or simulator
flutter run
```

**For iOS Simulator:** The app will connect to `http://localhost:8000` automatically.

**For Android Emulator:** Edit `lib/services/api_service.dart` and change:
```dart
static const String baseUrl = 'http://10.0.2.2:8000/api/v1';
```

**For Physical Device:** Find your computer's IP address and update:
```dart
static const String baseUrl = 'http://YOUR_IP:8000/api/v1';
```

## 🐳 Docker Setup (For Production/Linux Deployment)

### Prerequisites
1. Start Docker Desktop on your Mac
2. Make sure Docker is running: `docker ps`

### Start with Docker

```bash
cd /Users/carl/Documents/MobileCode/mobileGPS/ble-tracker

# Start all services
docker compose up -d --build

# View logs
docker compose logs -f backend

# Stop services
docker compose down
```

The backend will be available at: **http://localhost:8000**

### Check Docker Status

```bash
# Check if containers are running
docker compose ps

# View backend logs
docker compose logs backend

# Restart backend
docker compose restart backend
```

## 📱 Testing the Connection

### From iOS Simulator:
1. Start backend: `python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
2. Start Flutter app: `flutter run`
3. App should connect automatically and show 3 demo tags

### From Android Emulator:
1. Update API URL in `lib/services/api_service.dart` to `http://10.0.2.2:8000/api/v1`
2. Start backend
3. Start Flutter app
4. App should connect and show demo tags

### From Physical Device:
1. Find your computer's IP: `ifconfig | grep "inet " | grep -v 127.0.0.1`
2. Update API URL to use your IP: `http://192.168.1.X:8000/api/v1`
3. Make sure device is on same WiFi network
4. Start backend
5. Start Flutter app

## 🎯 What Works Now

### Backend Endpoints:
- ✅ `GET /` - API info
- ✅ `GET /health` - Health check
- ✅ `GET /api/v1/tags` - List all tags (demo data)
- ✅ `GET /api/v1/tags/{id}` - Get tag details
- ✅ `GET /api/v1/tags/{id}/location` - Get tag location
- ✅ `GET /api/v1/tags/{id}/history` - Get location history

### Mobile App Features:
- ✅ Connects to backend
- ✅ Displays tag list
- ✅ Shows tag details
- ✅ Displays tag locations
- ✅ Pull-to-refresh
- ✅ Error handling
- ✅ Health check on startup

## 📝 Next Steps

Now you have a working foundation! Next you can:

1. **Replace demo data with external API**
   - Update `backend/app/main.py` to call your external BLE API
   - Add authentication/API keys

2. **Add user authentication**
   - JWT tokens
   - User registration/login

3. **Add database**
   - PostgreSQL for user accounts
   - Redis for caching

4. **Build web dashboard**
   - Admin UI
   - Customer UI with map

5. **Deploy to production**
   - Deploy Docker container to Linux server
   - Set up domain and SSL

## 🔧 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill process if needed
kill -9 <PID>
```

### Flutter can't connect
- Check backend is running: `curl http://localhost:8000/health`
- Check iOS simulator uses `localhost`, Android emulator uses `10.0.2.2`
- For physical device, use your computer's IP address
- Make sure firewall allows connections on port 8000

### Docker issues
- Make sure Docker Desktop is running
- Try: `docker compose down && docker compose up -d --build`
- Check logs: `docker compose logs -f`

## 📚 File Structure

```
ble-tracker/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py            # Main API with demo endpoints
│   ├── Dockerfile
│   └── requirements.txt
│
├── mobile-app/
│   └── ble_tracker_app/       # Flutter app
│       ├── lib/
│       │   ├── main.dart      # Main app UI
│       │   └── services/
│       │       └── api_service.dart  # API client
│       └── pubspec.yaml
│
└── docker-compose.yml         # Docker configuration
```

## 🎉 Success!

You now have:
- ✅ Working backend with demo data
- ✅ Flutter mobile app connecting to backend
- ✅ Docker configuration ready for deployment
- ✅ Foundation to add real external API integration

**Ready to add your external API endpoints!**
