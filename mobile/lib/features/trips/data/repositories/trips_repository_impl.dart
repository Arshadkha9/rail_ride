import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../domain/entities/trip.dart';
import '../../domain/repositories/trips_repository.dart';
import '../datasources/trips_local_datasource.dart';

class TripsRepositoryImpl implements TripsRepository {
  TripsRepositoryImpl(this._localDataSource);

  final TripsLocalDataSource _localDataSource;

  @override
  List<Trip> getTrips() => _localDataSource.getTrips();
}

final tripsRepositoryProvider = Provider<TripsRepository>((ref) {
  return TripsRepositoryImpl(TripsLocalDataSource());
});
