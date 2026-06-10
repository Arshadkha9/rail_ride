import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/providers/theme_provider.dart';
import '../../../../core/router/app_router.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/widgets/dashboard_card.dart';
import '../../../auth/presentation/providers/auth_provider.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(authStateProvider).user;
    final themeMode = ref.watch(themeModeProvider);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final width = MediaQuery.sizeOf(context).width;
    final crossAxisCount = width > 600 ? 3 : 2;
    final aspectRatio = width > 600 ? 1.3 : 1.1;

    return Scaffold(
      body: SafeArea(
        child: CustomScrollView(
          slivers: [
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(20, 16, 20, 8),
                child: Row(
                  children: [
                    CircleAvatar(
                      radius: 24,
                      backgroundColor: AppColors.primary.withValues(alpha: 0.15),
                      child: Text(
                        (user?.name.isNotEmpty == true
                                ? user!.name[0]
                                : 'R')
                            .toUpperCase(),
                        style: const TextStyle(
                          color: AppColors.primary,
                          fontWeight: FontWeight.bold,
                          fontSize: 20,
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Hello, ${user?.name.split(' ').first ?? 'Traveler'}!',
                            style: Theme.of(context)
                                .textTheme
                                .titleLarge
                                ?.copyWith(fontWeight: FontWeight.bold),
                          ),
                          Text(
                            'Where would you like to go?',
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                  color: Theme.of(context)
                                      .colorScheme
                                      .onSurface
                                      .withValues(alpha: 0.6),
                                ),
                          ),
                        ],
                      ),
                    ),
                    IconButton(
                      icon: Icon(
                        themeMode == ThemeMode.dark
                            ? Icons.light_mode_rounded
                            : Icons.dark_mode_rounded,
                      ),
                      onPressed: () =>
                          ref.read(themeModeProvider.notifier).toggleTheme(),
                    ),
                    IconButton(
                      icon: const Icon(Icons.notifications_outlined),
                      onPressed: () => context.push(AppRoutes.notifications),
                    ),
                  ],
                ),
              ),
            ),
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
                child: Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        AppColors.primary,
                        AppColors.primary.withValues(alpha: 0.8),
                      ],
                    ),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Book your next trip',
                              style: Theme.of(context)
                                  .textTheme
                                  .titleMedium
                                  ?.copyWith(
                                    color: Colors.white,
                                    fontWeight: FontWeight.bold,
                                  ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'Trains, bikes, autos & taxis — all in one app',
                              style: Theme.of(context)
                                  .textTheme
                                  .bodySmall
                                  ?.copyWith(color: Colors.white70),
                            ),
                          ],
                        ),
                      ),
                      const Icon(
                        Icons.arrow_forward_ios_rounded,
                        color: Colors.white70,
                        size: 20,
                      ),
                    ],
                  ),
                ),
              ),
            ),
            SliverPadding(
              padding: const EdgeInsets.all(20),
              sliver: SliverGrid(
                gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: crossAxisCount,
                  mainAxisSpacing: 16,
                  crossAxisSpacing: 16,
                  childAspectRatio: aspectRatio,
                ),
                delegate: SliverChildListDelegate([
                  DashboardCard(
                    title: 'Railway',
                    subtitle: 'Trains, PNR & live status',
                    icon: Icons.train_rounded,
                    color: AppColors.railway,
                    onTap: () => context.push(AppRoutes.railway),
                  ),
                  DashboardCard(
                    title: 'Bike',
                    subtitle: 'Quick two-wheeler rides',
                    icon: Icons.two_wheeler_rounded,
                    color: AppColors.bike,
                    onTap: () => context.push(
                      '${AppRoutes.rideBooking}?type=bike',
                    ),
                  ),
                  DashboardCard(
                    title: 'Auto',
                    subtitle: 'Affordable auto rickshaw',
                    icon: Icons.electric_rickshaw_rounded,
                    color: AppColors.auto,
                    onTap: () => context.push(
                      '${AppRoutes.rideBooking}?type=auto',
                    ),
                  ),
                  DashboardCard(
                    title: 'Taxi',
                    subtitle: 'Comfortable cab rides',
                    icon: Icons.local_taxi_rounded,
                    color: AppColors.taxi,
                    onTap: () => context.push(
                      '${AppRoutes.rideBooking}?type=taxi',
                    ),
                  ),
                  DashboardCard(
                    title: 'Wallet',
                    subtitle: 'Balance & transactions',
                    icon: Icons.account_balance_wallet_rounded,
                    color: AppColors.wallet,
                    badge: '₹2,450',
                    onTap: () => context.push(AppRoutes.wallet),
                  ),
                  DashboardCard(
                    title: 'My Trips',
                    subtitle: 'Past & upcoming journeys',
                    icon: Icons.luggage_rounded,
                    color: AppColors.trips,
                    onTap: () => context.push(AppRoutes.trips),
                  ),
                  DashboardCard(
                    title: 'Notifications',
                    subtitle: 'Alerts & updates',
                    icon: Icons.notifications_active_rounded,
                    color: AppColors.notifications,
                    badge: '3',
                    onTap: () => context.push(AppRoutes.notifications),
                  ),
                  DashboardCard(
                    title: 'Profile',
                    subtitle: 'Account & settings',
                    icon: Icons.person_rounded,
                    color: AppColors.profile,
                    onTap: () => context.push(AppRoutes.profile),
                  ),
                ]),
              ),
            ),
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(20, 0, 20, 24),
                child: Text(
                  'RailRide v1.0.0',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Theme.of(context)
                            .colorScheme
                            .onSurface
                            .withValues(alpha: isDark ? 0.4 : 0.5),
                      ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
