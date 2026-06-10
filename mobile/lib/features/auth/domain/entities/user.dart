import 'package:equatable/equatable.dart';

class User extends Equatable {
  const User({
    required this.id,
    required this.name,
    required this.email,
    required this.phone,
    this.avatarUrl,
  });

  final String id;
  final String name;
  final String email;
  final String phone;
  final String? avatarUrl;

  @override
  List<Object?> get props => [id, name, email, phone, avatarUrl];
}
