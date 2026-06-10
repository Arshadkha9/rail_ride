import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/widgets/app_scaffold.dart';
import '../../../../core/widgets/empty_state.dart';
import '../../domain/entities/trip.dart';
import '../providers/trips_provider.dart';

class TripsScreen extends ConsumerWidget {
  const TripsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final trips = ref.watch(tripsProvider);
    final filter = ref.watch(tripFilterProvider);

    return AppScaffold(
      title: 'My Trips',
      body: Column(
        children: [
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: TripFilter.values.map((f) {
                final isSelected = filter == f;
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: FilterChip(
                    label: Text(_filterLabel(f)),
                    selected: isSelected,
                    onSelected: (_) =>
                        ref.read(tripFilterProvider.notifier).state = f,
                  ),
                );
              }).toList(),
            ),
          ),
          const SizedBox(height: 16),
          Expanded(
            child: trips.isEmpty
                ? const EmptyState(
                    icon: Icons.luggage_outlined,
                    title: 'No trips found',
                    message: 'Your journeys will appear here',
                  )
                : ListView.builder(
                    itemCount: trips.length,
                    itemBuilder: (context, index) =>
                        _TripCard(trip: trips[index]),
                  ),
          ),
        ],
      ),
    );
  }

  String _filterLabel(TripFilter filter) => switch (filter) {
        TripFilter.all => 'All',
        TripFilter.upcoming => 'Upcoming',
        TripFilter.completed => 'Completed',
        TripFilter.cancelled => 'Cancelled',
      };
}

class _TripCard extends StatelessWidget {
  const _TripCard({required this.trip});

  final Trip trip;

  Color get _typeColor => switch (trip.type) {
        TripType.railway => AppColors.railway,
        TripType.bike => AppColors.bike,
        TripType.auto => AppColors.auto,
        TripType.taxi => AppColors.taxi,
      };

  IconData get _typeIcon => switch (trip.type) {
        TripType.railway => Icons.train_rounded,
        TripType.bike => Icons.two_wheeler_rounded,
        TripType.auto => Icons.electric_rickshaw_rounded,
        TripType.taxi => Icons.local_taxi_rounded,
      };

  Color get _statusColor => switch (trip.status) {
        TripStatus.upcoming => AppColors.primary,
        TripStatus.completed => AppColors.success,
        TripStatus.cancelled => AppColors.error,
      };

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: _typeColor.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(_typeIcon, color: _typeColor, size: 22),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        trip.title,
                        style: const TextStyle(fontWeight: FontWeight.w600),
                      ),
                      Text(
                        DateFormat('dd MMM yyyy, hh:mm a').format(trip.date),
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: _statusColor.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    trip.status.name.capitalize(),
                    style: TextStyle(
                      color: _statusColor,
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
            const Divider(height: 24),
            Row(
              children: [
                const Icon(Icons.trip_origin, size: 16, color: AppColors.success),
                const SizedBox(width: 8),
                Expanded(child: Text(trip.from, style: const TextStyle(fontSize: 13))),
              ],
            ),
            const SizedBox(height: 4),
            Row(
              children: [
                const Icon(Icons.location_on, size: 16, color: AppColors.error),
                const SizedBox(width: 8),
                Expanded(child: Text(trip.to, style: const TextStyle(fontSize: 13))),
              ],
            ),
            if (trip.details != null) ...[
              const SizedBox(height: 8),
              Text(
                trip.details!,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Theme.of(context)
                          .colorScheme
                          .onSurface
                          .withValues(alpha: 0.6),
                    ),
              ),
            ],
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '₹${trip.amount.toStringAsFixed(0)}',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                if (trip.status == TripStatus.upcoming)
                  TextButton(
                    onPressed: () {},
                    child: const Text('View Details'),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

extension on String {
  String capitalize() =>
      isEmpty ? this : '${this[0].toUpperCase()}${substring(1)}';
}
