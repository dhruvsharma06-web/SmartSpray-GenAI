import '../models/field_analysis.dart';
import '../models/decision_result.dart';
import '../models/field_zone.dart';
import '../models/history_record.dart';

enum DemoScenario {
  tomatoEarlyBlight,
  diseaseHeavyRain,
  healthyCrop,
  lowSoilMoisture,
  lowConfidence,
}

class DemoScenarioData {
  final String title;
  final String description;
  final FieldAnalysisOutput analysis;
  final DecisionResult decision;

  DemoScenarioData({
    required this.title,
    required this.description,
    required this.analysis,
    required this.decision,
  });
}

class DemoService {
  static final Map<DemoScenario, DemoScenarioData> scenarios = {
    DemoScenario.tomatoEarlyBlight: DemoScenarioData(
      title: '1. Tomato Early Blight (Spray)',
      description: 'High confidence early blight with verified Mancozeb treatment and suitable weather.',
      analysis: FieldAnalysisOutput(
        crop: CropSummary(name: 'tomato', confidence: 0.92),
        disease: DiseaseSummary(name: 'early_blight', confidence: 0.88),
        pests: [],
        nutrientDeficiency: null,
        severity: SeveritySummary(level: 'high', affectedAreaPercent: 35.0),
        climateRisk: ClimateRiskSummary(drought: 0.2, heat: 0.2, flood: 0.0, waterlogging: 0.0),
        requiresConfirmation: false,
        metadata: {
          'knowledge_retrieval': {
            'found': true,
            'records': [
              {
                'product': 'Mancozeb 75% WP (SAMPLE DATA)',
                'active_ingredient': 'Mancozeb',
                'formulation': 'WP',
                'application_method': 'Foliar spray',
                'label_rate': '2.5 g/L of water',
                'pre_harvest_interval_days': 7,
                'safety_information': 'SAMPLE DATA — Wear protective gloves and mask during application.',
                'source': 'SAMPLE — CIBRC Regulatory Reference',
              }
            ]
          },
          'explanation': {
            'summary': 'Early Blight detected on Tomato foliage (88% confidence). High severity (35% leaf area). Verified treatment option available.',
            'sections': {
              'what_detected': 'Crop: Tomato (92%). Disease: Early Blight (88%). No pests detected.',
              'confidence': 'Crop ID: High (92%); Disease ID: High (88%).',
              'severity_risk': 'Overall severity: High. Affected area: 35.0%. Climate risk: Low.',
              'why_it_matters': 'Early Blight can cause severe defoliation and yield loss if left untreated.',
              'recommended_action': 'Verified option: Mancozeb 75% WP at 2.5 g/L water (Foliar spray, PHI: 7 days).',
              'confirmation_warning': '',
            }
          }
        },
      ),
      decision: DecisionResult(
        action: ActionType.SPRAY,
        reason: 'Verified spray recommended for tomato target \'early blight\' using Mancozeb 75% WP. Weather conditions are safe.',
        priority: PriorityLevel.HIGH,
        requiresConfirmation: false,
        safetyStatus: 'SAFE_TO_SPRAY',
        verifiedTreatment: {
          'product': 'Mancozeb 75% WP (SAMPLE DATA)',
          'active_ingredient': 'Mancozeb',
          'label_rate': '2.5 g/L of water',
          'pre_harvest_interval_days': 7,
          'safety_information': 'SAMPLE DATA — Wear PPE during spraying.',
          'source': 'CIBRC Sample Registration',
        },
        audit: DecisionAudit(
          triggeredRules: ['RULE_RECOMMEND_SPRAY'],
          inputsConsidered: {'crop': 'tomato', 'disease': 'early_blight', 'severity': 'high'},
          timestamp: DateTime.now().toIso8601String(),
        ),
      ),
    ),

    DemoScenario.diseaseHeavyRain: DemoScenarioData(
      title: '2. Disease + Heavy Rain (Delay)',
      description: 'Early blight detected, but 25mm heavy rain forecast delays spraying.',
      analysis: FieldAnalysisOutput(
        crop: CropSummary(name: 'tomato', confidence: 0.92),
        disease: DiseaseSummary(name: 'early_blight', confidence: 0.88),
        pests: [],
        nutrientDeficiency: null,
        severity: SeveritySummary(level: 'high', affectedAreaPercent: 35.0),
        climateRisk: ClimateRiskSummary(drought: 0.1, heat: 0.2, flood: 0.4, waterlogging: 0.3),
        requiresConfirmation: false,
        metadata: {
          'knowledge_retrieval': {
            'found': true,
            'records': [
              {
                'product': 'Mancozeb 75% WP (SAMPLE DATA)',
                'active_ingredient': 'Mancozeb',
                'label_rate': '2.5 g/L of water',
                'pre_harvest_interval_days': 7,
                'source': 'SAMPLE — CIBRC Reference',
              }
            ]
          },
          'explanation': {
            'summary': 'Early Blight detected. Spraying is DELAYED due to 25.0mm expected rain forecast to prevent wash-off.',
            'sections': {
              'what_detected': 'Crop: Tomato (92%). Disease: Early Blight (88%).',
              'confidence': 'High confidence.',
              'severity_risk': 'High severity. Climate risk: Rain forecast 25mm.',
              'why_it_matters': 'Heavy rain will wash away chemical application.',
              'recommended_action': 'Hold spraying until rain passes.',
              'confirmation_warning': '',
            }
          }
        },
      ),
      decision: DecisionResult(
        action: ActionType.DELAY,
        reason: 'Target condition \'early blight\' identified with verified treatment (Mancozeb 75% WP), but application is DELAYED due to heavy rainfall forecast (25.0mm).',
        priority: PriorityLevel.HIGH,
        requiresConfirmation: false,
        safetyStatus: 'WEATHER_DELAY',
        verifiedTreatment: {
          'product': 'Mancozeb 75% WP (SAMPLE DATA)',
          'active_ingredient': 'Mancozeb',
          'label_rate': '2.5 g/L of water',
          'pre_harvest_interval_days': 7,
        },
        audit: DecisionAudit(
          triggeredRules: ['RULE_SPRAY_DELAY_WEATHER'],
          inputsConsidered: {'rain_24h_mm': 25.0},
          timestamp: DateTime.now().toIso8601String(),
        ),
      ),
    ),

    DemoScenario.healthyCrop: DemoScenarioData(
      title: '3. Healthy Crop (No Action)',
      description: 'Crop foliage appears healthy with normal soil moisture and low climate risk.',
      analysis: FieldAnalysisOutput(
        crop: CropSummary(name: 'potato', confidence: 0.96),
        disease: DiseaseSummary(name: 'healthy', confidence: 0.98),
        pests: [],
        nutrientDeficiency: null,
        severity: SeveritySummary(level: 'healthy', affectedAreaPercent: 0.0),
        climateRisk: ClimateRiskSummary(drought: 0.05, heat: 0.1, flood: 0.0, waterlogging: 0.0),
        requiresConfirmation: false,
        metadata: {
          'explanation': {
            'summary': 'Potato crop appears healthy without disease or pest symptoms. Environmental conditions are optimal.',
            'sections': {
              'what_detected': 'Potato (96% conf). Foliage appears healthy.',
              'confidence': 'High confidence (96%).',
              'severity_risk': 'Healthy (0% affected area).',
              'why_it_matters': 'No intervention required.',
              'recommended_action': 'Continue regular crop monitoring.',
              'confirmation_warning': '',
            }
          }
        },
      ),
      decision: DecisionResult(
        action: ActionType.NO_ACTION,
        reason: 'Crop \'potato\' appears healthy with no active disease/pest infestation, normal soil moisture, and low climate risk. No intervention required.',
        priority: PriorityLevel.LOW,
        requiresConfirmation: false,
        safetyStatus: 'FIELD_HEALTHY',
        audit: DecisionAudit(
          triggeredRules: ['RULE_NO_ACTION'],
          inputsConsidered: {'crop': 'potato', 'healthy': true},
          timestamp: DateTime.now().toIso8601String(),
        ),
      ),
    ),

    DemoScenario.lowSoilMoisture: DemoScenarioData(
      title: '4. Low Moisture + Heat (Irrigate)',
      description: 'Soil moisture is 14.5% with 37°C air temp and high drought risk.',
      analysis: FieldAnalysisOutput(
        crop: CropSummary(name: 'tomato', confidence: 0.95),
        disease: DiseaseSummary(name: 'healthy', confidence: 0.94),
        pests: [],
        nutrientDeficiency: null,
        severity: SeveritySummary(level: 'healthy', affectedAreaPercent: 0.0),
        climateRisk: ClimateRiskSummary(drought: 0.78, heat: 0.65, flood: 0.0, waterlogging: 0.0),
        requiresConfirmation: false,
        metadata: {
          'explanation': {
            'summary': 'Low soil moisture (14.5%) and high drought risk (78%). Controlled irrigation cycle recommended.',
            'sections': {
              'what_detected': 'Tomato crop foliage healthy, but root zone is dry.',
              'confidence': 'High confidence.',
              'severity_risk': 'Drought risk: High (78%). Heat risk: Moderate (65%).',
              'why_it_matters': 'Prolonged dry soil under high heat will cause flower drop.',
              'recommended_action': 'Apply supplemental drip irrigation for 30 minutes.',
              'confirmation_warning': '',
            }
          }
        },
      ),
      decision: DecisionResult(
        action: ActionType.IRRIGATE,
        reason: 'Soil moisture (14.5%) and drought risk (78%) indicate water stress. Drip irrigation recommended for 30 minutes.',
        priority: PriorityLevel.HIGH,
        requiresConfirmation: false,
        safetyStatus: 'SAFE_TO_IRRIGATE',
        durationMinutes: 30.0,
        audit: DecisionAudit(
          triggeredRules: ['RULE_RECOMMEND_IRRIGATE'],
          inputsConsidered: {'soil_moisture': 14.5, 'drought_risk': 0.78},
          timestamp: DateTime.now().toIso8601String(),
        ),
      ),
    ),

    DemoScenario.lowConfidence: DemoScenarioData(
      title: '5. Low Confidence (Warn)',
      description: 'AI model confidence is 45% (below 60% threshold). Operator confirmation required.',
      analysis: FieldAnalysisOutput(
        crop: CropSummary(name: 'unknown_plant', confidence: 0.45),
        disease: DiseaseSummary(name: 'unclear_leaf_spot', confidence: 0.45),
        pests: [],
        nutrientDeficiency: null,
        severity: SeveritySummary(level: 'moderate', affectedAreaPercent: 20.0),
        climateRisk: ClimateRiskSummary(drought: 0.1, heat: 0.1, flood: 0.0, waterlogging: 0.0),
        requiresConfirmation: true,
        metadata: {
          'explanation': {
            'summary': 'AI confidence (45%) is low. Expert on-field confirmation is required before taking action.',
            'sections': {
              'what_detected': 'Possible leaf spot detected, but image quality or symptoms are ambiguous.',
              'confidence': 'Low confidence (45% < 60% threshold).',
              'severity_risk': 'Moderate severity (20% area).',
              'why_it_matters': 'Low confidence prevents automated decision making.',
              'recommended_action': 'Perform visual physical inspection.',
              'confirmation_warning': '⚠️ Low confidence. Farmer confirmation required.',
            }
          }
        },
      ),
      decision: DecisionResult(
        action: ActionType.WARN,
        reason: 'AI diagnosis confidence (45%) is below reliability threshold (60%). On-field expert confirmation required before automated action.',
        priority: PriorityLevel.HIGH,
        requiresConfirmation: true,
        safetyStatus: 'CONFIRMATION_REQUIRED',
        audit: DecisionAudit(
          triggeredRules: ['RULE_CONFIRMATION_REQUIRED'],
          inputsConsidered: {'crop_confidence': 0.45, 'disease_confidence': 0.45},
          timestamp: DateTime.now().toIso8601String(),
        ),
      ),
    ),
  };

