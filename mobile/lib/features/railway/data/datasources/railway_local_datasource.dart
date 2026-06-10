import '../../domain/entities/train.dart';

class RailwayLocalDataSource {
  List<Train> getMockTrains({
    required String from,
    required String to,
    required DateTime date,
  }) {
    return [
      Train(
        number: '12951',
        name: 'Rajdhani Express',
        from: from,
        to: to,
        departure: '16:25',
        arrival: '08:15',
        duration: '15h 50m',
        classes: const [
          TrainClass(code: 'SL', name: 'Sleeper', fare: 850, availability: 'WL 12'),
          TrainClass(code: '3A', name: 'AC 3 Tier', fare: 2150, availability: 'AVAILABLE 45'),
          TrainClass(code: '2A', name: 'AC 2 Tier', fare: 3200, availability: 'RAC 3'),
          TrainClass(code: '1A', name: 'AC First', fare: 5400, availability: 'AVAILABLE 8'),
        ],
      ),
      Train(
        number: '12259',
        name: 'Duronto Express',
        from: from,
        to: to,
        departure: '23:00',
        arrival: '15:30',
        duration: '16h 30m',
        classes: const [
          TrainClass(code: 'SL', name: 'Sleeper', fare: 720, availability: 'AVAILABLE 120'),
          TrainClass(code: '3A', name: 'AC 3 Tier', fare: 1890, availability: 'AVAILABLE 32'),
          TrainClass(code: '2A', name: 'AC 2 Tier', fare: 2750, availability: 'WL 5'),
        ],
      ),
      Train(
        number: '12627',
        name: 'Karnataka Express',
        from: from,
        to: to,
        departure: '07:10',
        arrival: '04:45',
        duration: '21h 35m',
        classes: const [
          TrainClass(code: 'SL', name: 'Sleeper', fare: 680, availability: 'AVAILABLE 200'),
          TrainClass(code: '3A', name: 'AC 3 Tier', fare: 1750, availability: 'AVAILABLE 18'),
        ],
      ),
    ];
  }

  List<Station> getMockStations(String query) {
    const allStations = [
      Station(code: 'NDLS', name: 'New Delhi', state: 'Delhi'),
      Station(code: 'BCT', name: 'Mumbai Central', state: 'Maharashtra'),
      Station(code: 'CSMT', name: 'Mumbai CSMT', state: 'Maharashtra'),
      Station(code: 'HWH', name: 'Howrah Junction', state: 'West Bengal'),
      Station(code: 'SBC', name: 'Bangalore City', state: 'Karnataka'),
      Station(code: 'MAS', name: 'Chennai Central', state: 'Tamil Nadu'),
      Station(code: 'PNBE', name: 'Patna Junction', state: 'Bihar'),
      Station(code: 'LKO', name: 'Lucknow NR', state: 'Uttar Pradesh'),
      Station(code: 'JP', name: 'Jaipur Junction', state: 'Rajasthan'),
      Station(code: 'ADI', name: 'Ahmedabad Junction', state: 'Gujarat'),
    ];

    if (query.isEmpty) return allStations;
    final q = query.toLowerCase();
    return allStations
        .where((s) =>
            s.name.toLowerCase().contains(q) ||
            s.code.toLowerCase().contains(q))
        .toList();
  }

  PnrStatus getMockPnrStatus(String pnr) {
    return PnrStatus(
      pnr: pnr,
      trainNumber: '12951',
      trainName: 'Rajdhani Express',
      from: 'NDLS - New Delhi',
      to: 'BCT - Mumbai Central',
      journeyDate: '15 Jun 2026',
      bookingStatus: 'CNF/B2/42',
      currentStatus: 'CNF/B2/42',
      chartPrepared: false,
      passengers: const [
        PassengerStatus(
          name: 'Rahul Sharma',
          bookingStatus: 'CNF/B2/42',
          currentStatus: 'CNF/B2/42',
        ),
        PassengerStatus(
          name: 'Priya Sharma',
          bookingStatus: 'CNF/B2/43',
          currentStatus: 'CNF/B2/43',
        ),
      ],
    );
  }

  List<Map<String, dynamic>> getMockSchedule(String trainNumber) {
    return [
      {'station': 'New Delhi', 'arrival': '--', 'departure': '16:25', 'day': 1},
      {'station': 'Mathura Junction', 'arrival': '18:10', 'departure': '18:12', 'day': 1},
      {'station': 'Kota Junction', 'arrival': '21:45', 'departure': '21:50', 'day': 1},
      {'station': 'Ratlam Junction', 'arrival': '02:30', 'departure': '02:35', 'day': 2},
      {'station': 'Vadodara Junction', 'arrival': '06:15', 'departure': '06:20', 'day': 2},
      {'station': 'Mumbai Central', 'arrival': '08:15', 'departure': '--', 'day': 2},
    ];
  }

  List<Map<String, dynamic>> getMockLiveStatus(String trainNumber) {
    return [
      {'station': 'New Delhi', 'scheduled': '16:25', 'actual': '16:28', 'delay': '+3 min', 'passed': true},
      {'station': 'Mathura Junction', 'scheduled': '18:10', 'actual': '18:15', 'delay': '+5 min', 'passed': true},
      {'station': 'Kota Junction', 'scheduled': '21:45', 'actual': '21:52', 'delay': '+7 min', 'passed': false},
      {'station': 'Ratlam Junction', 'scheduled': '02:30', 'actual': '--', 'delay': '--', 'passed': false},
      {'station': 'Mumbai Central', 'scheduled': '08:15', 'actual': '--', 'delay': '--', 'passed': false},
    ];
  }

  List<Map<String, String>> getMockFavorites() {
    return [
      {'from': 'NDLS', 'to': 'BCT', 'label': 'Delhi → Mumbai'},
      {'from': 'SBC', 'to': 'MAS', 'label': 'Bangalore → Chennai'},
      {'from': 'HWH', 'to': 'PNBE', 'label': 'Kolkata → Patna'},
    ];
  }
}
