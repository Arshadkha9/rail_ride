import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/datasources/trips_local_datasource.dart';
import '../../domain/entities/trip.dart';

final tripsLocalDataSourceProvider = Provider<TripsLocalDataSource>(
  (ref) => TripsLocalDataSource(),
);

enum TripFilter { all, upcoming, completed, cancelled }

final tripFilterProvider = StateProvider<TripFilter>((ref) => TripFilter.all);

final tripsProvider = Provider<List<Trip>>((ref) {
  final allTrips = ref.watch(tripsLocalDataSourceProvider).getTrips();
  final filter = ref.watch(tripFilterProvider);

  return switch (filter) {
    TripFilter.all => allTrips,
    TripFilter.upcoming =>
      allTrips.where((t) => t.status == TripStatus.upcoming).toList(),
    TripFilter.completed =>
      allTrips.where((t) => t.status == TripStatus.completed).toList(),
    TripFilter.cancelled =>
      allTrips.where((t) => t.status == TripStatus.cancelled).toList(),
  };
});
