import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../app/theme.dart';
import '../../models/field_zone.dart';
import '../../providers/app_state_provider.dart';

class ZoneDetailsScreen extends ConsumerWidget {
  const ZoneDetailsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final appState = ref.watch(appStateProvider);
    final notifier = ref.read(appStateProvider.notifier);
    final filters = ['All', 'Disease', 'Pest', 'Nutrient', 'Irrigation', 'Critical'];

    final filteredZones = appState.zones.where((zone) {
      if (appState.activeFilter == 'All') return true;
      if (appState.activeFilter == 'Disease' && zone.issueType == ZoneIssueType.disease) return true;
      if (appState.activeFilter == 'Pest' && zone.issueType == ZoneIssueType.pest) return true;
      if (appState.activeFilter == 'Nutrient' && zone.issueType == ZoneIssueType.nutrient) return true;
      if (appState.activeFilter == 'Irrigation' && zone.issueType == ZoneIssueType.irrigation) return true;
      if (appState.activeFilter == 'Critical' && zone.issueType == ZoneIssueType.critical) return true;
      return false;
    }).toList();

    return Scaffold(
      appBar: AppBar(
        title: const Text('FIELD ZONES & AFFECTED AREAS'),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(48),
          child: Container(
            color: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: filters.map((f) {
                  final isSelected = appState.activeFilter == f;
                  return Padding(
                    padding: const EdgeInsets.only(right: 8.0),
                    child: ChoiceChip(
                      label: Text(f.toUpperCase()),
                      selected: isSelected,
                      onSelected: (selected) {
                        if (selected) notifier.setFilter(f);
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
      body: ListView.builder(
        padding: const EdgeInsets.all(16.0),
        itemCount: filteredZones.length,
        itemBuilder: (context, index) {
          final zone = filteredZones[index];
          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        zone.label,
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(
                          color: AppTheme.primaryLight,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          zone.crop,
                          style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppTheme.primaryDark),
                        ),
                      ),
                    ],
                  ),
                  const Divider(),
                  _InfoItem(label: 'Detected Condition', value: zone.detectedIssue),
                  _InfoItem(label: 'Confidence', value: '${(zone.confidence * 100).toStringAsFixed(0)}%'),
                  _InfoItem(label: 'Severity Level', value: zone.severity),
                  _InfoItem(label: 'Climate Risk', value: zone.climateRiskSummary),
                  _InfoItem(label: 'Recommended Action', value: zone.recommendedAction, isBold: true),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

class _InfoItem extends StatelessWidget {
  final String label;
  final String value;
  final bool isBold;

  const _InfoItem({required this.label, required this.value, this.isBold = false});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 13, color: AppTheme.secondaryText)),
          Text(
            value,
            style: TextStyle(
              fontSize: 13,
              fontWeight: isBold ? FontWeight.bold : FontWeight.w500,
              color: isBold ? AppTheme.primaryDark : AppTheme.text,
            ),
          ),
        ],
      ),
    );
  }
}
