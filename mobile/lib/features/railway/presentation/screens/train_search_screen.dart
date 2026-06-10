import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/utils/extensions.dart';
import '../../../../core/widgets/app_scaffold.dart';
import '../../../../core/widgets/empty_state.dart';
import '../../domain/entities/train.dart';
import '../providers/railway_provider.dart';

class TrainSearchScreen extends ConsumerWidget {
  const TrainSearchScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final search = ref.watch(trainSearchProvider);
    final notifier = ref.read(trainSearchProvider.notifier);

    return AppScaffold(
      title: 'Train Search',
      body: Column(
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  TextField(
                    decoration: const InputDecoration(
                      labelText: 'From Station',
                      prefixIcon: Icon(Icons.trip_origin),
                    ),
                    controller: TextEditingController(text: search.from)
                      ..selection = TextSelection.collapsed(
                        offset: search.from.length,
                      ),
                    onChanged: notifier.setFrom,
                  ),
                  const SizedBox(height: 12),
                  Align(
                    alignment: Alignment.centerRight,
                    child: IconButton(
                      icon: const Icon(Icons.swap_vert_rounded),
                      onPressed: notifier.swapStations,
                    ),
                  ),
                  TextField(
                    decoration: const InputDecoration(
                      labelText: 'To Station',
                      prefixIcon: Icon(Icons.location_on_outlined),
                    ),
                    controller: TextEditingController(text: search.to)
                      ..selection = TextSelection.collapsed(
                        offset: search.to.length,
                      ),
                    onChanged: notifier.setTo,
                  ),
                  const SizedBox(height: 12),
                  InkWell(
                    onTap: () async {
                      final picked = await showDatePicker(
                        context: context,
                        initialDate: search.date ?? DateTime.now(),
                        firstDate: DateTime.now(),
                        lastDate: DateTime.now().add(const Duration(days: 120)),
                      );
                      if (picked != null) notifier.setDate(picked);
                    },
                    child: InputDecorator(
                      decoration: const InputDecoration(
                        labelText: 'Journey Date',
                        prefixIcon: Icon(Icons.calendar_today_outlined),
                      ),
                      child: Text(
                        search.date != null
                            ? DateFormat('dd MMM yyyy').format(search.date!)
                            : 'Select date',
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: search.isLoading ? null : notifier.search,
                      icon: search.isLoading
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.search),
                      label: const Text('Search Trains'),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Expanded(
            child: search.isLoading
                ? const Center(child: CircularProgressIndicator())
                : !search.searched
                    ? const EmptyState(
                        icon: Icons.train_rounded,
                        title: 'Search for trains',
                        message:
                            'Enter source, destination and date to find available trains',
                      )
                    : search.trains.isEmpty
                        ? const EmptyState(
                            icon: Icons.search_off_rounded,
                            title: 'No trains found',
                            message: 'Try different stations or date',
                          )
                        : ListView.builder(
                            itemCount: search.trains.length,
                            itemBuilder: (context, index) =>
                                _TrainCard(train: search.trains[index]),
                          ),
          ),
        ],
      ),
    );
  }
}

class _TrainCard extends StatelessWidget {
  const _TrainCard({required this.train});

  final Train train;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppColors.railway.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    train.number,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      color: AppColors.railway,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    train.name,
                    style: const TextStyle(fontWeight: FontWeight.w600),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        train.departure,
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                      Text(train.from, style: Theme.of(context).textTheme.bodySmall),
                    ],
                  ),
                ),
                Column(
                  children: [
                    Text(
                      train.duration,
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                    const Icon(Icons.arrow_forward, size: 16),
                  ],
                ),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(
                        train.arrival,
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                      Text(train.to, style: Theme.of(context).textTheme.bodySmall),
                    ],
                  ),
                ),
              ],
            ),
            const Divider(height: 24),
            ...train.classes.map((cls) => Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4),
                  child: Row(
                    children: [
                      SizedBox(
                        width: 40,
                        child: Text(
                          cls.code,
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ),
                      Expanded(child: Text(cls.name)),
                      Text(cls.fare.currency),
                      const SizedBox(width: 12),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 2,
                        ),
                        decoration: BoxDecoration(
                          color: cls.availability.contains('AVAILABLE')
                              ? AppColors.success.withValues(alpha: 0.15)
                              : AppColors.warning.withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          cls.availability,
                          style: TextStyle(
                            fontSize: 11,
                            color: cls.availability.contains('AVAILABLE')
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
    );
  }
}
