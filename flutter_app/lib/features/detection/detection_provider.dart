import 'dart:io';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../repositories/ai_repository.dart';
import '../../repositories/spray_repository.dart';

enum DetectionStatus { idle, scanning, resultReady, spraying, error, offline }

enum GenAiStatus { idle, loading, ready, unavailable }

class DetectionState {
  final DetectionStatus status;
  final Map<String, dynamic>? aiResult;
  final GenAiStatus genAiStatus;
  final Map<String, dynamic>? genAiResult;
  final String? errorMessage;

  const DetectionState({
    this.status = DetectionStatus.idle,
    this.aiResult,
    this.genAiStatus = GenAiStatus.idle,
    this.genAiResult,
    this.errorMessage,
  });

  DetectionState copyWith({
    DetectionStatus? status,
    Map<String, dynamic>? aiResult,
    GenAiStatus? genAiStatus,
    Map<String, dynamic>? genAiResult,
    String? errorMessage,
  }) {
    return DetectionState(
      status: status ?? this.status,
      aiResult: aiResult ?? this.aiResult,
      genAiStatus: genAiStatus ?? this.genAiStatus,
      genAiResult: genAiResult ?? this.genAiResult,
      errorMessage: errorMessage,
    );
  }
}

class DetectionStateNotifier extends Notifier<DetectionState> {
  @override
  DetectionState build() => const DetectionState();

  void startScan({File? imageFile}) async {
    state = const DetectionState(status: DetectionStatus.scanning);
    try {
      final result =
          await ref.read(aiRepositoryProvider).detect(imageFile: imageFile);
      if (result['success'] != true) {
        state = state.copyWith(
          status: DetectionStatus.error,
          errorMessage: 'Detection failed: ${result['error']}',
        );
        return;
      }

      state = DetectionState(
        status: DetectionStatus.resultReady,
        aiResult: result,
        genAiStatus:
            imageFile == null ? GenAiStatus.unavailable : GenAiStatus.loading,
      );
      if (imageFile != null) await _requestGenAiAnalysis(imageFile);
    } catch (_) {
      state = state.copyWith(
        status: DetectionStatus.offline,
        errorMessage: 'Backend API offline',
      );
    }
  }

  Future<void> _requestGenAiAnalysis(File imageFile) async {
    try {
      final result = await ref.read(aiRepositoryProvider).assist(imageFile);
      if (result['success'] == true && result['data'] is Map) {
        state = state.copyWith(
          genAiStatus: GenAiStatus.ready,
          genAiResult: Map<String, dynamic>.from(result['data'] as Map),
        );
      } else {
        state = state.copyWith(genAiStatus: GenAiStatus.unavailable);
      }
    } catch (_) {
      // This advisory request never alters detection or spray availability.
      state = state.copyWith(genAiStatus: GenAiStatus.unavailable);
    }
  }

  void spray() async {
    if (state.status != DetectionStatus.resultReady) return;

    // Only this user-initiated path may access the existing spray repository.
    final decision = state.aiResult?['decision'];
    if (decision == null || decision['auto_permitted'] == false) {
      state = state.copyWith(
        status: DetectionStatus.error,
        errorMessage: 'Spray not permitted by AI constraints.',
      );
      return;
    }

    state = state.copyWith(status: DetectionStatus.spraying);
    try {
      await ref.read(sprayRepositoryProvider).sprayManual('device-001', 1.0);
      await Future.delayed(const Duration(seconds: 2));
      state = const DetectionState(status: DetectionStatus.idle);
    } catch (_) {
      state = state.copyWith(
        status: DetectionStatus.error,
        errorMessage: 'Spray command failed.',
      );
    }
  }

  void skip() => state = const DetectionState(status: DetectionStatus.idle);

  void reset() => state = const DetectionState(status: DetectionStatus.idle);
}

final detectionStateProvider =
    NotifierProvider<DetectionStateNotifier, DetectionState>(() {
  return DetectionStateNotifier();
});
