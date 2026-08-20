import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'history_provider.dart';
import '../../app/theme.dart';

class HistoryScreen extends ConsumerWidget {
  const HistoryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(historyStateProvider);
    final notifier = ref.read(historyStateProvider.notifier);
    final events = state.filteredEvents;

    return Scaffold(
      appBar: AppBar(
        title: const Text('HISTORY'),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(48),
          child: Container(
            color: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: HistoryFilter.values.map((filter) {
                  final isSelected = state.filter == filter;
                  return Padding(
                    padding: const EdgeInsets.only(right: 8.0),
                    child: ChoiceChip(
                      label: Text(filter.name.toUpperCase()),
                      selected: isSelected,
                      onSelected: (selected) {
                        if (selected) notifier.setFilter(filter);
                      },
                      selectedColor: AppTheme.primaryLight,
                      labelStyle: TextStyle(
                        color: isSelected ? AppTheme.primaryDark : AppTheme.secondaryText,
                        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                      ),
                    ),
                  );
                }).toList(),
              ),
            ),
          ),
        ),
      ),
      body: events.isEmpty
          ? const Center(child: Text('No events found.'))
          : ListView.builder(
              padding: const EdgeInsets.all(16.0),
              itemCount: events.length,
              itemBuilder: (context, index) {
                final event = events[index];
                return _buildEventCard(context, event);
              },
            ),
    );
  }

  Widget _buildEventCard(BuildContext context, HistoryEvent event) {
    Color statusColor = AppTheme.secondaryText;
    if (event.status.toLowerCase() == 'completed') statusColor = AppTheme.success;
    if (event.status.toLowerCase() == 'failed' || event.status.toLowerCase() == 'stopped') statusColor = AppTheme.error;
    if (event.status.toLowerCase() == 'skipped') statusColor = AppTheme.info;

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  DateFormat('HH:mm - MMM d').format(event.timestamp),
                  style: Theme.of(context).textTheme.labelSmall?.copyWith(fontWeight: FontWeight.bold),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: statusColor.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    event.status.toUpperCase(),
                    style: TextStyle(color: statusColor, fontSize: 10, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
            const Divider(),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(event.plant, style: const TextStyle(fontWeight: FontWeight.bold)),
                Text('${event.disease} (${event.confidence}%)'),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Severity: ${event.severity}%', style: TextStyle(color: event.severity > 50 ? AppTheme.moderate : AppTheme.text)),
                Text(event.sprayLevel, style: const TextStyle(fontWeight: FontWeight.w600)),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Mode: ${event.mode}', style: Theme.of(context).textTheme.labelSmall),
                Text('Duration: ${event.duration}', style: Theme.of(context).textTheme.labelSmall),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
