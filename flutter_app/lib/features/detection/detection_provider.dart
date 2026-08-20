import 'package:flutter_riverpod/flutter_riverpod.dart';

enum DetectionState {
  idle,
  scanning,
  plantDetected,
  leafDetected,
  diseaseDetected,
  targetReady,
  waitingForConfirmation,
  spraying,
  sprayCompleted,
  error,
  offline
}

class DetectionStateNotifier extends StateNotifier<DetectionState> {
  DetectionStateNotifier() : super(DetectionState.idle);

  void startScan() {
    state = DetectionState.scanning;
    _mockFlow();
  }

  void _mockFlow() async {
    await Future.delayed(const Duration(seconds: 1));
    if (state != DetectionState.scanning) return;
    setPlantDetected();
    await Future.delayed(const Duration(seconds: 1));
    if (state != DetectionState.plantDetected) return;
    setLeafDetected();
    await Future.delayed(const Duration(seconds: 1));
    if (state != DetectionState.leafDetected) return;
    setDiseaseDetected();
    await Future.delayed(const Duration(seconds: 1));
    if (state != DetectionState.diseaseDetected) return;
    setTargetReady();
    await Future.delayed(const Duration(seconds: 1));
    if (state != DetectionState.targetReady) return;
    setWaitingForConfirmation();
  }

  void setPlantDetected() => state = DetectionState.plantDetected;
  void setLeafDetected() => state = DetectionState.leafDetected;
  void setDiseaseDetected() => state = DetectionState.diseaseDetected;
  void setTargetReady() => state = DetectionState.targetReady;
  void setWaitingForConfirmation() => state = DetectionState.waitingForConfirmation;

  void spray() async {
    if (state != DetectionState.waitingForConfirmation) return;
    state = DetectionState.spraying;
    await Future.delayed(const Duration(seconds: 2));
    if (state != DetectionState.spraying) return;
    setSprayCompleted();
  }

  void setSprayCompleted() => state = DetectionState.sprayCompleted;
  void setError() => state = DetectionState.error;
  void setEmergencyStopped() => state = DetectionState.error;

  void skip() {
    state = DetectionState.idle;
  }

  void reset() {
    state = DetectionState.idle;
  }
}

final detectionStateProvider = StateNotifierProvider<DetectionStateNotifier, DetectionState>((ref) {
  return DetectionStateNotifier();
});
