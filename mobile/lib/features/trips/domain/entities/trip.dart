import 'package:equatable/equatable.dart';

enum TripType { railway, bike, auto, taxi }

enum TripStatus { upcoming, completed, cancelled }

class Trip extends Equatable {
  const Trip({
    required this.id,
    required this.type,
    required this.title,
    required this.from,
    required this.to,
    required this.date,
    required this.status,
    required this.amount,
    this.details,
  });

  final String id;
  final TripType type;
  final String title;
  final String from;
  final String to;
  final DateTime date;
  final TripStatus status;
  final double amount;
  final String? details;

  @override
  List<Object?> get props =>
      [id, type, title, from, to, date, status, amount, details];
}
