import '../../domain/entities/wallet.dart';

class WalletLocalDataSource {
  WalletBalance getBalance() {
    return const WalletBalance(balance: 2450, currency: 'INR');
  }

  List<Transaction> getTransactions() {
    return [
      Transaction(
        id: 'TXN001',
        title: 'Bike ride - Connaught Place',
        amount: 45,
        type: TransactionType.debit,
        date: DateTime(2026, 6, 8, 14, 30),
        status: 'Completed',
      ),
      Transaction(
        id: 'TXN002',
        title: 'Added money via UPI',
        amount: 500,
        type: TransactionType.credit,
        date: DateTime(2026, 6, 7, 10, 15),
        status: 'Completed',
      ),
      Transaction(
        id: 'TXN003',
        title: 'Train booking - Rajdhani Express',
        amount: 2150,
        type: TransactionType.debit,
        date: DateTime(2026, 6, 5, 18, 45),
        status: 'Completed',
      ),
      Transaction(
        id: 'TXN004',
        title: 'Auto ride - Karol Bagh',
        amount: 89,
        type: TransactionType.debit,
        date: DateTime(2026, 6, 4, 9, 20),
        status: 'Completed',
      ),
      Transaction(
        id: 'TXN005',
        title: 'Cashback reward',
        amount: 50,
        type: TransactionType.credit,
        date: DateTime(2026, 6, 3, 12, 0),
        status: 'Completed',
      ),
    ];
  }
}
