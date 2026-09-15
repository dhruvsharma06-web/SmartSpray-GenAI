import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/field_analysis.dart';
import '../models/decision_result.dart';
import '../models/field_zone.dart';
import '../models/history_record.dart';
import '../services/demo_service.dart';

class AppState {
  final DemoScenario selectedScenario;
  final String farmName;
  final String farmerName;
  final List<FieldZone> zones;
  final FieldZone? selectedZone;
  final List<HistoryRecord> history;
  final bool isEsp32Connected;
  final bool isPumpRunning;
  final String activeFilter;

  AppState({
    required this.selectedScenario,
    this.farmName = 'Green Acres Plot #4 (Tomato & Potato)',
    this.farmerName = 'Ramesh Patel',
    required this.zones,
    this.selectedZone,
    required this.history,
    this.isEsp32Connected = true,
    this.isPumpRunning = false,
    this.activeFilter = 'All',
  });

  DemoScenarioData get currentScenarioData =>
      DemoService.scenarios[selectedScenario]!;

  FieldAnalysisOutput get currentAnalysis => currentScenarioData.analysis;

  DecisionResult get currentDecision => currentScenarioData.decision;

  AppState copyWith({
    DemoScenario? selectedScenario,
    String? farmName,
    String? farmerName,
    List<FieldZone>? zones,
    FieldZone? selectedZone,
    bool clearSelectedZone = false,
    List<HistoryRecord>? history,
    bool? isEsp32Connected,
    bool? isPumpRunning,
    String? activeFilter,
  }) {
    return AppState(
      selectedScenario: selectedScenario ?? this.selectedScenario,
      farmName: farmName ?? this.farmName,
      farmerName: farmerName ?? this.farmerName,
      zones: zones ?? this.zones,
      selectedZone: clearSelectedZone ? null : (selectedZone ?? this.selectedZone),
      history: history ?? this.history,
      isEsp32Connected: isEsp32Connected ?? this.isEsp32Connected,
      isPumpRunning: isPumpRunning ?? this.isPumpRunning,
      activeFilter: activeFilter ?? this.activeFilter,
    );
  }
}

class AppStateNotifier extends Notifier<AppState> {
  @override
  AppState build() {
    return AppState(
      selectedScenario: DemoScenario.tomatoEarlyBlight,
      zones: DemoService.getDemoZones(),
      history: DemoService.getDemoHistory(),
    );
  }

  void selectScenario(DemoScenario scenario) {
    state = state.copyWith(selectedScenario: scenario);
  }

  void selectZone(FieldZone? zone) {
    if (zone == null) {
      state = state.copyWith(clearSelectedZone: true);
    } else {
      state = state.copyWith(selectedZone: zone);
    }
  }

  void setFilter(String filter) {
    state = state.copyWith(activeFilter: filter);
  }

  void togglePump() {
    state = state.copyWith(isPumpRunning: !state.isPumpRunning);
  }

  void toggleEsp32() {
    state = state.copyWith(isEsp32Connected: !state.isEsp32Connected);
  }

  void addScanResult(FieldAnalysisOutput analysis, DecisionResult decision) {
    final newRecord = HistoryRecord(
      id: 'HIST-${DateTime.now().millisecondsSinceEpoch.toString().substring(7)}',
      timestamp: DateTime.now(),
      crop: analysis.crop.name.toUpperCase(),
      diseaseOrPest: analysis.disease?.name.replaceAll('_', ' ').toUpperCase() ?? 'HEALTHY',
      confidence: analysis.disease?.confidence ?? analysis.crop.confidence,
      severity: analysis.severity?.level.toUpperCase() ?? 'HEALTHY',
      actionTaken: decision.action.name,
      soilMoisture: 40.0,
      airTemp: 26.0,
      notes: 'New scan added via Scan screen.',
    );

    state = state.copyWith(
      history: [newRecord, ...state.history],
    );
  }
}

final appStateProvider =
    NotifierProvider<AppStateNotifier, AppState>(AppStateNotifier.new);
