import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../widgets/status_badge.dart';
import '../../widgets/stat_card.dart';
import '../../app/theme.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SMARTSPRAY'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'System Status',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            const Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                StatusBadge(label: 'Device', value: 'ONLINE', state: DeviceState.online),
                StatusBadge(label: 'AI', value: 'READY', state: DeviceState.ready),
                StatusBadge(label: 'ESP32', value: 'CONNECTED', state: DeviceState.connected),
                StatusBadge(label: 'Pump', value: 'OFF', state: DeviceState.offline),
              ],
            ),
            const SizedBox(height: 32),
            const Text(
              'Today\'s Statistics',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            const Row(
              children: [
                Expanded(child: StatCard(label: 'Plants Scanned', value: '42')),
                SizedBox(width: 16),
                Expanded(child: StatCard(label: 'Infected', value: '9')),
                SizedBox(width: 16),
                Expanded(child: StatCard(label: 'Sprayed', value: '7')),
              ],
            ),
            const SizedBox(height: 32),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppTheme.primaryLight,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppTheme.primary.withValues(alpha: 0.3)),
              ),
              child: Column(
                children: [
                  const Text(
                    'Operating Mode: ASSISTED',
                    style: TextStyle(
                      color: AppTheme.primaryDark,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'AI detects disease and recommends spray. Operator confirms.',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: AppTheme.primaryDark, fontSize: 13),
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton.icon(
                    onPressed: () {
                      context.go('/detect');
                    },
                    icon: const Icon(Icons.document_scanner),
                    label: const Text('START SCAN'),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
