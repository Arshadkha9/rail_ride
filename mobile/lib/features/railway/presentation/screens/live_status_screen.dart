import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/widgets/app_scaffold.dart';
import '../../data/datasources/railway_local_datasource.dart';
import '../providers/railway_provider.dart';

class LiveStatusScreen extends ConsumerStatefulWidget {
  const LiveStatusScreen({super.key});

  @override
  ConsumerState<LiveStatusScreen> createState() => _LiveStatusScreenState();
}

class _LiveStatusScreenState extends ConsumerState<LiveStatusScreen> {
  final _controller = TextEditingController(text: '12951');
  List<Map<String, dynamic>> _status = [];
  bool _loading = false;

  Future<void> _fetch() async {
    setState(() => _loading = true);
    await Future<void>.delayed(const Duration(milliseconds: 600));
    final data = ref.read(railwayLocalDataSourceProvider);
    setState(() {
      _status = data.getMockLiveStatus(_controller.text);
      _loading = false;
    });
  }

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _fetch());
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      title: 'Live Train Status',
      body: Column(
        children: [
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _controller,
                  decoration: const InputDecoration(
                    labelText: 'Train Number',
                    prefixIcon: Icon(Icons.train_rounded),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              ElevatedButton(
                onPressed: _loading ? null : _fetch,
                child: _loading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('Track'),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Expanded(
            child: _loading
                ? const Center(child: CircularProgressIndicator())
                : ListView.builder(
                    itemCount: _status.length,
                    itemBuilder: (context, index) {
                      final item = _status[index];
                      final passed = item['passed'] as bool;
                      final isLast = index == _status.length - 1;

                      return IntrinsicHeight(
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            SizedBox(
                              width: 32,
                              child: Column(
                                children: [
                                  Container(
                                    width: 16,
                                    height: 16,
                                    decoration: BoxDecoration(
                                      shape: BoxShape.circle,
                                      color: passed
                                          ? AppColors.success
                                          : index == _status.indexWhere((s) => !(s['passed'] as bool))
                                              ? AppColors.primary
                                              : Colors.grey.shade400,
                                      border: Border.all(
                                        color: Colors.white,
                                        width: 2,
                                      ),
                                    ),
                                  ),
                                  if (!isLast)
                                    Expanded(
                                      child: Container(
                                        width: 2,
                                        color: passed
                                            ? AppColors.success
                                            : Colors.grey.shade300,
                                      ),
                                    ),
                                ],
                              ),
                            ),
                            Expanded(
                              child: Card(
                                margin: const EdgeInsets.only(bottom: 8),
                                child: Padding(
                                  padding: const EdgeInsets.all(12),
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        item['station'] as String,
                                        style: const TextStyle(
                                          fontWeight: FontWeight.w600,
                                        ),
                                      ),
                                      const SizedBox(height: 8),
                                      Row(
                                        children: [
                                          _TimeChip(
                                            label: 'Scheduled',
                                            time: item['scheduled'] as String,
                                          ),
                                          const SizedBox(width: 8),
                                          _TimeChip(
                                            label: 'Actual',
                                            time: item['actual'] as String,
                                            highlight: passed,
                                          ),
                                          const Spacer(),
                                          if (item['delay'] != '--')
                                            Text(
                                              item['delay'] as String,
                                              style: TextStyle(
                                                color: AppColors.warning,
                                                fontWeight: FontWeight.w600,
                                                fontSize: 12,
                                              ),
                                            ),
                                        ],
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}

class _TimeChip extends StatelessWidget {
  const _TimeChip({
    required this.label,
    required this.time,
    this.highlight = false,
  });

  final String label;
  final String time;
  final bool highlight;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(fontSize: 10),
        ),
        Text(
          time,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: highlight ? AppColors.success : null,
          ),
        ),
      ],
    );
  }
}
