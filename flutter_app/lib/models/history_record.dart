/// Field History Record Model for scans, actions, and climate trends.
library;

class HistoryRecord {
  final String id;
  final DateTime timestamp;
  final String crop;
  final String diseaseOrPest;
  final double confidence;
  final String severity;
  final String actionTaken;
  final double soilMoisture;
  final double airTemp;
  final String notes;

  HistoryRecord({
    required this.id,
    required this.timestamp,
    required this.crop,
    required this.diseaseOrPest,
    required this.confidence,
    required this.severity,
    required this.actionTaken,
    required this.soilMoisture,
    required this.airTemp,
    required this.notes,
  });
}
