import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/router/app_router.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/utils/extensions.dart';
import '../../../../core/widgets/app_scaffold.dart';
import '../../domain/entities/ride.dart';
import '../providers/ride_provider.dart';

class RideFareScreen extends ConsumerStatefulWidget {
  const RideFareScreen({
    super.key,
    required this.rideType,
    required this.pickup,
    required this.drop,
  });

  final String rideType;
  final String pickup;
  final String drop;

  @override
  ConsumerState<RideFareScreen> createState() => _RideFareScreenState();
}

class _RideFareScreenState extends ConsumerState<RideFareScreen> {
  List<RideEstimate> _estimates = [];
  RideEstimate? _selected;
  bool _loading = true;

  Color get _rideColor => switch (widget.rideType) {
        'bike' => AppColors.bike,
        'auto' => AppColors.auto,
        'taxi' => AppColors.taxi,
        _ => AppColors.primary,
      };

  @override
  void initState() {
    super.initState();
    _loadEstimates();
  }

  Future<void> _loadEstimates() async {
    final estimates = await ref
        .read(rideBookingProvider.notifier)
        .getEstimates(widget.rideType);
    setState(() {
      _estimates = estimates;
      _selected = estimates.isNotEmpty ? estimates.first : null;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      title: 'Choose Fare',
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      children: [
                        _LocationRow(
                          icon: Icons.trip_origin,
                          color: AppColors.success,
                          label: widget.pickup,
                        ),
                        Padding(
                          padding: const EdgeInsets.only(left: 11),
                          child: Container(
                            width: 2,
                            height: 24,
                            color: Colors.grey.shade300,
                          ),
                        ),
                        _LocationRow(
                          icon: Icons.location_on,
                          color: AppColors.error,
                          label: widget.drop,
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  'Available options',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 12),
                Expanded(
                  child: ListView.builder(
                    itemCount: _estimates.length,
                    itemBuilder: (context, index) {
                      final estimate = _estimates[index];
                      final isSelected = _selected == estimate;
                      return Card(
                        margin: const EdgeInsets.only(bottom: 12),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(16),
                          side: BorderSide(
                            color: isSelected
                                ? _rideColor
                                : Colors.transparent,
                            width: 2,
                          ),
                        ),
                        child: InkWell(
                          onTap: () => setState(() => _selected = estimate),
                          borderRadius: BorderRadius.circular(16),
                          child: Padding(
                            padding: const EdgeInsets.all(16),
                            child: Row(
                              children: [
                                Icon(
                                  isSelected
                                      ? Icons.radio_button_checked
                                      : Icons.radio_button_off,
                                  color: isSelected ? _rideColor : null,
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        estimate.vehicleName,
                                        style: const TextStyle(
                                          fontWeight: FontWeight.w600,
                                        ),
                                      ),
                                      Text(
                                        '${estimate.eta} away • ${estimate.distance}',
                                        style: Theme.of(context)
                                            .textTheme
                                            .bodySmall,
                                      ),
                                    ],
                                  ),
                                ),
                                Text(
                                  estimate.fare.currency,
                                  style: Theme.of(context)
                                      .textTheme
                                      .titleLarge
                                      ?.copyWith(
                                        fontWeight: FontWeight.bold,
                                        color: _rideColor,
                                      ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      );
                    },
                  ),
                ),
                SizedBox(
                  width: double.infinity,
                  height: 52,
                  child: ElevatedButton(
                    onPressed: _selected == null
                        ? null
                        : () => context.push(
                              AppRoutes.rideConfirm,
                              extra: {
                                'rideType': widget.rideType,
                                'pickup': widget.pickup,
                                'drop': widget.drop,
                                'fare': _selected!.fare,
                                'vehicleName': _selected!.vehicleName,
                              },
                            ),
                    style: ElevatedButton.styleFrom(backgroundColor: _rideColor),
                    child: Text(
                      _selected != null
                          ? 'Book for ${_selected!.fare.currency}'
                          : 'Select a ride',
                    ),
                  ),
                ),
              ],
            ),
    );
  }
}

class _LocationRow extends StatelessWidget {
  const _LocationRow({
    required this.icon,
    required this.color,
    required this.label,
  });

  final IconData icon;
  final Color color;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, color: color, size: 24),
        const SizedBox(width: 12),
        Expanded(child: Text(label)),
      ],
    );
  }
}
