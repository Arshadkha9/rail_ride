import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/router/app_router.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/utils/extensions.dart';
import '../../../../core/utils/validators.dart';
import '../../../../core/widgets/app_scaffold.dart';
import '../../../../core/widgets/loading_overlay.dart';

class RideBookingScreen extends ConsumerStatefulWidget {
  const RideBookingScreen({super.key, required this.rideType});

  final String rideType;

  @override
  ConsumerState<RideBookingScreen> createState() => _RideBookingScreenState();
}

class _RideBookingScreenState extends ConsumerState<RideBookingScreen> {
  final _pickupController = TextEditingController();
  final _dropController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  bool _loading = false;

  Color get _rideColor => switch (widget.rideType) {
        'bike' => AppColors.bike,
        'auto' => AppColors.auto,
        'taxi' => AppColors.taxi,
        _ => AppColors.primary,
      };

  IconData get _rideIcon => switch (widget.rideType) {
        'bike' => Icons.two_wheeler_rounded,
        'auto' => Icons.electric_rickshaw_rounded,
        'taxi' => Icons.local_taxi_rounded,
        _ => Icons.directions_car_rounded,
      };

  String get _rideTitle => widget.rideType.capitalize;

  @override
  void dispose() {
    _pickupController.dispose();
    _dropController.dispose();
    super.dispose();
  }

  Future<void> _proceed() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _loading = true);
    await Future<void>.delayed(const Duration(milliseconds: 500));
    setState(() => _loading = false);
    if (!mounted) return;
    context.push(
      AppRoutes.rideFare,
      extra: {
        'rideType': widget.rideType,
        'pickup': _pickupController.text.trim(),
        'drop': _dropController.text.trim(),
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      title: 'Book $_rideTitle',
      body: Stack(
        children: [
          Form(
            key: _formKey,
            child: Column(
              children: [
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        _rideColor.withValues(alpha: 0.2),
                        _rideColor.withValues(alpha: 0.05),
                      ],
                    ),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: _rideColor.withValues(alpha: 0.3)),
                  ),
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(
                          color: _rideColor.withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(14),
                        ),
                        child: Icon(_rideIcon, color: _rideColor, size: 32),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              '$_rideTitle Ride',
                              style: Theme.of(context)
                                  .textTheme
                                  .titleLarge
                                  ?.copyWith(fontWeight: FontWeight.bold),
                            ),
                            Text(
                              'Fast, affordable & reliable',
                              style: Theme.of(context).textTheme.bodySmall,
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                TextFormField(
                  controller: _pickupController,
                  decoration: const InputDecoration(
                    labelText: 'Pickup Location',
                    prefixIcon: Icon(Icons.trip_origin, color: AppColors.success),
                  ),
                  validator: (v) => Validators.required(v, field: 'Pickup location'),
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _dropController,
                  decoration: const InputDecoration(
                    labelText: 'Drop Location',
                    prefixIcon: Icon(Icons.location_on, color: AppColors.error),
                  ),
                  validator: (v) => Validators.required(v, field: 'Drop location'),
                ),
                const SizedBox(height: 16),
                Card(
                  child: ListTile(
                    leading: const Icon(Icons.my_location_rounded),
                    title: const Text('Use current location'),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: () {
                      _pickupController.text = 'Connaught Place, New Delhi';
                    },
                  ),
                ),
                const SizedBox(height: 8),
                Card(
                  child: ListTile(
                    leading: const Icon(Icons.history_rounded),
                    title: const Text('Recent: India Gate'),
                    onTap: () => _dropController.text = 'India Gate, New Delhi',
                  ),
                ),
                const Spacer(),
                SizedBox(
                  width: double.infinity,
                  height: 52,
                  child: ElevatedButton(
                    onPressed: _loading ? null : _proceed,
                    style: ElevatedButton.styleFrom(backgroundColor: _rideColor),
                    child: _loading
                        ? const CircularProgressIndicator(color: Colors.white)
                        : const Text('See Fares'),
                  ),
                ),
              ],
            ),
          ),
          if (_loading) const LoadingOverlay(),
        ],
      ),
    );
  }
}
