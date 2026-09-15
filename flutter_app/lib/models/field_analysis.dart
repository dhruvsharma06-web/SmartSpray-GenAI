/// Dart data models matching Person 1 FieldAnalysisOutput JSON contract.
library;

class CropSummary {
  final String name;
  final double confidence;

  CropSummary({required this.name, required this.confidence});

  factory CropSummary.fromJson(Map<String, dynamic> json) {
    return CropSummary(
      name: json['name'] as String? ?? 'unknown',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() => {'name': name, 'confidence': confidence};
}

class DiseaseSummary {
  final String name;
  final double confidence;

  DiseaseSummary({required this.name, required this.confidence});

  factory DiseaseSummary.fromJson(Map<String, dynamic> json) {
    return DiseaseSummary(
      name: json['name'] as String? ?? 'healthy',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() => {'name': name, 'confidence': confidence};
}

class SeveritySummary {
  final String level;
  final double? affectedAreaPercent;

  SeveritySummary({required this.level, this.affectedAreaPercent});

  factory SeveritySummary.fromJson(Map<String, dynamic> json) {
    return SeveritySummary(
      level: json['level'] as String? ?? 'healthy',
      affectedAreaPercent: (json['affected_area_percent'] as num?)?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
        'level': level,
        'affected_area_percent': affectedAreaPercent,
      };
}

class ClimateRiskSummary {
  final double drought;
  final double heat;
  final double flood;
  final double waterlogging;

  ClimateRiskSummary({
    required this.drought,
    required this.heat,
    required this.flood,
    required this.waterlogging,
  });

  factory ClimateRiskSummary.fromJson(Map<String, dynamic> json) {
    return ClimateRiskSummary(
      drought: (json['drought'] as num?)?.toDouble() ?? 0.0,
      heat: (json['heat'] as num?)?.toDouble() ?? 0.0,
      flood: (json['flood'] as num?)?.toDouble() ?? 0.0,
      waterlogging: (json['waterlogging'] as num?)?.toDouble() ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() => {
        'drought': drought,
        'heat': heat,
        'flood': flood,
        'waterlogging': waterlogging,
      };
}

class DetectedPestItem {
  final String pestType;
  final double confidence;

  DetectedPestItem({required this.pestType, required this.confidence});

  factory DetectedPestItem.fromJson(Map<String, dynamic> json) {
    return DetectedPestItem(
      pestType: json['pest_type'] as String? ?? 'unknown',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() => {
        'pest_type': pestType,
        'confidence': confidence,
      };
}

class FieldAnalysisOutput {
  final CropSummary crop;
  final DiseaseSummary? disease;
  final List<DetectedPestItem> pests;
  final String? nutrientDeficiency;
  final SeveritySummary? severity;
  final ClimateRiskSummary climateRisk;
  final bool requiresConfirmation;
  final Map<String, dynamic>? metadata;

  FieldAnalysisOutput({
    required this.crop,
    this.disease,
    required this.pests,
    this.nutrientDeficiency,
    this.severity,
    required this.climateRisk,
    required this.requiresConfirmation,
    this.metadata,
  });

  factory FieldAnalysisOutput.fromJson(Map<String, dynamic> json) {
    final pestsRaw = json['pests'] as List? ?? [];
    return FieldAnalysisOutput(
      crop: CropSummary.fromJson(json['crop'] as Map<String, dynamic>? ?? {}),
      disease: json['disease'] != null
          ? DiseaseSummary.fromJson(json['disease'] as Map<String, dynamic>)
          : null,
      pests: pestsRaw
          .map((e) => DetectedPestItem.fromJson(e as Map<String, dynamic>))
          .toList(),
      nutrientDeficiency: json['nutrient_deficiency'] as String?,
      severity: json['severity'] != null
          ? SeveritySummary.fromJson(json['severity'] as Map<String, dynamic>)
          : null,
      climateRisk: ClimateRiskSummary.fromJson(
          json['climate_risk'] as Map<String, dynamic>? ?? {}),
      requiresConfirmation: json['requires_confirmation'] as bool? ?? false,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() => {
        'crop': crop.toJson(),
        if (disease != null) 'disease': disease!.toJson(),
        'pests': pests.map((p) => p.toJson()).toList(),
        'nutrient_deficiency': nutrientDeficiency,
        if (severity != null) 'severity': severity!.toJson(),
        'climate_risk': climateRisk.toJson(),
        'requires_confirmation': requiresConfirmation,
        if (metadata != null) 'metadata': metadata,
      };
}
