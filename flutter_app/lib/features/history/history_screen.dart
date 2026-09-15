import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../app/theme.dart';
import '../../models/history_record.dart';
import '../../providers/app_state_provider.dart';

class HistoryScreen extends ConsumerWidget {
  const HistoryScreen({super.key});

  void _showRecordDetail(BuildContext context, HistoryRecord record) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Scan Details (${record.id})',
                    style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
              const Divider(),
              _HistoryDetailRow(label: 'Timestamp', value: DateFormat('MMM d, yyyy - HH:mm').format(record.timestamp)),
              _HistoryDetailRow(label: 'Target Crop', value: record.crop),
              _HistoryDetailRow(label: 'Condition Diagnosed', value: record.diseaseOrPest),
              _HistoryDetailRow(label: 'Confidence Rating', value: '${(record.confidence * 100).toStringAsFixed(0)}%'),
              _HistoryDetailRow(label: 'Severity Level', value: record.severity),
              _HistoryDetailRow(label: 'Decision Action Taken', value: record.actionTaken, isBold: true),
              _HistoryDetailRow(label: 'Soil Moisture Telemetry', value: '${record.soilMoisture}%'),
              _HistoryDetailRow(label: 'Air Temp Telemetry', value: '${record.airTemp}°C'),
              const SizedBox(height: 8),
              const Text('Audit Notes:', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
              Text(record.notes, style: const TextStyle(fontSize: 12, color: AppTheme.secondaryText)),
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final appState = ref.watch(appStateProvider);
    final history = appState.history;

    return Scaffold(
      appBar: AppBar(
        title: const Text('FIELD ANALYSIS HISTORY'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Historical Trends Header
            Card(
              elevation: 2,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.show_chart, color: AppTheme.primary, size: 20),
                        SizedBox(width: 8),
                        Text(
                          'FIELD HEALTH & RISK TRENDS (7 DAYS)',
                          style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppTheme.primaryDark),
                        ),
                      ],
                    ),
                    const Divider(),
                    const SizedBox(height: 6),
                    const Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        _TrendMetric(label: 'Health Index', value: '↗ 94%', color: AppTheme.success),
                        _TrendMetric(label: 'Disease Load', value: '↘ -18%', color: AppTheme.primary),
                        _TrendMetric(label: 'Soil Moisture', value: '→ 40%', color: AppTheme.info),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),

            const Text(
              'PAST FIELD DIAGNOSES',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.text),
            ),
            const SizedBox(height: 12),

            ...history.map((record) => _buildCard(context, record)),
          ],
        ),
      ),
    );
  }

  Widget _buildCard(BuildContext context, HistoryRecord record) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        onTap: () => _showRecordDetail(context, record),
        leading: CircleAvatar(
          backgroundColor: AppTheme.primaryLight,
          child: Icon(
            record.actionTaken == 'SPRAY'
                ? Icons.cleaning_services
                : (record.actionTaken == 'IRRIGATE' ? Icons.water_drop : Icons.eco),
            color: AppTheme.primaryDark,
            size: 20,
          ),
        ),
        title: Text(
          '${record.crop} — ${record.diseaseOrPest}',
          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
        ),
        subtitle: Text(
          '${DateFormat('MMM d, HH:mm').format(record.timestamp)} • ${record.severity}',
          style: const TextStyle(fontSize: 12, color: AppTheme.secondaryText),
        ),
        trailing: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: AppTheme.primaryLight,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                record.actionTaken,
                style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppTheme.primaryDark),
              ),
            ),
            const SizedBox(height: 2),
            const Icon(Icons.chevron_right, size: 16, color: AppTheme.secondaryText),
          ],
        ),
      ),
    );
  }
}

class _TrendMetric extends StatelessWidget {
  final String label;
  final String value;
  final Color color;

  const _TrendMetric({required this.label, required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(value, style: TextStyle(fontWeight: FontWeight.w900, fontSize: 16, color: color)),
        Text(label, style: const TextStyle(fontSize: 11, color: AppTheme.secondaryText)),
      ],
    );
  }
}

class _HistoryDetailRow extends StatelessWidget {
  final String label;
  final String value;
  final bool isBold;

  const _HistoryDetailRow({required this.label, required this.value, this.isBold = false});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
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
