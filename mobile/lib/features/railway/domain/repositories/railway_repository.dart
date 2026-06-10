import '../entities/train.dart';

abstract class RailwayRepository {
  Future<List<Train>> searchTrains({
    required String from,
    required String to,
    required DateTime date,
  });
  Future<PnrStatus> getPnrStatus(String pnr);
  Future<List<Station>> searchStations(String query);
  Future<List<Map<String, dynamic>>> getTrainSchedule(String trainNumber);
  Future<List<Map<String, dynamic>>> getLiveStatus(String trainNumber);
  List<Map<String, String>> getFavorites();
}
