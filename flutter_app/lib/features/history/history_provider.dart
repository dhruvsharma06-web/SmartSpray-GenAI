import 'package:flutter_riverpod/flutter_riverpod.dart';

class HistoryEvent {
  final DateTime timestamp;
  final String plant;
  final String disease;
  final int confidence;
  final int severity;
  final String sprayLevel;
  final String mode;
  final String status;
  final String duration;

  const HistoryEvent({
    required this.timestamp,
    required this.plant,
    required this.disease,
    required this.confidence,
    required this.severity,
    required this.sprayLevel,
    required this.mode,
    required this.status,
    required this.duration,
  });
}

enum HistoryFilter { all, sprayed, skipped, failed }

class HistoryState {
  final List<HistoryEvent> events;
  final HistoryFilter filter;

  const HistoryState({
    required this.events,
    this.filter = HistoryFilter.all,
  });

  HistoryState copyWith({
    List<HistoryEvent>? events,
    HistoryFilter? filter,
  }) {
    return HistoryState(
      events: events ?? this.events,
      filter: filter ?? this.filter,
    );
  }

  List<HistoryEvent> get filteredEvents {
    switch (filter) {
      case HistoryFilter.all:
        return events;
      case HistoryFilter.sprayed:
        return events.where((e) => e.status.toLowerCase() == 'completed').toList();
      case HistoryFilter.skipped:
        return events.where((e) => e.status.toLowerCase() == 'skipped').toList();
      case HistoryFilter.failed:
        return events.where((e) => e.status.toLowerCase() == 'failed' || e.status.toLowerCase() == 'stopped').toList();
    }
  }
}

class HistoryStateNotifier extends StateNotifier<HistoryState> {
  HistoryStateNotifier() : super(HistoryState(events: _mockEvents));

  void setFilter(HistoryFilter filter) {
    state = state.copyWith(filter: filter);
  }

  static final List<HistoryEvent> _mockEvents = [
    HistoryEvent(
      timestamp: DateTime.now().subtract(const Duration(minutes: 10)),
      plant: 'Tomato',
      disease: 'Early Blight',
      confidence: 94,
      severity: 62,
      sprayLevel: 'Moderate Spray',
      mode: 'ASSISTED',
      status: 'Completed',
      duration: '1.2s',
    ),
    HistoryEvent(
      timestamp: DateTime.now().subtract(const Duration(hours: 1)),
      plant: 'Tomato',
      disease: 'Healthy',
      confidence: 99,
      severity: 0,
      sprayLevel: 'None',
      mode: 'AUTO',
      status: 'Skipped',
      duration: '0s',
    ),
    HistoryEvent(
      timestamp: DateTime.now().subtract(const Duration(hours: 2)),
      plant: 'Tomato',
      disease: 'Late Blight',
      confidence: 88,
      severity: 85,
      sprayLevel: 'Heavy Spray',
      mode: 'ASSISTED',
      status: 'Failed',
      duration: '0s',
    ),
  ];
}

final historyStateProvider = StateNotifierProvider<HistoryStateNotifier, HistoryState>((ref) {
  return HistoryStateNotifier();
});
