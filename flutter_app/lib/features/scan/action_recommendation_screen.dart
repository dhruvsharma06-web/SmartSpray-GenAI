import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../app/theme.dart';
import '../../models/decision_result.dart';
import '../../providers/app_state_provider.dart';
import '../../widgets/recommendation_card.dart';

class ActionRecommendationScreen extends ConsumerWidget {
  const ActionRecommendationScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final appState = ref.watch(appStateProvider);
    final decision = appState.currentDecision;

    return Scaffold(
      appBar: AppBar(
        title: const Text('RECOMMENDED ACTION'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Big Decision Card
            RecommendationCard(decision: decision),
            const SizedBox(height: 20),

            // Rule Audit Trail
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.shield_outlined, color: AppTheme.primary, size: 18),
                        SizedBox(width: 8),
                        Text(
                          'DECISION AUDIT & RULE TRACEABILITY',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: AppTheme.primaryDark,
                          ),
                        ),
                      ],
                    ),
                    const Divider(),
                    const SizedBox(height: 4),
                    const Text('Triggered Rules:', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                    ...decision.audit.triggeredRules.map(
                      (r) => Padding(
                        padding: const EdgeInsets.only(left: 8, top: 2),
                        child: Text('• $r', style: const TextStyle(fontSize: 12, color: AppTheme.secondaryText)),
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Evaluation Timestamp: ${decision.audit.timestamp}',
                      style: const TextStyle(fontSize: 11, color: AppTheme.secondaryText),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Hardware Action Controls
            if (decision.action == ActionType.SPRAY) ...[
              ElevatedButton.icon(
                onPressed: decision.requiresConfirmation
                    ? null
                    : () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('CONFIRMED: Spray command sent to backend/ESP32.'),
                            backgroundColor: AppTheme.success,
                          ),
                        );
                      },
                icon: const Icon(Icons.cleaning_services),
                label: const Text('CONFIRM & EXECUTE SPRAY'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.moderate,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
              ),
            ] else if (decision.action == ActionType.IRRIGATE) ...[
              ElevatedButton.icon(
                onPressed: () {
                  notifier(ref).togglePump();
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('CONFIRMED: Drip irrigation command sent to pump relay.'),
                      backgroundColor: AppTheme.info,
                    ),
                  );
                },
                icon: const Icon(Icons.water_drop),
                label: const Text('START 30-MIN IRRIGATION CYCLE'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.info,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
              ),
            ] else if (decision.action == ActionType.WARN) ...[
              ElevatedButton.icon(
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Farmer inspection logged.'),
                    ),
                  );
                },
                icon: const Icon(Icons.person_search),
                label: const Text('LOG FARMER PHYSICAL INSPECTION'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.warning,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
              ),
            ] else ...[
              OutlinedButton.icon(
                onPressed: () => Navigator.pop(context),
                icon: const Icon(Icons.check),
                label: const Text('RETURN TO DASHBOARD'),
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  AppStateNotifier notifier(WidgetRef ref) => ref.read(appStateProvider.notifier);
}
