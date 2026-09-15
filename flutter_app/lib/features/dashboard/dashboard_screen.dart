import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/theme.dart';
import '../../models/field_zone.dart';
import '../../providers/app_state_provider.dart';
import '../../widgets/interactive_field_map.dart';
import '../../widgets/recommendation_card.dart';
import '../../widgets/risk_summary_card.dart';
import '../../widgets/scenario_selector_bar.dart';
import '../../widgets/stat_card.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  void _showZoneDetailBottomSheet(BuildContext context, FieldZone zone) {
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
                    zone.label,
                    style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
              const Divider(),
              const SizedBox(height: 8),
              _DetailRow(label: 'Zone ID', value: zone.id),
              _DetailRow(label: 'Crop', value: zone.crop),
              _DetailRow(label: 'Detected Condition', value: zone.detectedIssue),
              _DetailRow(label: 'Confidence', value: '${(zone.confidence * 100).toStringAsFixed(0)}%'),
              _DetailRow(label: 'Severity', value: zone.severity),
              _DetailRow(label: 'Climate Risk', value: zone.climateRiskSummary),
              _DetailRow(label: 'Recommended Action', value: zone.recommendedAction, isBold: true),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: () {
                  Navigator.pop(context);
                  context.go('/scan');
                },
                icon: const Icon(Icons.document_scanner),
                label: const Text('SCAN THIS ZONE'),
              ),
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final appState = ref.watch(appStateProvider);
    final analysis = appState.currentAnalysis;
    final decision = appState.currentDecision;

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: const BoxDecoration(
                color: Colors.white,
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.eco, color: AppTheme.primary, size: 20),
            ),
            const SizedBox(width: 8),
            const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'SMART SPRAY AI',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                Text(
                  'Green Acres Plot #4 — Ramesh Patel',
                  style: TextStyle(fontSize: 11, color: Colors.white70),
                ),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Notifications: High risk alerts enabled.')),
              );
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Scenario Selector
            const ScenarioSelectorBar(),
            const SizedBox(height: 16),

            // A. Field Health Summary Header
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [AppTheme.primaryDark, AppTheme.primary],
                ),
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: AppTheme.primaryDark.withValues(alpha: 0.3),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  )
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'FIELD HEALTH INDEX',
                        style: TextStyle(
                          color: Colors.white70,
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 1,
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: const Text(
                          'DEMO DATA',
                          style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Text(
                        analysis.disease?.name == 'healthy' ? '94%' : '68%',
                        style: const TextStyle(
                          fontSize: 36,
                          fontWeight: FontWeight.w900,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              analysis.disease?.name == 'healthy'
                                  ? 'Field Condition Optimal'
                                  : 'Active Symptoms Detected',
                              style: const TextStyle(
                                fontSize: 14,
                                fontWeight: FontWeight.bold,
                                color: Colors.white,
                              ),
                            ),
                            Text(
                              'Last Analysis: ${DateTime.now().hour}:${DateTime.now().minute.toString().padLeft(2, '0')}',
                              style: const TextStyle(fontSize: 12, color: Colors.white70),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // B. Interactive Field Map
            InteractiveFieldMap(
              zones: appState.zones,
              selectedZone: appState.selectedZone,
              activeFilter: appState.activeFilter,
              onZoneSelected: (zone) => _showZoneDetailBottomSheet(context, zone),
            ),
            const SizedBox(height: 20),

            // E. Current Recommendation Card (Decision Engine)
            RecommendationCard(decision: decision),
            const SizedBox(height: 20),

            // C. Field Statistics
            const Text(
              'FIELD STATISTICS',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.text),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                const Expanded(child: StatCard(label: 'Total Plants', value: '120')),
                const SizedBox(width: 12),
                Expanded(
                  child: StatCard(
                    label: 'Healthy',
                    value: analysis.disease?.name == 'healthy' ? '112' : '78',
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: StatCard(
                    label: 'Affected',
                    value: analysis.disease?.name == 'healthy' ? '8' : '42',
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),

            // D. Risk Summary
            RiskSummaryCard(climateRisk: analysis.climateRisk),
            const SizedBox(height: 24),

            // F. Quick Actions
            const Text(
              'QUICK ACTIONS',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.text),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => context.go('/scan'),
                    icon: const Icon(Icons.document_scanner),
                    label: const Text('SCAN PLANT'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => context.go('/zones'),
                    icon: const Icon(Icons.grid_view),
                    label: const Text('VIEW ZONES'),
                    style: OutlinedButton.styleFrom(
                      minimumSize: const Size(double.infinity, 48),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _DetailRow extends StatelessWidget {
  final String label;
  final String value;
  final bool isBold;

  const _DetailRow({required this.label, required this.value, this.isBold = false});

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
              fontWeight: isBold ? FontWeight.bold : FontWeight.w600,
              color: isBold ? AppTheme.primaryDark : AppTheme.text,
            ),
          ),
        ],
      ),
    );
  }
}
