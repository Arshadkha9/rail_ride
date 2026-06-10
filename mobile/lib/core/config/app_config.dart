class AppConfig {
  AppConfig._();

  static const String appName = 'RailRide';
  static const String apiBaseUrl = 'https://api.railride.app/v1';
  static const Duration connectTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
  static const String googleMapsApiKey = 'YOUR_GOOGLE_MAPS_API_KEY';
}
