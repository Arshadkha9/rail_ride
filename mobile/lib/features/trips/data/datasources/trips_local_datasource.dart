import '../../domain/entities/trip.dart';

class TripsLocalDataSource {
  List<Trip> getTrips() {
    return [
      Trip(
        id: 'TRP001',
        type: TripType.railway,
        title: 'Rajdhani Express',
        from: 'New Delhi',
        to: 'Mumbai Central',
        date: DateTime(2026, 6, 15, 16, 25),
        status: TripStatus.upcoming,
        amount: 2150,
        details: 'PNR: 4521789630 • 3A',
      ),
      Trip(
        id: 'TRP002',
        type: TripType.bike,
        title: 'Bike Ride',
        from: 'Connaught Place',
        to: 'India Gate',
        date: DateTime(2026, 6, 8, 14, 30),
        status: TripStatus.completed,
        amount: 45,
      ),
      Trip(
        id: 'TRP003',
        type: TripType.auto,
        title: 'Auto Ride',
        from: 'Karol Bagh',
        to: 'Rajiv Chowk',
        date: DateTime(2026, 6, 4, 9, 20),
        status: TripStatus.completed,
        amount: 89,
      ),
      Trip(
        id: 'TRP004',
        type: TripType.taxi,
        title: 'Taxi Ride',
        from: 'IGI Airport T3',
        to: 'Gurgaon',
        date: DateTime(2026, 5, 28, 22, 15),
        status: TripStatus.completed,
        amount: 549,
      ),
      Trip(
        id: 'TRP005',
        type: TripType.railway,
        title: 'Duronto Express',
        from: 'Bangalore',
        to: 'Chennai',
        date: DateTime(2026, 5, 20, 23, 0),
        status: TripStatus.cancelled,
        amount: 890,
        details: 'Refund processed',
      ),
    ];
  }
}
