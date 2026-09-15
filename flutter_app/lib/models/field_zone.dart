/// Data model for Field Plot Zones & Marker Points.
library;

enum ZoneIssueType { healthy, disease, pest, nutrient, irrigation, critical }

class FieldZone {
  final String id;
  final String label;
  final double gridX; // Normalized 0.0 - 1.0 within field plot
  final double gridY; // Normalized 0.0 - 1.0 within field plot
  final String crop;
  final ZoneIssueType issueType;
  final String detectedIssue;
  final double confidence;
  final String severity;
  final String climateRiskSummary;
  final String recommendedAction;
  final DateTime timestamp;

  FieldZone({
    required this.id,
    required this.label,
    required this.gridX,
    required this.gridY,
    required this.crop,
    required this.issueType,
    required this.detectedIssue,
    required this.confidence,
    required this.severity,
    required this.climateRiskSummary,
    required this.recommendedAction,
    required this.timestamp,
  });
}
