import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../app/theme.dart';
import '../../providers/app_state_provider.dart';
import 'action_recommendation_screen.dart';

class AnalysisResultScreen extends ConsumerWidget {
  const AnalysisResultScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final appState = ref.watch(appStateProvider);
    final analysis = appState.currentAnalysis;
    final metadata = analysis.metadata ?? {};
    final explanation = metadata['explanation'] as Map<String, dynamic>? ?? {};

    final isLowConfidence = analysis.requiresConfirmation;

    return Scaffold(
      appBar: AppBar(
        title: const Text('AI ANALYSIS RESULT'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Confidence Tier Badge
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: isLowConfidence
                    ? AppTheme.warning.withValues(alpha: 0.15)
                    : AppTheme.primaryLight,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: isLowConfidence ? AppTheme.warning : AppTheme.primary,
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    isLowConfidence ? Icons.warning_amber : Icons.verified,
                    color: isLowConfidence ? AppTheme.warning : AppTheme.primary,
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          isLowConfidence
                              ? 'CONFIDENCE TIER: LOW (< 60%)'
                              : 'CONFIDENCE TIER: HIGH (≥ 85%)',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: isLowConfidence ? AppTheme.warning : AppTheme.primaryDark,
                          ),
                        ),
                        Text(
                          isLowConfidence
                              ? '⚠️ Farmer confirmation required before automated spray.'
                              : 'High diagnostic reliability. Ready for Decision Engine.',
                          style: const TextStyle(fontSize: 12),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // 1. Crop Block
            _ResultCard(
              title: 'CROP IDENTIFICATION',
              icon: Icons.grass,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _DataRow(label: 'Identified Crop', value: analysis.crop.name.toUpperCase()),
                  _DataRow(
                    label: 'Identification Confidence',
                    value: '${(analysis.crop.confidence * 100).toStringAsFixed(0)}%',
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),

            // 2. Disease Block
            _ResultCard(
              title: 'DISEASE DIAGNOSIS',
              icon: Icons.coronavirus,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _DataRow(
                    label: 'Diagnosed Disease',
                    value: analysis.disease?.name.replaceAll('_', ' ').toUpperCase() ?? 'NONE (HEALTHY)',
                  ),
                  if (analysis.disease != null) ...[
                    _DataRow(
                      label: 'Model Confidence',
                      value: '${(analysis.disease!.confidence * 100).toStringAsFixed(0)}%',
                    ),
                    _DataRow(
                      label: 'Foliage Severity Level',
                      value: analysis.severity?.level.toUpperCase() ?? 'HEALTHY',
                    ),
                    if (analysis.severity?.affectedAreaPercent != null)
                      _DataRow(
                        label: 'Leaf Affected Area',
                        value: '${analysis.severity!.affectedAreaPercent!.toStringAsFixed(1)}%',
                      ),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 12),

            // 3. Pest Block
            _ResultCard(
              title: 'PEST DETECTION',
              icon: Icons.bug_report,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _DataRow(
                    label: 'Detected Pests',
                    value: analysis.pests.isEmpty ? 'None Detected' : '${analysis.pests.length} pest instance(s)',
                  ),
                  if (analysis.pests.isNotEmpty)
                    _DataRow(
                      label: 'Dominant Species',
                      value: analysis.pests.first.pestType.toUpperCase(),
                    ),
                ],
              ),
            ),
            const SizedBox(height: 12),

            // 4. Nutrient Block
            _ResultCard(
              title: 'NUTRIENT DEFICIENCY',
              icon: Icons.opacity,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _DataRow(
                    label: 'Suspected Deficiency',
                    value: analysis.nutrientDeficiency?.toUpperCase() ?? 'None Observed',
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    'Note: Visual inspection indicates symptoms only. Soil/tissue testing is required for lab confirmation.',
                    style: TextStyle(fontSize: 11, color: AppTheme.secondaryText, fontStyle: FontStyle.italic),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),

            // 5. GenAI Explanation
            if (explanation.isNotEmpty) ...[
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppTheme.primaryDark,
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.auto_awesome, color: Colors.amber, size: 20),
                        SizedBox(width: 8),
                        Text(
                          'GENAI FARMER EXPLANATION',
                          style: TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                            letterSpacing: 1,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    Text(
                      explanation['summary']?.toString() ?? 'Explanation generated.',
                      style: const TextStyle(color: Colors.white, fontSize: 13, height: 1.4),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),
            ],

            // Proceed to Decision Engine Action Button
            ElevatedButton.icon(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const ActionRecommendationScreen(),
                  ),
                );
              },
              icon: const Icon(Icons.arrow_forward),
              label: const Text('VIEW DECISION ENGINE RECOMMENDATION'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ResultCard extends StatelessWidget {
  final String title;
  final IconData icon;
  final Widget child;

  const _ResultCard({required this.title, required this.icon, required this.child});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(14.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, size: 18, color: AppTheme.primary),
                const SizedBox(width: 6),
                Text(
                  title,
                  style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppTheme.primaryDark),
                ),
              ],
            ),
            const Divider(),
            child,
          ],
        ),
      ),
    );
  }
}

class _DataRow extends StatelessWidget {
  final String label;
  final String value;

  const _DataRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 13, color: AppTheme.secondaryText)),
          Text(value, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}
