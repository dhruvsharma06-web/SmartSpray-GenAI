import 'package:flutter/material.dart';
import '../app/theme.dart';
import '../models/field_zone.dart';

class InteractiveFieldMap extends StatelessWidget {
  final List<FieldZone> zones;
  final FieldZone? selectedZone;
  final ValueChanged<FieldZone> onZoneSelected;
  final String activeFilter;

  const InteractiveFieldMap({
    super.key,
    required this.zones,
    this.selectedZone,
    required this.onZoneSelected,
    this.activeFilter = 'All',
  });

  Color _getMarkerColor(ZoneIssueType issueType) {
    switch (issueType) {
      case ZoneIssueType.healthy:
        return AppTheme.success;
      case ZoneIssueType.disease:
        return AppTheme.error;
      case ZoneIssueType.pest:
        return Colors.purple;
      case ZoneIssueType.nutrient:
        return AppTheme.warning;
      case ZoneIssueType.irrigation:
        return AppTheme.info;
      case ZoneIssueType.critical:
        return AppTheme.emergency;
    }
  }

  IconData _getMarkerIcon(ZoneIssueType issueType) {
    switch (issueType) {
      case ZoneIssueType.healthy:
        return Icons.check_circle;
      case ZoneIssueType.disease:
        return Icons.coronavirus;
      case ZoneIssueType.pest:
        return Icons.bug_report;
      case ZoneIssueType.nutrient:
        return Icons.opacity;
      case ZoneIssueType.irrigation:
        return Icons.water_drop;
      case ZoneIssueType.critical:
        return Icons.warning_amber_rounded;
    }
  }

  bool _isZoneVisible(FieldZone zone) {
    if (activeFilter == 'All') return true;
    if (activeFilter == 'Disease' && zone.issueType == ZoneIssueType.disease) return true;
    if (activeFilter == 'Pest' && zone.issueType == ZoneIssueType.pest) return true;
    if (activeFilter == 'Nutrient' && zone.issueType == ZoneIssueType.nutrient) return true;
    if (activeFilter == 'Irrigation' && zone.issueType == ZoneIssueType.irrigation) return true;
    if (activeFilter == 'Critical' && zone.issueType == ZoneIssueType.critical) return true;
    return false;
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: const BoxDecoration(
              color: AppTheme.primaryDark,
              borderRadius: BorderRadius.only(
                topLeft: Radius.circular(16),
                topRight: Radius.circular(16),
              ),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Row(
                  children: [
                    Icon(Icons.map_outlined, color: Colors.white, size: 20),
                    SizedBox(width: 8),
                    Text(
                      'FIELD PLOT MAP (INTERACTIVE DEMO)',
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 13,
                        letterSpacing: 0.5,
                      ),
                    ),
                  ],
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Text(
                    'Plot #4 — 2.5 Acres',
                    style: TextStyle(color: Colors.white, fontSize: 11),
                  ),
                ),
              ],
            ),
          ),
          AspectRatio(
            aspectRatio: 1.6,
            child: Container(
              margin: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFFE2EFE0), // Field soil background
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppTheme.primary.withValues(alpha: 0.4), width: 2),
              ),
              child: Stack(
                children: [
                  // Grid lines
                  CustomPaint(
                    size: Size.infinite,
                    painter: _GridPainter(),
                  ),

                  // Plot orientation indicator
                  const Positioned(
                    top: 8,
                    left: 8,
                    child: Text(
                      'N ⬆ North Crop Row',
                      style: TextStyle(fontSize: 10, color: AppTheme.secondaryText, fontWeight: FontWeight.bold),
                    ),
                  ),

                  // Zone Markers
                  ...zones.where(_isZoneVisible).map((zone) {
                    final isSelected = selectedZone?.id == zone.id;
                    final color = _getMarkerColor(zone.issueType);
                    return Positioned(
                      left: zone.gridX * 280,
                      top: zone.gridY * 150,
                      child: GestureDetector(
                        onTap: () => onZoneSelected(zone),
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 250),
                          padding: const EdgeInsets.all(4),
                          decoration: BoxDecoration(
                            color: isSelected ? Colors.white : color.withValues(alpha: 0.9),
                            shape: BoxShape.circle,
                            border: Border.all(
                              color: isSelected ? color : Colors.white,
                              width: isSelected ? 3 : 2,
                            ),
                            boxShadow: [
                              BoxShadow(
                                color: color.withValues(alpha: 0.4),
                                blurRadius: isSelected ? 10 : 4,
                                spreadRadius: isSelected ? 3 : 1,
                              )
                            ],
                          ),
                          child: Icon(
                            _getMarkerIcon(zone.issueType),
                            color: isSelected ? color : Colors.white,
                            size: isSelected ? 24 : 18,
                          ),
                        ),
                      ),
                    );
                  }),
                ],
              ),
            ),
          ),
          // Legend
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            child: Wrap(
              spacing: 12,
              runSpacing: 6,
              children: const [
                _LegendItem(color: AppTheme.success, label: 'Healthy'),
                _LegendItem(color: AppTheme.error, label: 'Disease'),
                _LegendItem(color: Colors.purple, label: 'Pest'),
                _LegendItem(color: AppTheme.warning, label: 'Nutrient'),
                _LegendItem(color: AppTheme.info, label: 'Irrigation'),
                _LegendItem(color: AppTheme.emergency, label: 'Critical'),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _LegendItem extends StatelessWidget {
  final Color color;
  final String label;

  const _LegendItem({required this.color, required this.label});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 10,
          height: 10,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 4),
        Text(label, style: const TextStyle(fontSize: 11, color: AppTheme.secondaryText)),
      ],
    );
  }
}

class _GridPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = AppTheme.primary.withValues(alpha: 0.12)
      ..strokeWidth = 1.0;

    for (double i = 0; i < size.width; i += 40) {
      canvas.drawLine(Offset(i, 0), Offset(i, size.height), paint);
    }
    for (double j = 0; j < size.height; j += 35) {
      canvas.drawLine(Offset(0, j), Offset(size.width, j), paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
