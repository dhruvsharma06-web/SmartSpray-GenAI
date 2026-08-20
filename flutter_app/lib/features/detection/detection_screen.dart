import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'detection_provider.dart';
import '../../widgets/detection_visualizer.dart';
import '../../app/theme.dart';

class DetectionScreen extends ConsumerWidget {
  const DetectionScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(detectionStateProvider);
    final notifier = ref.read(detectionStateProvider.notifier);

    return Scaffold(
      appBar: AppBar(
        title: const Text('DETECT (ASSISTED)'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => notifier.reset(),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            DetectionVisualizer(state: state),
            const SizedBox(height: 24),
            _buildStatusPanel(state),
            const SizedBox(height: 24),
            _buildControls(context, state, notifier),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusPanel(DetectionState state) {
    if (state == DetectionState.idle) {
      return const Center(child: Text('Press START SCAN to begin.'));
    }

    if (state == DetectionState.scanning) {
      return const Center(
        child: Column(
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Looking for a plant...'),
          ],
        ),
      );
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (state.index >= DetectionState.plantDetected.index)
              const _StatusRow(icon: Icons.eco, text: 'Plant detected', color: Colors.green),
            if (state.index >= DetectionState.leafDetected.index)
              const _StatusRow(icon: Icons.spa, text: 'Leaf detected', color: Colors.blue),
            if (state.index >= DetectionState.diseaseDetected.index) ...[
              const Divider(),
              const Text('Disease: Early Blight', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
              const Text('Confidence: 94%'),
            ],
            if (state.index >= DetectionState.targetReady.index) ...[
              const Divider(),
              const Text('Severity: 62%', style: TextStyle(color: AppTheme.moderate, fontWeight: FontWeight.bold)),
              const Text('Recommended: MODERATE SPRAY'),
            ],
            if (state == DetectionState.waitingForConfirmation) ...[
              const Divider(),
              const Text(
                'Aim nozzle at highlighted target.',
                style: TextStyle(color: AppTheme.emergency, fontWeight: FontWeight.bold),
              ),
            ],
            if (state == DetectionState.spraying) ...[
              const Divider(),
              const Center(
                child: Column(
                  children: [
                    CircularProgressIndicator(),
                    SizedBox(height: 8),
                    Text('Spraying...'),
                  ],
                ),
              ),
            ],
            if (state == DetectionState.sprayCompleted) ...[
              const Divider(),
              const Center(
                child: Text('Spray complete', style: TextStyle(color: AppTheme.success, fontWeight: FontWeight.bold, fontSize: 18)),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildControls(BuildContext context, DetectionState state, DetectionStateNotifier notifier) {
    if (state == DetectionState.idle || state == DetectionState.sprayCompleted) {
      return ElevatedButton.icon(
        onPressed: () => notifier.startScan(),
        icon: const Icon(Icons.document_scanner),
        label: const Text('START SCAN'),
      );
    }

    if (state == DetectionState.waitingForConfirmation) {
      return Row(
        children: [
          Expanded(
            child: OutlinedButton(
              onPressed: () => notifier.skip(),
              style: OutlinedButton.styleFrom(
                minimumSize: const Size(double.infinity, 48),
              ),
              child: const Text('SKIP'),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            flex: 2,
            child: ElevatedButton(
              onPressed: () => notifier.spray(),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.moderate,
              ),
              child: const Text('SPRAY'),
            ),
          ),
        ],
      );
    }

    if (state == DetectionState.spraying) {
      return ElevatedButton(
        onPressed: null,
        style: ElevatedButton.styleFrom(
          disabledBackgroundColor: AppTheme.moderate.withValues(alpha: 0.5),
        ),
        child: const Text('SPRAYING...'),
      );
    }

    return const SizedBox.shrink();
  }
}

class _StatusRow extends StatelessWidget {
  final IconData icon;
  final String text;
  final Color color;

  const _StatusRow({required this.icon, required this.text, required this.color});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 8),
          Text(text),
        ],
      ),
    );
  }
}
