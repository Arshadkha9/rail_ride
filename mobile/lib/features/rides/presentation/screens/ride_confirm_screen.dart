import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/router/app_router.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/utils/extensions.dart';
import '../../../../core/widgets/app_scaffold.dart';
import '../providers/ride_provider.dart';

class RideConfirmScreen extends ConsumerStatefulWidget {
  const RideConfirmScreen({
    super.key,
    required this.rideType,
    required this.pickup,
    required this.drop,
    required this.fare,
    required this.vehicleName,
  });

  final String rideType;
  final String pickup;
  final String drop;
  final double fare;
  final String vehicleName;

  @override
  ConsumerState<RideConfirmScreen> createState() => _RideConfirmScreenState();
}

class _RideConfirmScreenState extends ConsumerState<RideConfirmScreen> {
  String _paymentMethod = 'wallet';
  bool _booking = false;

  Color get _rideColor => switch (widget.rideType) {
        'bike' => AppColors.bike,
        'auto' => AppColors.auto,
        'taxi' => AppColors.taxi,
        _ => AppColors.primary,
      };

  Future<void> _confirmBooking() async {
    setState(() => _booking = true);
    await Future<void>.delayed(const Duration(seconds: 2));
    final rideId = 'RR${DateTime.now().millisecondsSinceEpoch % 100000}';
    final activeRide = ref.read(ridesLocalDataSourceProvider).getMockActiveRide(
          rideId: rideId,
          rideType: widget.rideType,
          pickup: widget.pickup,
          drop: widget.drop,
        );
    ref.read(activeRideProvider.notifier).state = activeRide;
    setState(() => _booking = false);
    if (!mounted) return;
    context.go(
      AppRoutes.rideTracking,
      extra: {
        'rideId': rideId,
        'rideType': widget.rideType,
        'pickup': widget.pickup,
        'drop': widget.drop,
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      title: 'Confirm Ride',
      body: Column(
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  Text(
                    widget.vehicleName,
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    widget.fare.currency,
                    style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: _rideColor,
                        ),
                  ),
                  const Divider(height: 32),
                  _DetailRow(label: 'Pickup', value: widget.pickup),
                  const SizedBox(height: 8),
                  _DetailRow(label: 'Drop', value: widget.drop),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'Payment Method',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 12),
          _PaymentOption(
            icon: Icons.account_balance_wallet_rounded,
            title: 'RailRide Wallet',
            subtitle: 'Balance: ₹2,450',
            value: 'wallet',
            groupValue: _paymentMethod,
            onChanged: (v) => setState(() => _paymentMethod = v!),
          ),
          _PaymentOption(
            icon: Icons.credit_card_rounded,
            title: 'Credit / Debit Card',
            subtitle: '**** 4242',
            value: 'card',
            groupValue: _paymentMethod,
            onChanged: (v) => setState(() => _paymentMethod = v!),
          ),
          _PaymentOption(
            icon: Icons.payments_rounded,
            title: 'Cash',
            subtitle: 'Pay driver directly',
            value: 'cash',
            groupValue: _paymentMethod,
            onChanged: (v) => setState(() => _paymentMethod = v!),
          ),
          const Spacer(),
          SizedBox(
            width: double.infinity,
            height: 52,
            child: ElevatedButton(
              onPressed: _booking ? null : _confirmBooking,
              style: ElevatedButton.styleFrom(backgroundColor: _rideColor),
              child: _booking
                  ? const Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        ),
                        SizedBox(width: 12),
                        Text('Finding driver...'),
                      ],
                    )
                  : Text('Confirm & Book • ${widget.fare.currency}'),
            ),
          ),
        ],
      ),
    );
  }
}

class _DetailRow extends StatelessWidget {
  const _DetailRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 60,
          child: Text(
            label,
            style: TextStyle(
              color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.6),
            ),
          ),
        ),
        Expanded(child: Text(value)),
      ],
    );
  }
}

class _PaymentOption extends StatelessWidget {
  const _PaymentOption({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.value,
    required this.groupValue,
    required this.onChanged,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final String value;
  final String groupValue;
  final ValueChanged<String?> onChanged;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: RadioListTile<String>(
        value: value,
        groupValue: groupValue,
        onChanged: onChanged,
        secondary: Icon(icon),
        title: Text(title),
        subtitle: Text(subtitle),
      ),
    );
  }
}