  static List<FieldZone> getDemoZones() {
    final now = DateTime.now();
    return [
      FieldZone(
        id: 'Z-01',
        label: 'Zone A1 — Tomato Early Blight',
        gridX: 0.25,
        gridY: 0.30,
        crop: 'Tomato',
        issueType: ZoneIssueType.disease,
        detectedIssue: 'Early Blight',
        confidence: 0.88,
        severity: 'High (35%)',
        climateRiskSummary: 'Low Risk',
        recommendedAction: 'SPRAY (Mancozeb 75% WP)',
        timestamp: now.subtract(const Duration(minutes: 15)),
      ),
      FieldZone(
        id: 'Z-02',
        label: 'Zone A2 — Potato Healthy',
        gridX: 0.70,
        gridY: 0.25,
        crop: 'Potato',
        issueType: ZoneIssueType.healthy,
        detectedIssue: 'Healthy Foliage',
        confidence: 0.98,
        severity: 'Healthy (0%)',
        climateRiskSummary: 'Low Risk',
        recommendedAction: 'NO_ACTION',
        timestamp: now.subtract(const Duration(minutes: 42)),
      ),
      FieldZone(
        id: 'Z-03',
        label: 'Zone B1 — Tomato Aphid Spot',
        gridX: 0.35,
        gridY: 0.65,
        crop: 'Tomato',
        issueType: ZoneIssueType.pest,
        detectedIssue: 'Aphid Infestation (4 count)',
        confidence: 0.85,
        severity: 'Moderate',
        climateRiskSummary: 'Low Risk',
        recommendedAction: 'SPRAY (Verified Organic Neem)',
        timestamp: now.subtract(const Duration(hours: 1, minutes: 10)),
      ),
      FieldZone(
        id: 'Z-04',
        label: 'Zone B2 — Potato Nitrogen Risk',
        gridX: 0.80,
        gridY: 0.60,
        crop: 'Potato',
        issueType: ZoneIssueType.nutrient,
        detectedIssue: 'Nitrogen Deficiency (Visual)',
        confidence: 0.72,
        severity: 'Moderate',
        climateRiskSummary: 'Soil Test Recommended',
        recommendedAction: 'Soil/Tissue Test',
        timestamp: now.subtract(const Duration(hours: 2)),
      ),
      FieldZone(
        id: 'Z-05',
        label: 'Zone C1 — Dry Moisture Area',
        gridX: 0.20,
        gridY: 0.80,
        crop: 'Tomato',
        issueType: ZoneIssueType.irrigation,
        detectedIssue: 'Low Soil Moisture (14.5%)',
        confidence: 0.95,
        severity: 'High Drought Risk (78%)',
        climateRiskSummary: 'Heat 37°C',
        recommendedAction: 'IRRIGATE (30 mins)',
        timestamp: now.subtract(const Duration(hours: 3)),
      ),
      FieldZone(
        id: 'Z-06',
        label: 'Zone C2 — Unclear Spot (Low Conf)',
        gridX: 0.60,
        gridY: 0.85,
        crop: 'Potato',
        issueType: ZoneIssueType.critical,
        detectedIssue: 'Unclear Spot (45% Conf)',
        confidence: 0.45,
        severity: 'Moderate',
        climateRiskSummary: 'Low Risk',
        recommendedAction: 'WARN (Farmer Confirm)',
        timestamp: now.subtract(const Duration(hours: 4)),
      ),
    ];
  }

