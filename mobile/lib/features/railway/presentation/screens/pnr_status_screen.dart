import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/utils/validators.dart';
import '../../../../core/widgets/app_scaffold.dart';
import '../../domain/entities/train.dart';
import '../providers/railway_provider.dart';

class PnrStatusScreen extends ConsumerStatefulWidget {
  const PnrStatusScreen({super.key});

  @override
  ConsumerState<PnrStatusScreen> createState() => _PnrStatusScreenState();
}

class _PnrStatusScreenState extends ConsumerState<PnrStatusScreen> {
  final _controller = TextEditingController();
  final _formKey = GlobalKey<FormState>();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final pnrState = ref.watch(pnrProvider);

    return AppScaffold(
      title: 'PNR Status',
      body: Column(
        children: [
          Form(
            key: _formKey,
            child: Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _controller,
                    keyboardType: TextInputType.number,
                    maxLength: 10,
                    decoration: const InputDecoration(
                      labelText: 'PNR Number',
                      counterText: '',
                    ),
                    validator: Validators.pnr,
                  ),
                ),
                const SizedBox(width: 12),
                ElevatedButton(
                  onPressed: () {
                    if (_formKey.currentState!.validate()) {
                      ref.read(pnrProvider.notifier).checkPnr(_controller.text);
                    }
                  },
                  child: const Text('Check'),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Expanded(
            child: pnrState.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (e, _) => Center(child: Text('Error: $e')),
              data: (pnr) {
                if (pnr == null) {
                  return Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          Icons.confirmation_number_outlined,
                          size: 64,
                          color: AppColors.primary.withValues(alpha: 0.3),
                        ),
                        const SizedBox(height: 16),
                        const Text('Enter your 10-digit PNR number'),
                      ],
                    ),
                  );
                }
                return _PnrResultCard(pnr: pnr);
              },
            ),
          ),
        ],
      ),
    );
  }
}

class _PnrResultCard extends StatelessWidget {
  const _PnrResultCard({required this.pnr});

  final PnrStatus pnr;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'PNR: ${pnr.pnr}',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                      Chip(
                        label: Text(
                          pnr.chartPrepared ? 'Chart Prepared' : 'Chart Not Prepared',
                          style: const TextStyle(fontSize: 12),
                        ),
                        backgroundColor: pnr.chartPrepared
                            ? AppColors.success.withValues(alpha: 0.15)
                            : AppColors.warning.withValues(alpha: 0.15),
                      ),
                    ],
                  ),
                  const Divider(height: 24),
                  _InfoRow(label: 'Train', value: '${pnr.trainNumber} - ${pnr.trainName}'),
                  _InfoRow(label: 'From', value: pnr.from),
                  _InfoRow(label: 'To', value: pnr.to),
                  _InfoRow(label: 'Date', value: pnr.journeyDate),
                  _InfoRow(label: 'Status', value: pnr.currentStatus),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),
          Card(
            child: Column(
              children: [
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    children: const [
                      Expanded(
                        flex: 2,
                        child: Text('Passenger', style: TextStyle(fontWeight: FontWeight.bold)),
                      ),
                      Expanded(child: Text('Booking', style: TextStyle(fontWeight: FontWeight.bold))),
                      Expanded(child: Text('Current', style: TextStyle(fontWeight: FontWeight.bold))),
                    ],
                  ),
                ),
                const Divider(height: 1),
                ...pnr.passengers.map((p) => Padding(
                      padding: const EdgeInsets.all(16),
                      child: Row(
                        children: [
                          Expanded(flex: 2, child: Text(p.name)),
                          Expanded(child: Text(p.bookingStatus, style: const TextStyle(fontSize: 12))),
                          Expanded(
                            child: Text(
                              p.currentStatus,
                              style: TextStyle(
                                fontSize: 12,
                                color: p.currentStatus.contains('CNF')
                                    ? AppColors.success
                                    : AppColors.warning,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ],
                      ),
                    )),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  const _InfoRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 80,
            child: Text(
              label,
              style: TextStyle(
                color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.6),
              ),
            ),
          ),
          Expanded(child: Text(value, style: const TextStyle(fontWeight: FontWeight.w500))),
        ],
      ),
    );
  }
}
