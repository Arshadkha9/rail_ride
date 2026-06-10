import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../domain/entities/ride.dart';
import '../../domain/repositories/rides_repository.dart';
import '../datasources/rides_local_datasource.dart';

class RidesRepositoryImpl implements RidesRepository {
  RidesRepositoryImpl(this._localDataSource);

  final RidesLocalDataSource _localDataSource;

  @override
  Future<List<RideEstimate>> getEstimates(String rideType) async {
    await Future<void>.delayed(const Duration(milliseconds: 500));
    return _localDataSource.getEstimates(rideType);
  }

  @override
  Future<ActiveRide> bookRide({
    required String rideType,
    required String pickup,
    required String drop,
    required double fare,
  }) async {
    await Future<void>.delayed(const Duration(seconds: 1));
    return _localDataSource.getMockActiveRide(
      rideId: 'RR${DateTime.now().millisecondsSinceEpoch % 100000}',
      rideType: rideType,
      pickup: pickup,
      drop: drop,
    );
  }

  @override
  ActiveRide getActiveRide({
    required String rideId,
    required String rideType,
    required String pickup,
    required String drop,
  }) {
    return _localDataSource.getMockActiveRide(
      rideId: rideId,
      rideType: rideType,
      pickup: pickup,
      drop: drop,
    );
  }
}

final ridesRepositoryProvider = Provider<RidesRepository>((ref) {
  return RidesRepositoryImpl(RidesLocalDataSource());
});
