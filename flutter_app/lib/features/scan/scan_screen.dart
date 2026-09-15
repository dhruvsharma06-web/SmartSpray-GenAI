import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../app/theme.dart';
import '../../providers/app_state_provider.dart';
import '../../services/demo_service.dart';
import 'analysis_result_screen.dart';

class ScanScreen extends ConsumerStatefulWidget {
  const ScanScreen({super.key});

  @override
  ConsumerState<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends ConsumerState<ScanScreen> {
  bool _isAnalyzing = false;
  String _selectedImageName = 'sample_tomato_early_blight.jpg';

  void _runAnalysis() async {
    setState(() => _isAnalyzing = true);
    await Future.delayed(const Duration(milliseconds: 1200));
    if (!mounted) return;
    setState(() => _isAnalyzing = false);

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const AnalysisResultScreen(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final appState = ref.watch(appStateProvider);
    final notifier = ref.read(appStateProvider.notifier);

    return Scaffold(
      appBar: AppBar(
        title: const Text('SCAN PLANT FOLIAGE'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Image Preview Box
            Container(
              height: 240,
              decoration: BoxDecoration(
                color: Colors.grey.shade200,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppTheme.border, width: 2),
              ),
              child: Stack(
                alignment: Alignment.center,
                children: [
                  Icon(
                    Icons.eco,
                    size: 96,
                    color: AppTheme.primary.withValues(alpha: 0.3),
                  ),
                  Positioned(
                    bottom: 12,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: Colors.black.withValues(alpha: 0.7),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        'PREVIEW: $_selectedImageName',
                        style: const TextStyle(color: Colors.white, fontSize: 12),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Demo Scenario Direct Picker
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppTheme.primaryLight,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppTheme.primary.withValues(alpha: 0.3)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.camera_alt, color: AppTheme.primaryDark),
                      SizedBox(width: 8),
                      Text(
                        'SELECT SAMPLE DEMO FOLIAGE IMAGE:',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                          color: AppTheme.primaryDark,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                   ...DemoScenario.values.map((scenario) {
                    final data = DemoService.scenarios[scenario]!;
                    final isSelected = appState.selectedScenario == scenario;
                    return Container(
                      margin: const EdgeInsets.only(bottom: 6),
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(8),
                        color: isSelected ? AppTheme.primary.withValues(alpha: 0.08) : Colors.transparent,
                      ),
                      child: ListTile(
                        dense: true,
                        leading: Icon(
                          isSelected ? Icons.radio_button_checked : Icons.radio_button_unchecked,
                          color: isSelected ? AppTheme.primaryDark : AppTheme.secondaryText,
                          size: 20,
                        ),
                        title: Text(
                          data.title,
                          style: TextStyle(
                            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                            color: isSelected ? AppTheme.primaryDark : AppTheme.text,
                          ),
                        ),
                        subtitle: Text(
                          data.description,
                          style: const TextStyle(fontSize: 11),
                        ),
                        onTap: () {
                          notifier.selectScenario(scenario);
                          setState(() {
                            _selectedImageName = scenario.name;
                          });
                        },
                      ),
                    );
                  }),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Action Button
            if (_isAnalyzing)
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppTheme.surface,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppTheme.primary),
                ),
                child: const Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    SizedBox(
                      width: 24,
                      height: 24,
                      child: CircularProgressIndicator(strokeWidth: 3),
                    ),
                    SizedBox(width: 14),
                    Text(
                      'AI RUNNING 8-STAGE FIELD DIAGNOSIS...',
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                    ),
                  ],
                ),
              )
            else
              ElevatedButton.icon(
                onPressed: _runAnalysis,
                icon: const Icon(Icons.auto_awesome),
                label: const Text('ANALYZE PLANT WITH AI'),
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
