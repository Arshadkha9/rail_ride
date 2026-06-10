import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../features/auth/presentation/providers/auth_provider.dart';
import '../../features/auth/presentation/screens/login_screen.dart';
import '../../features/auth/presentation/screens/otp_verification_screen.dart';
import '../../features/auth/presentation/screens/signup_screen.dart';
import '../../features/auth/presentation/screens/splash_screen.dart';
import '../../features/home/presentation/screens/home_screen.dart';
import '../../features/notifications/presentation/screens/notifications_screen.dart';
import '../../features/profile/presentation/screens/profile_screen.dart';
import '../../features/railway/presentation/screens/favorites_screen.dart';
import '../../features/railway/presentation/screens/live_status_screen.dart';
import '../../features/railway/presentation/screens/pnr_status_screen.dart';
import '../../features/railway/presentation/screens/railway_home_screen.dart';
import '../../features/railway/presentation/screens/station_search_screen.dart';
import '../../features/railway/presentation/screens/train_schedule_screen.dart';
import '../../features/railway/presentation/screens/train_search_screen.dart';
import '../../features/rides/presentation/screens/ride_booking_screen.dart';
import '../../features/rides/presentation/screens/ride_confirm_screen.dart';
import '../../features/rides/presentation/screens/ride_fare_screen.dart';
import '../../features/rides/presentation/screens/ride_tracking_screen.dart';
import '../../features/trips/presentation/screens/trips_screen.dart';
import '../../features/wallet/presentation/screens/wallet_screen.dart';

class AppRoutes {
  AppRoutes._();

  static const splash = '/';
  static const login = '/login';
  static const signup = '/signup';
  static const otp = '/otp';
  static const home = '/home';
  static const railway = '/railway';
  static const trainSearch = '/railway/search';
  static const pnrStatus = '/railway/pnr';
  static const liveStatus = '/railway/live-status';
  static const trainSchedule = '/railway/schedule';
  static const stationSearch = '/railway/stations';
  static const favorites = '/railway/favorites';
  static const rideBooking = '/rides/book';
  static const rideFare = '/rides/fare';
  static const rideConfirm = '/rides/confirm';
  static const rideTracking = '/rides/tracking';
  static const wallet = '/wallet';
  static const trips = '/trips';
  static const profile = '/profile';
  static const notifications = '/notifications';
}

final routerProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authStateProvider);

  return GoRouter(
    initialLocation: AppRoutes.splash,
    debugLogDiagnostics: false,
    redirect: (context, state) {
      final isAuthenticated = authState.isAuthenticated;
      final isAuthRoute = state.matchedLocation == AppRoutes.login ||
          state.matchedLocation == AppRoutes.signup ||
          state.matchedLocation == AppRoutes.otp;
      final isSplash = state.matchedLocation == AppRoutes.splash;

      if (authState.isLoading && isSplash) return null;

      if (!isAuthenticated && !isAuthRoute && !isSplash) {
        return AppRoutes.login;
      }

      if (isAuthenticated && (isAuthRoute || isSplash)) {
        return AppRoutes.home;
      }

      return null;
    },
    routes: [
      GoRoute(
        path: AppRoutes.splash,
        builder: (_, __) => const SplashScreen(),
      ),
      GoRoute(
        path: AppRoutes.login,
        builder: (_, __) => const LoginScreen(),
      ),
      GoRoute(
        path: AppRoutes.signup,
        builder: (_, __) => const SignupScreen(),
      ),
      GoRoute(
        path: AppRoutes.otp,
        builder: (_, state) {
          final phone = state.uri.queryParameters['phone'] ?? '';
          return OtpVerificationScreen(phone: phone);
        },
      ),
      GoRoute(
        path: AppRoutes.home,
        builder: (_, __) => const HomeScreen(),
      ),
      GoRoute(
        path: AppRoutes.railway,
        builder: (_, __) => const RailwayHomeScreen(),
      ),
      GoRoute(
        path: AppRoutes.trainSearch,
        builder: (_, __) => const TrainSearchScreen(),
      ),
      GoRoute(
        path: AppRoutes.pnrStatus,
        builder: (_, __) => const PnrStatusScreen(),
      ),
      GoRoute(
        path: AppRoutes.liveStatus,
        builder: (_, __) => const LiveStatusScreen(),
      ),
      GoRoute(
        path: AppRoutes.trainSchedule,
        builder: (_, __) => const TrainScheduleScreen(),
      ),
      GoRoute(
        path: AppRoutes.stationSearch,
        builder: (_, __) => const StationSearchScreen(),
      ),
      GoRoute(
        path: AppRoutes.favorites,
        builder: (_, __) => const FavoritesScreen(),
      ),
      GoRoute(
        path: AppRoutes.rideBooking,
        builder: (_, state) {
          final type = state.uri.queryParameters['type'] ?? 'bike';
          return RideBookingScreen(rideType: type);
        },
      ),
      GoRoute(
        path: AppRoutes.rideFare,
        builder: (_, state) {
          final extra = state.extra as Map<String, dynamic>? ?? {};
          return RideFareScreen(
            rideType: extra['rideType'] as String? ?? 'bike',
            pickup: extra['pickup'] as String? ?? '',
            drop: extra['drop'] as String? ?? '',
          );
        },
      ),
      GoRoute(
        path: AppRoutes.rideConfirm,
        builder: (_, state) {
          final extra = state.extra as Map<String, dynamic>? ?? {};
          return RideConfirmScreen(
            rideType: extra['rideType'] as String? ?? 'bike',
            pickup: extra['pickup'] as String? ?? '',
            drop: extra['drop'] as String? ?? '',
            fare: extra['fare'] as double? ?? 0,
            vehicleName: extra['vehicleName'] as String? ?? '',
          );
        },
      ),
      GoRoute(
        path: AppRoutes.rideTracking,
        builder: (_, state) {
          final extra = state.extra as Map<String, dynamic>? ?? {};
          return RideTrackingScreen(
            rideId: extra['rideId'] as String? ?? 'RR001',
            rideType: extra['rideType'] as String? ?? 'bike',
            pickup: extra['pickup'] as String? ?? '',
            drop: extra['drop'] as String? ?? '',
          );
        },
      ),
      GoRoute(
        path: AppRoutes.wallet,
        builder: (_, __) => const WalletScreen(),
      ),
      GoRoute(
        path: AppRoutes.trips,
        builder: (_, __) => const TripsScreen(),
      ),
      GoRoute(
        path: AppRoutes.profile,
        builder: (_, __) => const ProfileScreen(),
      ),
      GoRoute(
        path: AppRoutes.notifications,
        builder: (_, __) => const NotificationsScreen(),
      ),
    ],
    errorBuilder: (context, state) => Scaffold(
      body: Center(
        child: Text('Page not found: ${state.uri}'),
      ),
    ),
  );
});
