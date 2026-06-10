import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/router/app_router.dart';
import '../../../../core/theme/app_colors.dart';
import '../../domain/entities/dashboard_module.dart';

abstract class HomeRepository {
  List<DashboardModule> getDashboardModules();
}

class HomeRepositoryImpl implements HomeRepository {
  @override
  List<DashboardModule> getDashboardModules() {
    return const [
      DashboardModule(
        id: 'railway',
        title: 'Railway',
        subtitle: 'Trains, PNR & live status',
        icon: Icons.train_rounded,
        color: AppColors.railway,
        route: AppRoutes.railway,
      ),
      DashboardModule(
        id: 'bike',
        title: 'Bike',
        subtitle: 'Quick two-wheeler rides',
        icon: Icons.two_wheeler_rounded,
        color: AppColors.bike,
        route: '${AppRoutes.rideBooking}?type=bike',
      ),
      DashboardModule(
        id: 'auto',
        title: 'Auto',
        subtitle: 'Affordable auto rickshaw',
        icon: Icons.electric_rickshaw_rounded,
        color: AppColors.auto,
        route: '${AppRoutes.rideBooking}?type=auto',
      ),
      DashboardModule(
        id: 'taxi',
        title: 'Taxi',
        subtitle: 'Comfortable cab rides',
        icon: Icons.local_taxi_rounded,
        color: AppColors.taxi,
        route: '${AppRoutes.rideBooking}?type=taxi',
      ),
      DashboardModule(
        id: 'wallet',
        title: 'Wallet',
        subtitle: 'Balance & transactions',
        icon: Icons.account_balance_wallet_rounded,
        color: AppColors.wallet,
        route: AppRoutes.wallet,
        badge: '₹2,450',
      ),
      DashboardModule(
        id: 'trips',
        title: 'My Trips',
        subtitle: 'Past & upcoming journeys',
        icon: Icons.luggage_rounded,
        color: AppColors.trips,
        route: AppRoutes.trips,
      ),
      DashboardModule(
        id: 'notifications',
        title: 'Notifications',
        subtitle: 'Alerts & updates',
        icon: Icons.notifications_active_rounded,
        color: AppColors.notifications,
        route: AppRoutes.notifications,
        badge: '3',
      ),
      DashboardModule(
        id: 'profile',
        title: 'Profile',
        subtitle: 'Account & settings',
        icon: Icons.person_rounded,
        color: AppColors.profile,
        route: AppRoutes.profile,
      ),
    ];
  }
}

final homeRepositoryProvider = Provider<HomeRepository>((ref) {
  return HomeRepositoryImpl();
});
