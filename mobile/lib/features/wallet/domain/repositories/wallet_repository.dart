import '../entities/wallet.dart';

abstract class WalletRepository {
  WalletBalance getBalance();
  List<Transaction> getTransactions();
  Future<bool> addMoney(double amount);
}
