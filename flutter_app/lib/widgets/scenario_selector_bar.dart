import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../app/theme.dart';
import '../providers/app_state_provider.dart';
import '../services/demo_service.dart';

class ScenarioSelectorBar extends ConsumerWidget {
  const ScenarioSelectorBar({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final appState = ref.watch(appStateProvider);
    final notifier = ref.read(appStateProvider.notifier);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: AppTheme.primaryLight,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppTheme.primary.withValues(alpha: 0.3)),
      ),
      child: Row(
        children: [
          const Icon(Icons.tune, color: AppTheme.primaryDark, size: 20),
          const SizedBox(width: 8),
          const Text(
            'DEMO SCENARIO:',
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.bold,
              color: AppTheme.primaryDark,
              letterSpacing: 0.5,
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: DropdownButtonHideUnderline(
              child: DropdownButton<DemoScenario>(
                value: appState.selectedScenario,
                isExpanded: true,
                style: const TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.bold,
                  color: AppTheme.primaryDark,
                ),
                onChanged: (scenario) {
                  if (scenario != null) {
                    notifier.selectScenario(scenario);
                  }
                },
                items: DemoScenario.values.map((scenario) {
                  final data = DemoService.scenarios[scenario]!;
                  return DropdownMenuItem<DemoScenario>(
                    value: scenario,
                    child: Text(
                      data.title,
                      overflow: TextOverflow.ellipsis,
                    ),
                  );
                }).toList(),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
