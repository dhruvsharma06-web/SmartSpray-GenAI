import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../app/theme.dart';
import '../../providers/app_state_provider.dart';

class DeviceScreen extends ConsumerWidget {
  const DeviceScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final appState = ref.watch(appStateProvider);
    final notifier = ref.read(appStateProvider.notifier);

    final isConnected = appState.isEsp32Connected;
    final isPumpOn = appState.isPumpRunning;

    return Scaffold(
      appBar: AppBar(
        title: const Text('IOT & DEVICE TELEMETRY'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Connection Status Banner
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isConnected ? AppTheme.primaryLight : AppTheme.error.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: isConnected ? AppTheme.primary : AppTheme.error),
              ),
              child: Row(
                children: [
                  Icon(
                    isConnected ? Icons.wifi : Icons.wifi_off,
                    color: isConnected ? AppTheme.primary : AppTheme.error,
                    size: 28,
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          isConnected ? 'ESP32 NODE: CONNECTED' : 'ESP32 NODE: OFFLINE',
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.bold,
                            color: isConnected ? AppTheme.primaryDark : AppTheme.error,
                          ),
                        ),
                        Text(
                          isConnected
                              ? 'Device ID: ESP32-SMARTSPRAY-001 • RSSI: -62 dBm'
                              : 'Reconnecting to Wi-Fi/MQTT gateway...',
                          style: const TextStyle(fontSize: 12),
                        ),
                      ],
                    ),
                  ),
                  TextButton(
                    onPressed: () => notifier.toggleEsp32(),
                    child: Text(isConnected ? 'Disconnect' : 'Connect'),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Telemetry Gauges
            const Text(
              'LIVE SENSOR TELEMETRY',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.text),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _SensorCard(
                    title: 'Soil Moisture',
                    value: '40.0%',
                    subtitle: 'Optimum Range',
                    icon: Icons.opacity,
                    color: AppTheme.info,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _SensorCard(
                    title: 'Ambient Temp',
                    value: '26.0°C',
                    subtitle: 'Normal',
                    icon: Icons.thermostat,
                    color: Colors.orange,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _SensorCard(
                    title: 'Relative Humidity',
                    value: '55.0%',
                    subtitle: 'Normal',
                    icon: Icons.water_drop,
                    color: AppTheme.primary,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _SensorCard(
                    title: 'Rain Sensor',
                    value: 'DRY (0mm)',
                    subtitle: 'No Rain Detected',
                    icon: Icons.umbrella,
                    color: AppTheme.secondaryText,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Actuator Controls
            const Text(
              'ACTUATOR & PUMP STATUS (DEMO)',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.text),
            ),
            const SizedBox(height: 12),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            Icon(
                              Icons.power_settings_new,
                              color: isPumpOn ? AppTheme.success : AppTheme.offline,
                              size: 24,
                            ),
                            const SizedBox(width: 10),
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text('SPRAY PUMP RELAY', style: TextStyle(fontWeight: FontWeight.bold)),
                                Text(
                                  isPumpOn ? 'RUNNING (ACTIVATED)' : 'IDLE (OFF)',
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: isPumpOn ? AppTheme.success : AppTheme.secondaryText,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                        Switch(
                          value: isPumpOn,
                          onChanged: (val) => notifier.togglePump(),
                          activeThumbColor: AppTheme.primary,
                        ),
                      ],
                    ),
                    const Divider(),
                    const SizedBox(height: 6),
                    const Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Last Command Executed:', style: TextStyle(fontSize: 12, color: AppTheme.secondaryText)),
                        Text('CMD_PUMP_OFF_SUCCESS', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SensorCard extends StatelessWidget {
  final String title;
  final String value;
  final String subtitle;
  final IconData icon;
  final Color color;

  const _SensorCard({
    required this.title,
    required this.value,
    required this.subtitle,
    required this.icon,
    required this.color,
  });

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
                Icon(icon, color: color, size: 20),
                const SizedBox(width: 6),
                Text(title, style: const TextStyle(fontSize: 12, color: AppTheme.secondaryText)),
              ],
            ),
            const SizedBox(height: 8),
            Text(value, style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: color)),
            Text(subtitle, style: const TextStyle(fontSize: 11, color: AppTheme.secondaryText)),
          ],
        ),
      ),
    );
  }
}
