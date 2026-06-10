import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/datasources/rides_local_datasource.dart';
import '../../domain/entities/ride.dart';

final ridesLocalDataSourceProvider = Provider<RidesLocalDataSource>(
  (ref) => RidesLocalDataSource(),
);

class RideBookingState {
  const RideBookingState({
    this.pickup = '',
    this.drop = '',
    this.estimates = const [],
    this.isLoading = false,
    this.selectedEstimate,
  });

  final String pickup;
  final String drop;
  final List<RideEstimate> estimates;
  final bool isLoading;
  final RideEstimate? selectedEstimate;

  RideBookingState copyWith({
    String? pickup,
    String? drop,
    List<RideEstimate>? estimates,
    bool? isLoading,
    RideEstimate? selectedEstimate,
    bool clearEstimate = false,
  }) {
    return RideBookingState(
      pickup: pickup ?? this.pickup,
      drop: drop ?? this.drop,
      estimates: estimates ?? this.estimates,
      isLoading: isLoading ?? this.isLoading,
      selectedEstimate:
          clearEstimate ? null : (selectedEstimate ?? this.selectedEstimate),
    );
  }
}

class RideBookingNotifier extends StateNotifier<RideBookingState> {
  RideBookingNotifier(this._dataSource) : super(const RideBookingState());

  final RidesLocalDataSource _dataSource;

  void setPickup(String value) => state = state.copyWith(pickup: value);
  void setDrop(String value) => state = state.copyWith(drop: value);

  void selectEstimate(RideEstimate estimate) {
    state = state.copyWith(selectedEstimate: estimate);
  }

  Future<List<RideEstimate>> getEstimates(String rideType) async {
    state = state.copyWith(isLoading: true);
    await Future<void>.delayed(const Duration(milliseconds: 600));
    final estimates = _dataSource.getEstimates(rideType);
    state = state.copyWith(isLoading: false, estimates: estimates);
    return estimates;
  }

  void reset() => state = const RideBookingState();
}

final rideBookingProvider =
    StateNotifierProvider<RideBookingNotifier, RideBookingState>((ref) {
  return RideBookingNotifier(ref.watch(ridesLocalDataSourceProvider));
});

final activeRideProvider = StateProvider<ActiveRide?>((ref) => null);
