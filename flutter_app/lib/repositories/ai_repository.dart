import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_service.dart';
import '../core/config/api_config.dart';

abstract class AiRepository {
  Future<Map<String, dynamic>> getAiStatus();
  Future<Map<String, dynamic>> detect();
}

class AiRepositoryImpl implements AiRepository {
  final ApiService _api;

  AiRepositoryImpl(this._api);

  @override
  Future<Map<String, dynamic>> getAiStatus() async {
    final response = await _api.get('${ApiConfig.ai}/status');
    return response.data;
  }

  @override
  Future<Map<String, dynamic>> detect() async {
    final response = await _api.post('${ApiConfig.ai}/detect');
    return response.data;
  }
}

final aiRepositoryProvider = Provider<AiRepository>((ref) {
  return AiRepositoryImpl(ref.read(apiServiceProvider));
});
