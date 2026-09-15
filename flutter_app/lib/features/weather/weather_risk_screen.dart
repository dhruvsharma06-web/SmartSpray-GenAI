import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../app/theme.dart';
import '../../providers/app_state_provider.dart';

class WeatherRiskScreen extends ConsumerWidget {
  const WeatherRiskScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final appState = ref.watch(appStateProvider);
    final risk = appState.currentAnalysis.climateRisk;

    return Scaffold(
      appBar: AppBar(
        title: const Text('WEATHER & CLIMATE RISK'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Current Weather Card
            Card(
              elevation: 2,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            Icon(Icons.cloud, color: AppTheme.info, size: 22),
                            SizedBox(width: 8),
                            Text(
                              'TELEMETRY & WEATHER FORECAST',
                              style: TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                                color: AppTheme.primaryDark,
                              ),
                            ),
                          ],
                        ),
                        Text(
                          'LIVE SENSORS',
                          style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppTheme.success),
                        ),
                      ],
                    ),
                    const Divider(),
                    const SizedBox(height: 8),
                    const Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        _WeatherItem(label: 'Air Temp', value: '26.0°C', icon: Icons.thermostat),
                        _WeatherItem(label: 'Humidity', value: '55.0%', icon: Icons.water_drop),
                        _WeatherItem(label: '24h Rain', value: '0.0 mm', icon: Icons.umbrella),
                        _WeatherItem(label: 'Soil Moist', value: '40.0%', icon: Icons.opacity),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),

            // Climate Risk Vectors
            const Text(
              'CLIMATE RISK VECTORS',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.text),
            ),
            const SizedBox(height: 12),
            _RiskVectorTile(
              label: 'Drought Risk Index',
              value: risk.drought,
              explanation: risk.drought >= 0.5
                  ? 'High risk: Soil moisture low under intense solar radiation.'
                  : 'Low risk: Soil moisture is currently adequate for vegetative growth.',
            ),
            const SizedBox(height: 10),
            _RiskVectorTile(
              label: 'Heat-Stress Index',
              value: risk.heat,
              explanation: risk.heat >= 0.5
                  ? 'High risk: Air temp exceeds threshold. Flower drop possible.'
                  : 'Low risk: Temperatures within safe photosynthesis range.',
            ),
            const SizedBox(height: 10),
            _RiskVectorTile(
              label: 'Flood & Waterlogging Index',
              value: risk.flood > risk.waterlogging ? risk.flood : risk.waterlogging,
              explanation: risk.flood >= 0.5 || risk.waterlogging >= 0.5
                  ? 'High risk: Heavy rainfall forecast will cause surface runoff.'
                  : 'Low risk: Soil drainage capacity is optimal.',
            ),
            const SizedBox(height: 24),

            // WHAT THIS MEANS FOR THE FARMER
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppTheme.primaryLight,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: AppTheme.primary.withValues(alpha: 0.4)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.lightbulb_outline, color: AppTheme.primaryDark),
                      SizedBox(width: 8),
                      Text(
                        'WHAT THIS MEANS FOR THE FARMER',
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.bold,
                          color: AppTheme.primaryDark,
                          letterSpacing: 0.5,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Text(
                    risk.drought >= 0.5
                        ? '• Low soil moisture + high heat: Supplemental drip irrigation recommended.'
                        : (risk.flood >= 0.5
                            ? '• Heavy rainfall expected: Foliar spraying should be delayed to prevent chemical wash-off.'
                            : '• Normal environmental telemetry: No weather-related operational delays currently required.'),
                    style: const TextStyle(fontSize: 13, height: 1.4, color: AppTheme.text),
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

class _WeatherItem extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;

  const _WeatherItem({required this.label, required this.value, required this.icon});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Icon(icon, color: AppTheme.primary, size: 20),
        const SizedBox(height: 4),
        Text(value, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
        Text(label, style: const TextStyle(fontSize: 11, color: AppTheme.secondaryText)),
      ],
    );
  }
}

class _RiskVectorTile extends StatelessWidget {
  final String label;
  final double value;
  final String explanation;

  const _RiskVectorTile({required this.label, required this.value, required this.explanation});

  @override
  Widget build(BuildContext context) {
    final statusStr = value >= 0.7 ? 'HIGH' : (value >= 0.35 ? 'MEDIUM' : 'LOW');
    final color = value >= 0.7 ? AppTheme.emergency : (value >= 0.35 ? Colors.orange : AppTheme.success);

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppTheme.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(label, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(8)),
                child: Text(
                  '$statusStr (${(value * 100).toStringAsFixed(0)}%)',
                  style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          LinearProgressIndicator(
            value: value,
            backgroundColor: color.withValues(alpha: 0.15),
            valueColor: AlwaysStoppedAnimation<Color>(color),
            minHeight: 6,
          ),
          const SizedBox(height: 6),
          Text(explanation, style: const TextStyle(fontSize: 11, color: AppTheme.secondaryText)),
        ],
      ),
    );
  }
}
