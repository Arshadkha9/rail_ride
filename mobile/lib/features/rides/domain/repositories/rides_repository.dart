import '../entities/ride.dart';

abstract class RidesRepository {
  Future<List<RideEstimate>> getEstimates(String rideType);
  Future<ActiveRide> bookRide({
    required String rideType,
    required String pickup,
    required String drop,
    required double fare,
  });
  ActiveRide getActiveRide({
    required String rideId,
    required String rideType,
    required String pickup,
    required String drop,
  });
}
