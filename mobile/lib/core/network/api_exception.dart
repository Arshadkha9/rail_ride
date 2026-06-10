import 'package:dio/dio.dart';
import 'package:equatable/equatable.dart';

class ApiException extends Equatable implements Exception {
  const ApiException({
    required this.message,
    this.statusCode,
    this.originalError,
  });

  final String message;
  final int? statusCode;
  final dynamic originalError;

  factory ApiException.fromDio(DioException error) {
    String message = 'Something went wrong. Please try again.';

    if (error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.receiveTimeout ||
        error.type == DioExceptionType.sendTimeout) {
      message = 'Connection timed out. Check your internet connection.';
    } else if (error.type == DioExceptionType.connectionError) {
      message = 'No internet connection. Please try again.';
    } else if (error.response?.data is Map) {
      final data = error.response!.data as Map;
      message = data['message']?.toString() ??
          data['error']?.toString() ??
          message;
    }

    return ApiException(
      message: message,
      statusCode: error.response?.statusCode,
      originalError: error,
    );
  }

  @override
  List<Object?> get props => [message, statusCode];
}
