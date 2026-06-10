import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../domain/entities/train.dart';
import '../../domain/repositories/railway_repository.dart';
import '../datasources/railway_local_datasource.dart';

class RailwayRepositoryImpl implements RailwayRepository {
  RailwayRepositoryImpl(this._localDataSource);

  final RailwayLocalDataSource _localDataSource;

  @override
  Future<List<Train>> searchTrains({
    required String from,
    required String to,
    required DateTime date,
  }) async {
    await Future<void>.delayed(const Duration(milliseconds: 500));
    return _localDataSource.getMockTrains(from: from, to: to, date: date);
  }

  @override
  Future<PnrStatus> getPnrStatus(String pnr) async {
    await Future<void>.delayed(const Duration(milliseconds: 400));
    return _localDataSource.getMockPnrStatus(pnr);
  }

  @override
  Future<List<Station>> searchStations(String query) async {
    return _localDataSource.getMockStations(query);
  }

  @override
  Future<List<Map<String, dynamic>>> getTrainSchedule(String trainNumber) async {
    return _localDataSource.getMockSchedule(trainNumber);
  }

  @override
  Future<List<Map<String, dynamic>>> getLiveStatus(String trainNumber) async {
    return _localDataSource.getMockLiveStatus(trainNumber);
  }

  @override
  List<Map<String, String>> getFavorites() => _localDataSource.getMockFavorites();
}

final railwayRepositoryProvider = Provider<RailwayRepository>((ref) {
  return RailwayRepositoryImpl(RailwayLocalDataSource());
});
