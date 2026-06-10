import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/router/app_router.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/widgets/app_scaffold.dart';

class RailwayHomeScreen extends StatelessWidget {
  const RailwayHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final items = [
      _RailwayMenuItem(
        title: 'Train Search',
        subtitle: 'Find trains between stations',
        icon: Icons.search_rounded,
        color: AppColors.railway,
        route: AppRoutes.trainSearch,
      ),
      _RailwayMenuItem(
        title: 'PNR Status',
        subtitle: 'Check your booking status',
        icon: Icons.confirmation_number_rounded,
        color: AppColors.secondary,
        route: AppRoutes.pnrStatus,
      ),
      _RailwayMenuItem(
        title: 'Live Train Status',
        subtitle: 'Real-time running status',
        icon: Icons.gps_fixed_rounded,
        color: AppColors.accent,
        route: AppRoutes.liveStatus,
      ),
      _RailwayMenuItem(
        title: 'Train Schedule',
        subtitle: 'View complete route schedule',
        icon: Icons.schedule_rounded,
        color: AppColors.trips,
        route: AppRoutes.trainSchedule,
      ),
      _RailwayMenuItem(
        title: 'Station Search',
        subtitle: 'Find stations by name or code',
        icon: Icons.location_on_rounded,
        color: AppColors.auto,
        route: AppRoutes.stationSearch,
      ),
      _RailwayMenuItem(
        title: 'Favorites',
        subtitle: 'Your saved routes',
        icon: Icons.favorite_rounded,
        color: AppColors.notifications,
        route: AppRoutes.favorites,
      ),
    ];

    return AppScaffold(
      title: 'Railway',
      body: ListView.separated(
        itemCount: items.length,
        separatorBuilder: (_, __) => const SizedBox(height: 12),
        itemBuilder: (context, index) {
          final item = items[index];
          return Card(
            child: ListTile(
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 16,
                vertical: 8,
              ),
              leading: Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: item.color.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(item.icon, color: item.color),
              ),
              title: Text(
                item.title,
                style: const TextStyle(fontWeight: FontWeight.w600),
              ),
              subtitle: Text(item.subtitle),
              trailing: const Icon(Icons.chevron_right_rounded),
              onTap: () => context.push(item.route),
            ),
          );
        },
      ),
    );
  }
}

class _RailwayMenuItem {
  const _RailwayMenuItem({
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.color,
    required this.route,
  });

  final String title;
  final String subtitle;
  final IconData icon;
  final Color color;
  final String route;
}
