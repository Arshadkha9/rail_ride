import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/datasources/wallet_local_datasource.dart';
import '../../domain/entities/wallet.dart';

final walletLocalDataSourceProvider = Provider<WalletLocalDataSource>(
  (ref) => WalletLocalDataSource(),
);

final walletBalanceProvider = Provider<WalletBalance>((ref) {
  return ref.watch(walletLocalDataSourceProvider).getBalance();
});

final transactionsProvider = Provider<List<Transaction>>((ref) {
  return ref.watch(walletLocalDataSourceProvider).getTransactions();
});

class AddMoneyNotifier extends StateNotifier<AsyncValue<void>> {
  AddMoneyNotifier() : super(const AsyncValue.data(null));

  Future<bool> addMoney(double amount) async {
    state = const AsyncValue.loading();
    await Future<void>.delayed(const Duration(seconds: 1));
    state = const AsyncValue.data(null);
    return true;
  }
}

final addMoneyProvider =
    StateNotifierProvider<AddMoneyNotifier, AsyncValue<void>>((ref) {
  return AddMoneyNotifier();
});
