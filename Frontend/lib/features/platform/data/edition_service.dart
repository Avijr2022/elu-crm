import 'dart:convert';

import '../../../core/network/api_client.dart';

class EditionSummary {
  EditionSummary({
    required this.id,
    required this.code,
    required this.name,
    required this.status,
    required this.versionNo,
    this.description,
    this.features = const [],
    this.limits = const [],
  });

  final String id;
  final String code;
  final String name;
  final String status;
  final int versionNo;
  final String? description;
  final List<Map<String, dynamic>> features;
  final List<Map<String, dynamic>> limits;

  factory EditionSummary.fromJson(Map<String, dynamic> json) {
    return EditionSummary(
      id: json['id'] as String,
      code: json['code'] as String,
      name: json['name'] as String,
      status: json['status'] as String,
      versionNo: json['version_no'] as int,
      description: json['description'] as String?,
      features: (json['features'] as List<dynamic>? ?? [])
          .cast<Map<String, dynamic>>(),
      limits:
          (json['limits'] as List<dynamic>? ?? []).cast<Map<String, dynamic>>(),
    );
  }
}

class EditionService {
  final ApiClient _client = ApiClient();

  Future<List<EditionSummary>> listEditions({String? status}) async {
    final query = <String, String>{
      if (status != null && status.isNotEmpty) 'status': status,
    };
    final resp = await _client.get('/api/v1/platform/editions', query: query);
    if (resp.statusCode != 200) {
      throw Exception(_client.extractError(resp.body) ?? 'Failed to list editions');
    }
    final body = jsonDecode(resp.body) as Map<String, dynamic>;
    final items = (body['items'] as List<dynamic>).cast<Map<String, dynamic>>();
    return items.map(EditionSummary.fromJson).toList();
  }

  Future<EditionSummary> tenantEdition() async {
    final resp = await _client.get('/api/v1/tenant/edition');
    if (resp.statusCode != 200) {
      throw Exception(_client.extractError(resp.body) ?? 'Failed to load edition');
    }
    return EditionSummary.fromJson(
      jsonDecode(resp.body) as Map<String, dynamic>,
    );
  }

  Future<EditionSummary> getEdition(String id) async {
    final resp = await _client.get('/api/v1/platform/editions/$id');
    if (resp.statusCode != 200) {
      throw Exception(_client.extractError(resp.body) ?? 'Failed to load edition');
    }
    return EditionSummary.fromJson(
      jsonDecode(resp.body) as Map<String, dynamic>,
    );
  }
}
