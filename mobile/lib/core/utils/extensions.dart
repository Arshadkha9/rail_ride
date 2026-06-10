import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

extension ContextExtensions on BuildContext {
  ThemeData get theme => Theme.of(this);
  ColorScheme get colorScheme => theme.colorScheme;
  TextTheme get textTheme => theme.textTheme;
  Size get screenSize => MediaQuery.sizeOf(this);
  bool get isDark => theme.brightness == Brightness.dark;
  EdgeInsets get padding => MediaQuery.paddingOf(this);
}

extension StringExtensions on String {
  String get capitalize =>
      isEmpty ? this : '${this[0].toUpperCase()}${substring(1)}';

  String get titleCase => split(' ').map((w) => w.capitalize).join(' ');
}

extension DateTimeExtensions on DateTime {
  String get formattedDate => DateFormat('dd MMM yyyy').format(this);
  String get formattedTime => DateFormat('hh:mm a').format(this);
  String get formattedDateTime => DateFormat('dd MMM yyyy, hh:mm a').format(this);
}

extension DoubleExtensions on double {
  String get currency => '₹${toStringAsFixed(0)}';
}
