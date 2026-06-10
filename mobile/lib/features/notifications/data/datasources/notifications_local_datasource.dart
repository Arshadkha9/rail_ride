import '../../domain/entities/notification.dart';

class NotificationsLocalDataSource {
  List<AppNotification> getNotifications() {
    return [
      AppNotification(
        id: 'N001',
        title: 'Driver arriving soon',
        body: 'Rajesh is 3 minutes away from your pickup location.',
        type: NotificationType.ride,
        createdAt: DateTime.now().subtract(const Duration(minutes: 5)),
        actionRoute: '/rides/tracking',
      ),
      AppNotification(
        id: 'N002',
        title: 'PNR Status Updated',
        body: 'Your PNR 4521789630 is now confirmed. Chart not prepared.',
        type: NotificationType.railway,
        createdAt: DateTime.now().subtract(const Duration(hours: 2)),
      ),
      AppNotification(
        id: 'N003',
        title: '₹50 Cashback credited',
        body: 'You earned cashback on your last bike ride.',
        type: NotificationType.wallet,
        createdAt: DateTime.now().subtract(const Duration(hours: 5)),
        isRead: true,
      ),
      AppNotification(
        id: 'N004',
        title: 'Weekend offer!',
        body: 'Get 20% off on your next taxi ride. Use code RIDE20.',
        type: NotificationType.promo,
        createdAt: DateTime.now().subtract(const Duration(days: 1)),
      ),
      AppNotification(
        id: 'N005',
        title: 'App updated',
        body: 'RailRide v1.0.0 is now available with new features.',
        type: NotificationType.system,
        createdAt: DateTime.now().subtract(const Duration(days: 2)),
        isRead: true,
      ),
    ];
  }
}
