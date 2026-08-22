import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../repositories/spray_repository.dart';


class ControlState {
  final double sprayDuration;
  final bool isSpraying;
  final bool isEmergencyStopped;
  final String? errorMessage;

  const ControlState({
    this.sprayDuration = 1.0,
    this.isSpraying = false,
    this.isEmergencyStopped = false,
    this.errorMessage,
  });

  ControlState copyWith({
    double? sprayDuration,
    bool? isSpraying,
    bool? isEmergencyStopped,
    String? errorMessage,
  }) {
    return ControlState(
      sprayDuration: sprayDuration ?? this.sprayDuration,
      isSpraying: isSpraying ?? this.isSpraying,
      isEmergencyStopped: isEmergencyStopped ?? this.isEmergencyStopped,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }
}

class ControlStateNotifier extends Notifier<ControlState> {
  @override
  ControlState build() => const ControlState();


  void setSprayDuration(double duration) {
    if (state.isEmergencyStopped || state.isSpraying) return;
    state = state.copyWith(sprayDuration: duration);
  }

  void startSpray() async {
    if (state.isEmergencyStopped || state.isSpraying) return;
    state = ControlState(
      sprayDuration: state.sprayDuration,
      isSpraying: true,
      isEmergencyStopped: state.isEmergencyStopped,
    );
    try {
      await ref.read(sprayRepositoryProvider).sprayManual('device-001', state.sprayDuration);
      await Future.delayed(Duration(milliseconds: (state.sprayDuration * 1000).toInt()));
    } catch (error) {
      state = state.copyWith(isSpraying: false, errorMessage: error.toString());
      return;
    }

    if (state.isSpraying) {
      state = state.copyWith(isSpraying: false);
    }
  }

  void stopSpray() async {
    state = state.copyWith(isSpraying: false);
    try {
      await ref.read(sprayRepositoryProvider).stopSpray('device-001');
    } catch (error) {
      state = state.copyWith(errorMessage: error.toString());
    }
  }

  void emergencyStop() async {
    state = state.copyWith(isSpraying: false, isEmergencyStopped: true);
    try {
      await ref.read(sprayRepositoryProvider).emergencyStop();
    } catch (error) {
      state = state.copyWith(errorMessage: error.toString());
    }
  }

  void resetEmergencyStop() async {
    state = state.copyWith(isEmergencyStopped: false);
    try {
      await ref.read(sprayRepositoryProvider).resetEmergencyStop();
    } catch (error) {
      state = state.copyWith(errorMessage: error.toString());
    }
  }


}

final controlStateProvider = NotifierProvider<ControlStateNotifier, ControlState>(() {
  return ControlStateNotifier();
});
