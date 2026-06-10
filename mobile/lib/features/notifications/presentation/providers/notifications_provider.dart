import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/datasources/notifications_local_datasource.dart';
import '../../domain/entities/notification.dart';

final notificationsLocalDataSourceProvider =
    Provider<NotificationsLocalDataSource>(
  (ref) => NotificationsLocalDataSource(),
);

class NotificationsNotifier extends StateNotifier<List<AppNotification>> {
  NotificationsNotifier(this._dataSource)
      : super(_dataSource.getNotifications());

  final NotificationsLocalDataSource _dataSource;

  void markAsRead(String id) {
    state = state
        .map((n) => n.id == id ? n.copyWith(isRead: true) : n)
        .toList();
  }

  void markAllAsRead() {
    state = state.map((n) => n.copyWith(isRead: true)).toList();
  }

  int get unreadCount => state.where((n) => !n.isRead).length;
}

final notificationsProvider =
    StateNotifierProvider<NotificationsNotifier, List<AppNotification>>((ref) {
  return NotificationsNotifier(ref.watch(notificationsLocalDataSourceProvider));
});

final unreadNotificationsCountProvider = Provider<int>((ref) {
  return ref.watch(notificationsProvider).where((n) => !n.isRead).length;
});
