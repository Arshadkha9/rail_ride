import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../domain/entities/notification.dart';
import '../../domain/repositories/notifications_repository.dart';
import '../datasources/notifications_local_datasource.dart';

class NotificationsRepositoryImpl implements NotificationsRepository {
  NotificationsRepositoryImpl(this._localDataSource);

  final NotificationsLocalDataSource _localDataSource;
  late List<AppNotification> _notifications =
      _localDataSource.getNotifications();

  @override
  List<AppNotification> getNotifications() => List.unmodifiable(_notifications);

  @override
  void markAsRead(String id) {
    _notifications = _notifications
        .map((n) => n.id == id ? n.copyWith(isRead: true) : n)
        .toList();
  }

  @override
  void markAllAsRead() {
    _notifications =
        _notifications.map((n) => n.copyWith(isRead: true)).toList();
  }
}

final notificationsRepositoryProvider = Provider<NotificationsRepository>((ref) {
  return NotificationsRepositoryImpl(NotificationsLocalDataSource());
});
