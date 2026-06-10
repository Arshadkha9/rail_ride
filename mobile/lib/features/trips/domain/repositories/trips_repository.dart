import '../entities/trip.dart';

abstract class TripsRepository {
  List<Trip> getTrips();
}