  static List<HistoryRecord> getDemoHistory() {
    final now = DateTime.now();
    return [
      HistoryRecord(
        id: 'HIST-101',
        timestamp: now.subtract(const Duration(minutes: 15)),
        crop: 'Tomato',
        diseaseOrPest: 'Early Blight',
        confidence: 0.88,
        severity: 'High (35%)',
        actionTaken: 'SPRAY (Mancozeb)',
        soilMoisture: 40.0,
        airTemp: 26.0,
        notes: 'Verified spray recommended by Decision Engine.',
      ),
      HistoryRecord(
        id: 'HIST-102',
        timestamp: now.subtract(const Duration(hours: 2)),
        crop: 'Tomato',
        diseaseOrPest: 'Early Blight',
        confidence: 0.88,
        severity: 'High',
        actionTaken: 'DELAY (Heavy Rain 25mm)',
        soilMoisture: 45.0,
        airTemp: 22.0,
        notes: 'Application delayed due to rain forecast.',
      ),
      HistoryRecord(
        id: 'HIST-103',
        timestamp: now.subtract(const Duration(hours: 5)),
        crop: 'Potato',
        diseaseOrPest: 'Healthy',
        confidence: 0.98,
        severity: 'Healthy',
        actionTaken: 'NO_ACTION',
        soilMoisture: 45.0,
        airTemp: 24.0,
        notes: 'Routine scanning: foliage healthy.',
      ),
      HistoryRecord(
        id: 'HIST-104',
        timestamp: now.subtract(const Duration(hours: 8)),
        crop: 'Tomato',
        diseaseOrPest: 'Dry Soil Stress',
        confidence: 0.95,
        severity: 'High Drought (78%)',
        actionTaken: 'IRRIGATE (30 mins)',
        soilMoisture: 14.5,
        airTemp: 37.0,
        notes: 'Drip irrigation cycle completed.',
      ),
      HistoryRecord(
        id: 'HIST-105',
        timestamp: now.subtract(const Duration(hours: 12)),
        crop: 'Unknown',
        diseaseOrPest: 'Unclear Spot',
        confidence: 0.45,
        severity: 'Moderate',
        actionTaken: 'WARN (Farmer Confirm)',
        soilMoisture: 38.0,
        airTemp: 27.0,
        notes: 'Low confidence scan flagged for operator inspection.',
      ),
    ];
  }
}
