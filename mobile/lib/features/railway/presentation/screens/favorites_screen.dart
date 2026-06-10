import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/router/app_router.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/widgets/app_scaffold.dart';
import '../../../../core/widgets/empty_state.dart';
import '../providers/railway_provider.dart';

class FavoritesScreen extends ConsumerWidget {
  const FavoritesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final favorites =
        ref.read(railwayLocalDataSourceProvider).getMockFavorites();

    return AppScaffold(
      title: 'Favorite Routes',
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => context.push(AppRoutes.trainSearch),
        icon: const Icon(Icons.add),
        label: const Text('Add Route'),
      ),
      body: favorites.isEmpty
          ? const EmptyState(
              icon: Icons.favorite_border_rounded,
              title: 'No favorites yet',
              message: 'Save your frequently used routes for quick access',
            )
          : ListView.builder(
              itemCount: favorites.length,
              itemBuilder: (context, index) {
                final fav = favorites[index];
                return Card(
                  margin: const EdgeInsets.only(bottom: 12),
                  child: ListTile(
                    leading: Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: AppColors.notifications.withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Icon(
                        Icons.favorite_rounded,
                        color: AppColors.notifications,
                      ),
                    ),
                    title: Text(fav['label']!),
                    subtitle: Text('${fav['from']} → ${fav['to']}'),
                    trailing: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        IconButton(
                          icon: const Icon(Icons.search_rounded),
                          onPressed: () {
                            ref.read(trainSearchProvider.notifier)
                              ..setFrom(fav['from']!)
                              ..setTo(fav['to']!);
                            context.push(AppRoutes.trainSearch);
                          },
                        ),
                        IconButton(
                          icon: Icon(
                            Icons.delete_outline,
                            color: AppColors.error.withValues(alpha: 0.7),
                          ),
                          onPressed: () {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(content: Text('Route removed')),
                            );
                          },
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
    );
  }
}
