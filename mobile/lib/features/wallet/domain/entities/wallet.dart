import 'package:equatable/equatable.dart';

class WalletBalance extends Equatable {
  const WalletBalance({
    required this.balance,
    required this.currency,
  });

  final double balance;
  final String currency;

  @override
  List<Object?> get props => [balance, currency];
}

class Transaction extends Equatable {
  const Transaction({
    required this.id,
    required this.title,
    required this.amount,
    required this.type,
    required this.date,
    required this.status,
  });

  final String id;
  final String title;
  final double amount;
  final TransactionType type;
  final DateTime date;
  final String status;

  @override
  List<Object?> get props => [id, title, amount, type, date, status];
}

enum TransactionType { credit, debit }
