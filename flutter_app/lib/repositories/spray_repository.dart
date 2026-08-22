import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_service.dart';
import '../core/config/api_config.dart';

abstract class SprayRepository {
  Future<void> sprayManual(String deviceId, double duration);
  Future<void> stopSpray(String deviceId);
  Future<void> emergencyStop();
  Future<void> resetEmergencyStop();
}

class SprayRepositoryImpl implements SprayRepository {
  final ApiService _api;

  SprayRepositoryImpl(this._api);

  void _ensureSuccess(dynamic response) {
    final data = response.data;
    if (data is Map && data['success'] == false) {
      final error = data['error'];
      final code = error is Map ? error['code'] : null;
      final message = error is Map ? error['message'] : null;
      final details = [code, message]
          .where((value) => value != null && value.toString().isNotEmpty)
          .join(': ');
      throw Exception(
        details.isEmpty ? 'Spray request failed' : 'Spray request failed: $details',
      );
    }
  }

  @override
  Future<void> sprayManual(String deviceId, double duration) async {
    final response = await _api.post('${ApiConfig.spray}/manual', data: {
      'device_id': deviceId,
      'duration_ms': (duration * 1000).toInt(),
      'command_id': DateTime.now().millisecondsSinceEpoch.toString(),
    });
    _ensureSuccess(response);
  }

  @override
  Future<void> stopSpray(String deviceId) async {
    final response = await _api.post('${ApiConfig.spray}/stop', data: {'device_id': deviceId});
    _ensureSuccess(response);
  }

  @override
  Future<void> emergencyStop() async {
    final response = await _api.post('${ApiConfig.spray}/emergency-stop');
    _ensureSuccess(response);
  }

  @override
  Future<void> resetEmergencyStop() async {
    final response = await _api.post('${ApiConfig.spray}/reset-emergency-stop');
    _ensureSuccess(response);
  }
}

final sprayRepositoryProvider = Provider<SprayRepository>((ref) {
  return SprayRepositoryImpl(ref.read(apiServiceProvider));
});
