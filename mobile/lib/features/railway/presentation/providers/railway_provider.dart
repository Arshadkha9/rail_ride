import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/datasources/railway_local_datasource.dart';
import '../../domain/entities/train.dart';

final railwayLocalDataSourceProvider = Provider<RailwayLocalDataSource>(
  (ref) => RailwayLocalDataSource(),
);

class TrainSearchState {
  const TrainSearchState({
    this.from = '',
    this.to = '',
    this.date,
    this.trains = const [],
    this.isLoading = false,
    this.searched = false,
  });

  final String from;
  final String to;
  final DateTime? date;
  final List<Train> trains;
  final bool isLoading;
  final bool searched;

  TrainSearchState copyWith({
    String? from,
    String? to,
    DateTime? date,
    List<Train>? trains,
    bool? isLoading,
    bool? searched,
  }) {
    return TrainSearchState(
      from: from ?? this.from,
      to: to ?? this.to,
      date: date ?? this.date,
      trains: trains ?? this.trains,
      isLoading: isLoading ?? this.isLoading,
      searched: searched ?? this.searched,
    );
  }
}

class TrainSearchNotifier extends StateNotifier<TrainSearchState> {
  TrainSearchNotifier(this._dataSource)
      : super(TrainSearchState(date: DateTime.now()));

  final RailwayLocalDataSource _dataSource;

  void setFrom(String value) => state = state.copyWith(from: value);
  void setTo(String value) => state = state.copyWith(to: value);
  void setDate(DateTime value) => state = state.copyWith(date: value);

  void swapStations() {
    state = state.copyWith(from: state.to, to: state.from);
  }

  Future<void> search() async {
    if (state.from.isEmpty || state.to.isEmpty) return;
    state = state.copyWith(isLoading: true);
    await Future<void>.delayed(const Duration(milliseconds: 800));
    final trains = _dataSource.getMockTrains(
      from: state.from,
      to: state.to,
      date: state.date ?? DateTime.now(),
    );
    state = state.copyWith(
      isLoading: false,
      trains: trains,
      searched: true,
    );
  }
}

final trainSearchProvider =
    StateNotifierProvider<TrainSearchNotifier, TrainSearchState>((ref) {
  return TrainSearchNotifier(ref.watch(railwayLocalDataSourceProvider));
});

final stationSearchProvider =
    StateNotifierProvider<StationSearchNotifier, List<Station>>((ref) {
  return StationSearchNotifier(ref.watch(railwayLocalDataSourceProvider));
});

class StationSearchNotifier extends StateNotifier<List<Station>> {
  StationSearchNotifier(this._dataSource) : super([]);

  final RailwayLocalDataSource _dataSource;

  void search(String query) {
    state = _dataSource.getMockStations(query);
  }
}

final pnrProvider =
    StateNotifierProvider<PnrNotifier, AsyncValue<PnrStatus?>>((ref) {
  return PnrNotifier(ref.watch(railwayLocalDataSourceProvider));
});

class PnrNotifier extends StateNotifier<AsyncValue<PnrStatus?>> {
  PnrNotifier(this._dataSource) : super(const AsyncValue.data(null));

  final RailwayLocalDataSource _dataSource;

  Future<void> checkPnr(String pnr) async {
    state = const AsyncValue.loading();
    await Future<void>.delayed(const Duration(milliseconds: 600));
    state = AsyncValue.data(_dataSource.getMockPnrStatus(pnr));
  }

  void clear() => state = const AsyncValue.data(null);
}
