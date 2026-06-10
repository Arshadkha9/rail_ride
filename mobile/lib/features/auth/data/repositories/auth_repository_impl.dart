import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../../../core/constants/app_constants.dart';
import '../../../../core/network/token_storage.dart';
import '../../domain/entities/user.dart';
import '../../domain/repositories/auth_repository.dart';
import '../datasources/auth_remote_datasource.dart';

class AuthRepositoryImpl implements AuthRepository {
  AuthRepositoryImpl(
    this._remoteDataSource,
    this._tokenStorage,
    this._prefs,
  );

  final AuthRemoteDataSource _remoteDataSource;
  final TokenStorage _tokenStorage;
  final SharedPreferences _prefs;
  User? _cachedUser;

  @override
  Future<User> login({required String email, required String password}) async {
    final result = await _remoteDataSource.login(
      email: email,
      password: password,
    );
    await _tokenStorage.saveTokens(
      accessToken: result.accessToken,
      refreshToken: result.refreshToken,
    );
    await _prefs.setString(AppConstants.userIdKey, result.user.id);
    _cachedUser = result.user.toEntity();
    return _cachedUser!;
  }

  @override
  Future<void> signup({
    required String name,
    required String email,
    required String phone,
    required String password,
  }) =>
      _remoteDataSource.signup(
        name: name,
        email: email,
        phone: phone,
        password: password,
      );

  @override
  Future<User> verifyOtp({required String phone, required String otp}) async {
    final result = await _remoteDataSource.verifyOtp(phone: phone, otp: otp);
    await _tokenStorage.saveTokens(
      accessToken: result.accessToken,
      refreshToken: result.refreshToken,
    );
    await _prefs.setString(AppConstants.userIdKey, result.user.id);
    _cachedUser = result.user.toEntity();
    return _cachedUser!;
  }

  @override
  Future<void> resendOtp({required String phone}) =>
      _remoteDataSource.resendOtp(phone: phone);

  @override
  Future<void> logout() async {
    try {
      await _remoteDataSource.logout();
    } finally {
      await _tokenStorage.clearTokens();
      _cachedUser = null;
    }
  }

  @override
  Future<User?> getCurrentUser() async {
    if (_cachedUser != null) return _cachedUser;
    final hasSession = await _tokenStorage.hasValidSession();
    if (!hasSession) return null;
    try {
      final user = await _remoteDataSource.getProfile();
      _cachedUser = user.toEntity();
      return _cachedUser;
    } catch (_) {
      return null;
    }
  }

  @override
  Future<bool> isAuthenticated() => _tokenStorage.hasValidSession();
}

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepositoryImpl(
    ref.watch(authRemoteDataSourceProvider),
    ref.watch(tokenStorageProvider),
    ref.watch(sharedPreferencesProvider),
  );
});
