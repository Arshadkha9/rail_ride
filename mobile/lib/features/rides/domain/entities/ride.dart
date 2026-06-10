import 'package:equatable/equatable.dart';

class RideEstimate extends Equatable {
  const RideEstimate({
    required this.vehicleType,
    required this.vehicleName,
    required this.fare,
    required this.eta,
    required this.distance,
  });

  final String vehicleType;
  final String vehicleName;
  final double fare;
  final String eta;
  final String distance;

  @override
  List<Object?> get props => [vehicleType, vehicleName, fare, eta, distance];
}

class ActiveRide extends Equatable {
  const ActiveRide({
    required this.id,
    required this.rideType,
    required this.pickup,
    required this.drop,
    required this.driverName,
    required this.vehicleNumber,
    required this.status,
    required this.pickupLat,
    required this.pickupLng,
    required this.dropLat,
    required this.dropLng,
    required this.driverLat,
    required this.driverLng,
  });

  final String id;
  final String rideType;
  final String pickup;
  final String drop;
  final String driverName;
  final String vehicleNumber;
  final String status;
  final double pickupLat;
  final double pickupLng;
  final double dropLat;
  final double dropLng;
  final double driverLat;
  final double driverLng;

  @override
  List<Object?> get props => [
        id,
        rideType,
        pickup,
        drop,
        driverName,
        vehicleNumber,
        status,
        pickupLat,
        pickupLng,
        dropLat,
        dropLng,
        driverLat,
        driverLng,
      ];
}
