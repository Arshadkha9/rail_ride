import '../entities/user.dart';

abstract class AuthRepository {
  Future<User> login({required String email, required String password});
  Future<void> signup({
    required String name,
    required String email,
    required String phone,
    required String password,
  });
  Future<User> verifyOtp({required String phone, required String otp});
  Future<void> resendOtp({required String phone});
  Future<void> logout();
  Future<User?> getCurrentUser();
  Future<bool> isAuthenticated();
}
