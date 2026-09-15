// ignore_for_file: constant_identifier_names
/// Dart data models matching Person 3 DecisionResult JSON contract.
library;

enum ActionType { SPRAY, IRRIGATE, WARN, DELAY, NO_ACTION }

enum PriorityLevel { LOW, MEDIUM, HIGH, CRITICAL }


class DecisionAudit {
  final List<String> triggeredRules;
  final Map<String, dynamic> inputsConsidered;
  final String timestamp;

  DecisionAudit({
    required this.triggeredRules,
    required this.inputsConsidered,
    required this.timestamp,
  });

  factory DecisionAudit.fromJson(Map<String, dynamic> json) {
    return DecisionAudit(
      triggeredRules: (json['triggered_rules'] as List? ?? [])
          .map((e) => e.toString())
          .toList(),
      inputsConsidered:
          json['inputs_considered'] as Map<String, dynamic>? ?? {},
      timestamp: json['timestamp'] as String? ?? '',
    );
  }

  Map<String, dynamic> toJson() => {
        'triggered_rules': triggeredRules,
        'inputs_considered': inputsConsidered,
        'timestamp': timestamp,
      };
}

class DecisionResult {
  final ActionType action;
  final String reason;
  final PriorityLevel priority;
  final bool requiresConfirmation;
  final String safetyStatus;
  final double? durationMinutes;
  final Map<String, dynamic>? verifiedTreatment;
  final DecisionAudit audit;

  DecisionResult({
    required this.action,
    required this.reason,
    required this.priority,
    required this.requiresConfirmation,
    required this.safetyStatus,
    this.durationMinutes,
    this.verifiedTreatment,
    required this.audit,
  });

  factory DecisionResult.fromJson(Map<String, dynamic> json) {
    final actionStr = json['action'] as String? ?? 'NO_ACTION';
    final priorityStr = json['priority'] as String? ?? 'LOW';

    return DecisionResult(
      action: ActionType.values.firstWhere(
        (e) => e.name == actionStr,
        orElse: () => ActionType.NO_ACTION,
      ),
      reason: json['reason'] as String? ?? '',
      priority: PriorityLevel.values.firstWhere(
        (e) => e.name == priorityStr,
        orElse: () => PriorityLevel.LOW,
      ),
      requiresConfirmation: json['requires_confirmation'] as bool? ?? false,
      safetyStatus: json['safety_status'] as String? ?? 'FIELD_HEALTHY',
      durationMinutes: (json['duration_minutes'] as num?)?.toDouble(),
      verifiedTreatment: json['verified_treatment'] as Map<String, dynamic>?,
      audit: DecisionAudit.fromJson(
          json['audit'] as Map<String, dynamic>? ?? {}),
    );
  }

  Map<String, dynamic> toJson() => {
        'action': action.name,
        'reason': reason,
        'priority': priority.name,
        'requires_confirmation': requiresConfirmation,
        'safety_status': safetyStatus,
        if (durationMinutes != null) 'duration_minutes': durationMinutes,
        if (verifiedTreatment != null) 'verified_treatment': verifiedTreatment,
        'audit': audit.toJson(),
      };
}
