import 'package:equatable/equatable.dart';

class ProfileSettings extends Equatable {
  const ProfileSettings({
    this.notificationsEnabled = true,
    this.language = 'en',
    this.kycVerified = true,
  });

  final bool notificationsEnabled;
  final String language;
  final bool kycVerified;

  @override
  List<Object?> get props => [notificationsEnabled, language, kycVerified];
}
