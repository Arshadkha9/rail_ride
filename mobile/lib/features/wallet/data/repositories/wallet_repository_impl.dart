import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../domain/entities/wallet.dart';
import '../../domain/repositories/wallet_repository.dart';
import '../datasources/wallet_local_datasource.dart';

class WalletRepositoryImpl implements WalletRepository {
  WalletRepositoryImpl(this._localDataSource);

  final WalletLocalDataSource _localDataSource;

  @override
  WalletBalance getBalance() => _localDataSource.getBalance();

  @override
  List<Transaction> getTransactions() => _localDataSource.getTransactions();

  @override
  Future<bool> addMoney(double amount) async {
    await Future<void>.delayed(const Duration(seconds: 1));
    return true;
  }
}

final walletRepositoryProvider = Provider<WalletRepository>((ref) {
  return WalletRepositoryImpl(WalletLocalDataSource());
});
