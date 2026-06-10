import 'package:equatable/equatable.dart';
import 'package:flutter/material.dart';

class DashboardModule extends Equatable {
  const DashboardModule({
    required this.id,
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.color,
    required this.route,
    this.badge,
  });

  final String id;
  final String title;
  final String subtitle;
  final IconData icon;
  final Color color;
  final String route;
  final String? badge;

  @override
  List<Object?> get props => [id, title, subtitle, icon, color, route, badge];
}
