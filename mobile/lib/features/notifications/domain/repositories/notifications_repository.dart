import '../entities/notification.dart';

abstract class NotificationsRepository {
  List<AppNotification> getNotifications();
  void markAsRead(String id);
  void markAllAsRead();
}
