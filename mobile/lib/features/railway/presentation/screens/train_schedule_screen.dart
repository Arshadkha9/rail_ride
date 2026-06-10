import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/widgets/app_scaffold.dart';
import '../providers/railway_provider.dart';

class TrainScheduleScreen extends ConsumerStatefulWidget {
  const TrainScheduleScreen({super.key});

  @override
  ConsumerState<TrainScheduleScreen> createState() =>
      _TrainScheduleScreenState();
}

class _TrainScheduleScreenState extends ConsumerState<TrainScheduleScreen> {
  final _controller = TextEditingController(text: '12951');
  List<Map<String, dynamic>> _schedule = [];
  bool _loading = false;

  Future<void> _fetch() async {
    setState(() => _loading = true);
    await Future<void>.delayed(const Duration(milliseconds: 600));
    final data = ref.read(railwayLocalDataSourceProvider);
    setState(() {
      _schedule = data.getMockSchedule(_controller.text);
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
      title: 'Train Schedule',
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
                child: const Text('Get Schedule'),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Expanded(
            child: _loading
                ? const Center(child: CircularProgressIndicator())
                : ListView.builder(
                    itemCount: _schedule.length,
                    itemBuilder: (context, index) {
                      final stop = _schedule[index];
                      return Card(
                        margin: const EdgeInsets.only(bottom: 8),
                        child: ListTile(
                          leading: CircleAvatar(
                            backgroundColor:
                                AppColors.railway.withValues(alpha: 0.15),
                            child: Text(
                              '${stop['day']}',
                              style: const TextStyle(
                                color: AppColors.railway,
                                fontWeight: FontWeight.bold,
                                fontSize: 12,
                              ),
                            ),
                          ),
                          title: Text(
                            stop['station'] as String,
                            style: const TextStyle(fontWeight: FontWeight.w600),
                          ),
                          subtitle: Text(
                            'Arr: ${stop['arrival']}  •  Dep: ${stop['departure']}',
                          ),
                          trailing: index == 0
                              ? const Chip(label: Text('Start'))
                              : index == _schedule.length - 1
                                  ? const Chip(label: Text('End'))
                                  : null,
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
