class ApiEndpoints {
  ApiEndpoints._();

  // Auth
  static const String login = '/auth/login';
  static const String signup = '/auth/signup';
  static const String verifyOtp = '/auth/verify-otp';
  static const String refreshToken = '/auth/refresh';
  static const String logout = '/auth/logout';
  static const String resendOtp = '/auth/resend-otp';

  // Railway
  static const String trainSearch = '/railway/trains/search';
  static const String pnrStatus = '/railway/pnr';
  static const String liveStatus = '/railway/live-status';
  static const String trainSchedule = '/railway/schedule';
  static const String stationSearch = '/railway/stations/search';
  static const String favorites = '/railway/favorites';

  // Rides
  static const String rideEstimate = '/rides/estimate';
  static const String rideBook = '/rides/book';
  static const String rideTrack = '/rides/track';
  static const String rideCancel = '/rides/cancel';

  // Wallet
  static const String walletBalance = '/wallet/balance';
  static const String walletTransactions = '/wallet/transactions';
  static const String walletAddMoney = '/wallet/add-money';

  // Trips
  static const String trips = '/trips';
  static const String tripDetail = '/trips';

  // Profile
  static const String profile = '/profile';
  static const String updateProfile = '/profile';

  // Notifications
  static const String notifications = '/notifications';
  static const String markRead = '/notifications/read';
}
