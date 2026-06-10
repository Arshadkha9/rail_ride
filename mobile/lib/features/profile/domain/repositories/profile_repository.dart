import '../entities/profile_settings.dart';

abstract class ProfileRepository {
  ProfileSettings getSettings();
  Future<void> updateSettings(ProfileSettings settings);
}
