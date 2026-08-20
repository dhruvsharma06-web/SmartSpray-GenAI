import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_app/features/detection/detection_provider.dart';

void main() {
  group('DetectionStateNotifier', () {
    test('initial state is idle', () {
      final notifier = DetectionStateNotifier();
      expect(notifier.state, DetectionState.idle);
    });

    test('state transitions through scan flow correctly', () {
      final notifier = DetectionStateNotifier();
      
      notifier.startScan();
      expect(notifier.state, DetectionState.scanning);
      
      notifier.setPlantDetected();
      expect(notifier.state, DetectionState.plantDetected);
      
      notifier.setLeafDetected();
      expect(notifier.state, DetectionState.leafDetected);
      
      notifier.setDiseaseDetected();
      expect(notifier.state, DetectionState.diseaseDetected);
      
      notifier.setTargetReady();
      expect(notifier.state, DetectionState.targetReady);
      
      notifier.setWaitingForConfirmation();
      expect(notifier.state, DetectionState.waitingForConfirmation);
      
      notifier.spray();
      expect(notifier.state, DetectionState.spraying);
      
      notifier.setSprayCompleted();
      expect(notifier.state, DetectionState.sprayCompleted);
    });
  });
}
