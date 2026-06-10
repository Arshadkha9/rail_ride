import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/widgets/app_scaffold.dart';
import '../providers/railway_provider.dart';

class StationSearchScreen extends ConsumerStatefulWidget {
  const StationSearchScreen({super.key});

  @override
  ConsumerState<StationSearchScreen> createState() =>
      _StationSearchScreenState();
}

class _StationSearchScreenState extends ConsumerState<StationSearchScreen> {
  final _controller = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(stationSearchProvider.notifier).search('');
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final stations = ref.watch(stationSearchProvider);

    return AppScaffold(
      title: 'Station Search',
      body: Column(
        children: [
          TextField(
            controller: _controller,
            decoration: InputDecoration(
              labelText: 'Search station',
              prefixIcon: const Icon(Icons.search),
              suffixIcon: _controller.text.isNotEmpty
                  ? IconButton(
                      icon: const Icon(Icons.clear),
                      onPressed: () {
                        _controller.clear();
                        ref.read(stationSearchProvider.notifier).search('');
                        setState(() {});
                      },
                    )
                  : null,
            ),
            onChanged: (v) {
              ref.read(stationSearchProvider.notifier).search(v);
              setState(() {});
            },
          ),
          const SizedBox(height: 16),
          Expanded(
            child: ListView.builder(
              itemCount: stations.length,
              itemBuilder: (context, index) {
                final station = stations[index];
                return Card(
                  margin: const EdgeInsets.only(bottom: 8),
                  child: ListTile(
                    leading: CircleAvatar(
                      backgroundColor: AppColors.railway.withValues(alpha: 0.15),
                      child: Text(
                        station.code.substring(0, 2),
                        style: const TextStyle(
                          color: AppColors.railway,
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    ),
                    title: Text(station.name),
                    subtitle: Text('${station.code} • ${station.state}'),
                    trailing: IconButton(
                      icon: const Icon(Icons.copy_outlined, size: 20),
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text('Copied ${station.code}')),
                        );
                      },
                    ),
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
