import 'package:flutter_riverpod/flutter_riverpod.dart';

class ControlState {
  final double servoAngle;
  final double sprayDuration;
  final bool isSpraying;
  final bool isEmergencyStopped;

  const ControlState({
    this.servoAngle = 90.0,
    this.sprayDuration = 1.0,
    this.isSpraying = false,
    this.isEmergencyStopped = false,
  });

  ControlState copyWith({
    double? servoAngle,
    double? sprayDuration,
    bool? isSpraying,
    bool? isEmergencyStopped,
  }) {
    return ControlState(
      servoAngle: servoAngle ?? this.servoAngle,
      sprayDuration: sprayDuration ?? this.sprayDuration,
      isSpraying: isSpraying ?? this.isSpraying,
      isEmergencyStopped: isEmergencyStopped ?? this.isEmergencyStopped,
    );
  }
}

class ControlStateNotifier extends StateNotifier<ControlState> {
  ControlStateNotifier() : super(const ControlState());

  void setServoAngle(double angle) {
    if (state.isEmergencyStopped || state.isSpraying) return;
    state = state.copyWith(servoAngle: angle);
  }

  void setSprayDuration(double duration) {
    if (state.isEmergencyStopped || state.isSpraying) return;
    state = state.copyWith(sprayDuration: duration);
  }

  void startSpray() async {
    if (state.isEmergencyStopped || state.isSpraying) return;
    state = state.copyWith(isSpraying: true);
    
    // Simulate spray duration
    await Future.delayed(Duration(milliseconds: (state.sprayDuration * 1000).toInt()));
    
    if (state.isSpraying) {
      state = state.copyWith(isSpraying: false);
    }
  }

  void stopSpray() {
    state = state.copyWith(isSpraying: false);
  }

  void emergencyStop() {
    state = state.copyWith(isSpraying: false, isEmergencyStopped: true);
  }

  void resetEmergencyStop() {
    state = state.copyWith(isEmergencyStopped: false);
  }
}

final controlStateProvider = StateNotifierProvider<ControlStateNotifier, ControlState>((ref) {
  return ControlStateNotifier();
});
