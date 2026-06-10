import 'package:equatable/equatable.dart';

class Train extends Equatable {
  const Train({
    required this.number,
    required this.name,
    required this.from,
    required this.to,
    required this.departure,
    required this.arrival,
    required this.duration,
    required this.classes,
  });

  final String number;
  final String name;
  final String from;
  final String to;
  final String departure;
  final String arrival;
  final String duration;
  final List<TrainClass> classes;

  @override
  List<Object?> get props =>
      [number, name, from, to, departure, arrival, duration, classes];
}

class TrainClass extends Equatable {
  const TrainClass({
    required this.code,
    required this.name,
    required this.fare,
    required this.availability,
  });

  final String code;
  final String name;
  final double fare;
  final String availability;

  @override
  List<Object?> get props => [code, name, fare, availability];
}

class Station extends Equatable {
  const Station({
    required this.code,
    required this.name,
    required this.state,
  });

  final String code;
  final String name;
  final String state;

  @override
  List<Object?> get props => [code, name, state];
}

class PnrStatus extends Equatable {
  const PnrStatus({
    required this.pnr,
    required this.trainNumber,
    required this.trainName,
    required this.from,
    required this.to,
    required this.journeyDate,
    required this.bookingStatus,
    required this.currentStatus,
    required this.passengers,
    required this.chartPrepared,
  });

  final String pnr;
  final String trainNumber;
  final String trainName;
  final String from;
  final String to;
  final String journeyDate;
  final String bookingStatus;
  final String currentStatus;
  final List<PassengerStatus> passengers;
  final bool chartPrepared;

  @override
  List<Object?> get props => [
        pnr,
        trainNumber,
        trainName,
        from,
        to,
        journeyDate,
        bookingStatus,
        currentStatus,
        passengers,
        chartPrepared,
      ];
}

class PassengerStatus extends Equatable {
  const PassengerStatus({
    required this.name,
    required this.bookingStatus,
    required this.currentStatus,
  });

  final String name;
  final String bookingStatus;
  final String currentStatus;

  @override
  List<Object?> get props => [name, bookingStatus, currentStatus];
}
