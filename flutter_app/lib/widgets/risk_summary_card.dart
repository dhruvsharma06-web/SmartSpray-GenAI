import 'package:flutter/material.dart';
import '../app/theme.dart';
import '../models/field_analysis.dart';

class RiskSummaryCard extends StatelessWidget {
  final ClimateRiskSummary climateRisk;
  final double soilMoisturePercent;

  const RiskSummaryCard({
    super.key,
    required this.climateRisk,
    this.soilMoisturePercent = 40.0,
  });

  String _getRiskLevelStr(double value) {
    if (value >= 0.70) return 'HIGH';
    if (value >= 0.35) return 'MEDIUM';
    return 'LOW';
  }

  Color _getRiskColor(double value) {
    if (value >= 0.70) return AppTheme.emergency;
    if (value >= 0.35) return Colors.orange;
    return AppTheme.success;
  }

  Widget _buildRiskTile(
    BuildContext context, {
    required String label,
    required double value,
    required IconData icon,
    required String explanation,
  }) {
    final statusStr = _getRiskLevelStr(value);
    final color = _getRiskColor(value);

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Icon(icon, color: color, size: 18),
                  const SizedBox(width: 6),
                  Text(
                    label,
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: color,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  statusStr,
                  style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          LinearProgressIndicator(
            value: value,
            backgroundColor: color.withValues(alpha: 0.2),
            valueColor: AlwaysStoppedAnimation<Color>(color),
            minHeight: 6,
            borderRadius: BorderRadius.circular(3),
          ),
          const SizedBox(height: 6),
          Text(
            explanation,
            style: const TextStyle(fontSize: 11, color: AppTheme.secondaryText),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'RISK & CLIMATE SUMMARY',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.text),
        ),
        const SizedBox(height: 12),
        _buildRiskTile(
          context,
          label: 'Drought Risk',
          value: climateRisk.drought,
          icon: Icons.wb_sunny_outlined,
          explanation: climateRisk.drought >= 0.5
              ? 'Soil moisture is low under elevated temperatures.'
              : 'Soil moisture levels are adequate.',
        ),
        const SizedBox(height: 8),
        _buildRiskTile(
          context,
          label: 'Heat Stress',
          value: climateRisk.heat,
          icon: Icons.thermostat_outlined,
          explanation: climateRisk.heat >= 0.5
              ? 'Air temp exceeds 35°C, potential blossom drop.'
              : 'Ambient temperature within safe vegetative range.',
        ),
        const SizedBox(height: 8),
        _buildRiskTile(
          context,
          label: 'Flood & Waterlogging',
          value: maxDouble(climateRisk.flood, climateRisk.waterlogging),
          icon: Icons.water_outlined,
          explanation: climateRisk.flood >= 0.5 || climateRisk.waterlogging >= 0.5
              ? 'Precipitation forecast or soil saturation high.'
              : 'No excessive inundation detected.',
        ),
      ],
    );
  }

  double maxDouble(double a, double b) => a > b ? a : b;
}
