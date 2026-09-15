import 'package:flutter/material.dart';
import '../app/theme.dart';
import '../models/decision_result.dart';

class RecommendationCard extends StatelessWidget {
  final DecisionResult decision;

  const RecommendationCard({super.key, required this.decision});

  Color _getActionColor(ActionType action) {
    switch (action) {
      case ActionType.SPRAY:
        return AppTheme.moderate;
      case ActionType.IRRIGATE:
        return AppTheme.info;
      case ActionType.WARN:
        return AppTheme.warning;
      case ActionType.DELAY:
        return Colors.orange;
      case ActionType.NO_ACTION:
        return AppTheme.success;
    }
  }

  IconData _getActionIcon(ActionType action) {
    switch (action) {
      case ActionType.SPRAY:
        return Icons.cleaning_services;
      case ActionType.IRRIGATE:
        return Icons.water_drop;
      case ActionType.WARN:
        return Icons.warning_amber_rounded;
      case ActionType.DELAY:
        return Icons.access_time_filled;
      case ActionType.NO_ACTION:
        return Icons.check_circle_outline;
    }
  }

  @override
  Widget build(BuildContext context) {
    final actionColor = _getActionColor(decision.action);

    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: actionColor.withValues(alpha: 0.5), width: 2),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: actionColor.withValues(alpha: 0.15),
                        shape: BoxShape.circle,
                      ),
                      child: Icon(_getActionIcon(decision.action), color: actionColor, size: 24),
                    ),
                    const SizedBox(width: 12),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'DECISION ENGINE RESULT',
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            color: AppTheme.secondaryText,
                            letterSpacing: 0.8,
                          ),
                        ),
                        Text(
                          decision.action.name,
                          style: TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.w900,
                            color: actionColor,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: actionColor.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    'PRIORITY: ${decision.priority.name}',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                      color: actionColor,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            const Divider(),
            const SizedBox(height: 8),
            Text(
              decision.reason,
              style: const TextStyle(fontSize: 14, height: 1.4, color: AppTheme.text),
            ),
            if (decision.durationMinutes != null) ...[
              const SizedBox(height: 8),
              Row(
                children: [
                  const Icon(Icons.timer, size: 16, color: AppTheme.info),
                  const SizedBox(width: 6),
                  Text(
                    'Recommended Duration: ${decision.durationMinutes!.toStringAsFixed(0)} minutes',
                    style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppTheme.info),
                  ),
                ],
              ),
            ],
            if (decision.requiresConfirmation) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: AppTheme.warning.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: AppTheme.warning),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.warning_amber, color: AppTheme.warning, size: 18),
                    SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        '⚠️ Farmer Confirmation Required before taking action.',
                        style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppTheme.text),
                      ),
                    ),
                  ],
                ),
              ),
            ],
            if (decision.verifiedTreatment != null) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppTheme.primaryLight,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: AppTheme.primary.withValues(alpha: 0.3)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.verified, color: AppTheme.primary, size: 16),
                        SizedBox(width: 6),
                        Text(
                          'VERIFIED RAG TREATMENT RECORD',
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            color: AppTheme.primaryDark,
                            letterSpacing: 0.5,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Text(
                      'Product: ${decision.verifiedTreatment!['product'] ?? 'Verified Treatment'}',
                      style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppTheme.primaryDark),
                    ),
                    if (decision.verifiedTreatment!['active_ingredient'] != null)
                      Text(
                        'Active Ingredient: ${decision.verifiedTreatment!['active_ingredient']}',
                        style: const TextStyle(fontSize: 12, color: AppTheme.secondaryText),
                      ),
                    if (decision.verifiedTreatment!['label_rate'] != null)
                      Text(
                        'Label Rate: ${decision.verifiedTreatment!['label_rate']}',
                        style: const TextStyle(fontSize: 12, color: AppTheme.secondaryText),
                      ),
                    if (decision.verifiedTreatment!['pre_harvest_interval_days'] != null)
                      Text(
                        'Pre-Harvest Interval (PHI): ${decision.verifiedTreatment!['pre_harvest_interval_days']} days',
                        style: const TextStyle(fontSize: 12, color: AppTheme.secondaryText),
                      ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
