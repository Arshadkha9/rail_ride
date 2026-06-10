import '../../domain/entities/ride.dart';

class RidesLocalDataSource {
  List<RideEstimate> getEstimates(String rideType) {
    return switch (rideType) {
      'bike' => const [
          RideEstimate(
            vehicleType: 'bike',
            vehicleName: 'Bike - Standard',
            fare: 45,
            eta: '3 min',
            distance: '2.4 km',
          ),
          RideEstimate(
            vehicleType: 'bike',
            vehicleName: 'Bike - Premium',
            fare: 65,
            eta: '5 min',
            distance: '2.4 km',
          ),
        ],
      'auto' => const [
          RideEstimate(
            vehicleType: 'auto',
            vehicleName: 'Auto Rickshaw',
            fare: 89,
            eta: '4 min',
            distance: '2.4 km',
          ),
          RideEstimate(
            vehicleType: 'auto',
            vehicleName: 'Auto - Share',
            fare: 55,
            eta: '6 min',
            distance: '2.4 km',
          ),
        ],
      'taxi' => const [
          RideEstimate(
            vehicleType: 'taxi',
            vehicleName: 'Mini Sedan',
            fare: 149,
            eta: '5 min',
            distance: '2.4 km',
          ),
          RideEstimate(
            vehicleType: 'taxi',
            vehicleName: 'SUV Premium',
            fare: 249,
            eta: '7 min',
            distance: '2.4 km',
          ),
        ],
      _ => const [],
    };
  }

  ActiveRide getMockActiveRide({
    required String rideId,
    required String rideType,
    required String pickup,
    required String drop,
  }) {
    return ActiveRide(
      id: rideId,
      rideType: rideType,
      pickup: pickup,
      drop: drop,
      driverName: 'Rajesh Kumar',
      vehicleNumber: rideType == 'bike' ? 'DL 4S AB 1234' : 'DL 1C CD 5678',
      status: 'Driver is on the way',
      pickupLat: 28.6139,
      pickupLng: 77.2090,
      dropLat: 28.5355,
      dropLng: 77.3910,
      driverLat: 28.6200,
      driverLng: 77.2150,
    );
  }
}
