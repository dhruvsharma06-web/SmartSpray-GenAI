import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_service.dart';
import '../core/config/api_config.dart';

abstract class SprayRepository {
  Future<void> sprayAuto();
  Future<void> sprayManual(double servoAngle, double duration);
  Future<void> stopSpray();
}

class SprayRepositoryImpl implements SprayRepository {
  final ApiService _api;

  SprayRepositoryImpl(this._api);

  @override
  Future<void> sprayAuto() async {
    try {
      await _api.post('${ApiConfig.spray}/auto');
    } catch (e) {
      // Mock fallback
    }
  }

  @override
  Future<void> sprayManual(double servoAngle, double duration) async {
    try {
      await _api.post('${ApiConfig.spray}/manual', data: {
        'angle': servoAngle,
        'duration': duration,
      });
    } catch (e) {
      // Mock fallback
    }
  }

  @override
  Future<void> stopSpray() async {
    try {
      await _api.post('${ApiConfig.spray}/stop');
    } catch (e) {
      // Mock fallback
    }
  }
}

final sprayRepositoryProvider = Provider<SprayRepository>((ref) {
  return SprayRepositoryImpl(ref.read(apiServiceProvider));
});
