import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../domain/entities/profile_settings.dart';
import '../../domain/repositories/profile_repository.dart';

class ProfileRepositoryImpl implements ProfileRepository {
  ProfileSettings _settings = const ProfileSettings();

  @override
  ProfileSettings getSettings() => _settings;

  @override
  Future<void> updateSettings(ProfileSettings settings) async {
    await Future<void>.delayed(const Duration(milliseconds: 300));
    _settings = settings;
  }
}

final profileRepositoryProvider = Provider<ProfileRepository>((ref) {
  return ProfileRepositoryImpl();
});
