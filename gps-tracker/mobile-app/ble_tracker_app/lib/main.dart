import 'package:flutter/material.dart';
import 'package:ble_tracker_app/theme/app_theme.dart';
import 'package:ble_tracker_app/screens/auth/welcome_screen.dart';
import 'package:ble_tracker_app/screens/map_screen.dart';
import 'package:ble_tracker_app/screens/poi_management_screen.dart';
import 'package:ble_tracker_app/services/auth_service.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Asset Tracker',
      theme: AppTheme.lightTheme,
      debugShowCheckedModeBanner: false,
      home: const SplashScreen(),
      routes: {
        '/welcome': (context) => const WelcomeScreen(),
        '/map': (context) => const MapScreen(),
        '/poi-management': (context) => const POIManagementScreen(),
      },
    );
  }
}

// Splash screen to check authentication
class SplashScreen extends StatefulWidget {
  const SplashScreen({Key? key}) : super(key: key);

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  final _authService = AuthService();

  @override
  void initState() {
    super.initState();
    _checkAuthStatus();
  }

  Future<void> _checkAuthStatus() async {
    await Future.delayed(Duration(milliseconds: 500)); // Brief delay
    
    try {
      final isLoggedIn = await _authService.isLoggedIn();
      
      if (!mounted) return;
      
      if (isLoggedIn) {
        // Check if user has tags
        final hasTags = await _authService.hasTags();
        
        if (!mounted) return;
        
        if (hasTags) {
          // User has tags, go directly to map
          Navigator.pushReplacementNamed(context, '/map');
        } else {
          // User logged in but no tags, go to map anyway
          Navigator.pushReplacementNamed(context, '/map');
        }
      } else {
        // Not logged in, go to welcome
        Navigator.pushReplacementNamed(context, '/welcome');
      }
    } catch (e) {
      print('Error checking auth: $e');
      if (mounted) {
        Navigator.pushReplacementNamed(context, '/welcome');
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF173D64), Color(0xFF1f4f7e)],
          ),
        ),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.location_on,
                size: 80,
                color: Colors.white,
              ),
              SizedBox(height: 24),
              Text(
                'Asset Tracker',
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              SizedBox(height: 40),
              CircularProgressIndicator(
                valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
// Test staging
