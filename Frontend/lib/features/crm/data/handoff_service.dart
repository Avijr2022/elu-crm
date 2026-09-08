import 'dart:convert';

import '../../../core/network/api_client.dart';

class HandoffService {
  HandoffService({ApiClient? client}) : _client = client ?? ApiClient();

  final ApiClient _client;

  Future<String?> requestFromOpportunity(String opportunityId) async {
    final response = await _client.post(
      '/api/v1/prj/handoffs/from-opportunity/$opportunityId',
    );
    if (response.statusCode == 201) {
      final body = jsonDecode(response.body) as Map<String, dynamic>;
      final wo = body['wo_number'] as String?;
      return wo != null ? 'Work order $wo queued' : body['message'] as String?;
    }
    return null;
  }
}
