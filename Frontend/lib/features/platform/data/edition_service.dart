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

class EditionVersionRow {
  EditionVersionRow({
    required this.versionNo,
    this.changeSummary,
    required this.createdOn,
  });

  final int versionNo;
  final String? changeSummary;
  final String createdOn;

  factory EditionVersionRow.fromJson(Map<String, dynamic> json) {
    return EditionVersionRow(
      versionNo: json['version_no'] as int,
      changeSummary: json['change_summary'] as String?,
      createdOn: json['created_on'] as String,
    );
  }
}

class EditionService {
  final ApiClient _client = ApiClient();

  Future<List<EditionSummary>> listEditions({
    String? status,
    String? search,
  }) async {
    if (search != null && search.trim().isNotEmpty) {
      final resp = await _client.get(
        '/api/v1/platform/editions/search',
        query: {'q': search.trim()},
      );
      if (resp.statusCode != 200) {
        throw Exception(
          _client.extractError(resp.body) ?? 'Search editions failed',
        );
      }
      final body = jsonDecode(resp.body) as Map<String, dynamic>;
      final items =
          (body['items'] as List<dynamic>).cast<Map<String, dynamic>>();
      return items.map(EditionSummary.fromJson).toList();
    }

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

  Future<EditionSummary> createDraft({
    required String code,
    required String name,
    String? description,
  }) async {
    final resp = await _client.post(
      '/api/v1/platform/editions',
      body: {
        'code': code,
        'name': name,
        'description': description,
        'features': [
          {'feature_code': 'CRM_LEAD', 'is_enabled': true, 'is_visible': true},
        ],
        'limits': [
          {
            'limit_code': 'MAX_USERS',
            'limit_name': 'Maximum users',
            'limit_value': '5',
            'limit_unit': 'users',
          },
          {
            'limit_code': 'MAX_STORAGE_GB',
            'limit_name': 'Storage',
            'limit_value': '5',
            'limit_unit': 'GB',
          },
          {
            'limit_code': 'MAX_ROLES',
            'limit_name': 'Roles',
            'limit_value': '5',
            'limit_unit': 'roles',
          },
        ],
      },
    );
    if (resp.statusCode != 201) {
      throw Exception(_client.extractError(resp.body) ?? 'Create failed');
    }
    return EditionSummary.fromJson(
      jsonDecode(resp.body) as Map<String, dynamic>,
    );
  }

  Future<EditionSummary> updateDraft({
    required String id,
    required int versionNo,
    required String name,
    String? description,
  }) async {
    final resp = await _client.put(
      '/api/v1/platform/editions/$id',
      body: {
        'name': name,
        'description': description,
        'version_no': versionNo,
      },
    );
    if (resp.statusCode != 200) {
      throw Exception(_client.extractError(resp.body) ?? 'Update failed');
    }
    return EditionSummary.fromJson(
      jsonDecode(resp.body) as Map<String, dynamic>,
    );
  }

  Future<EditionSummary> publish(String id, int versionNo) async {
    final resp = await _client.post(
      '/api/v1/platform/editions/$id/publish',
      body: {'version_no': versionNo},
    );
    if (resp.statusCode != 200) {
      throw Exception(_client.extractError(resp.body) ?? 'Publish failed');
    }
    return EditionSummary.fromJson(
      jsonDecode(resp.body) as Map<String, dynamic>,
    );
  }

  Future<EditionSummary> deprecate(
    String id,
    int versionNo,
    String reason,
  ) async {
    final resp = await _client.post(
      '/api/v1/platform/editions/$id/deprecate',
      body: {'version_no': versionNo, 'reason': reason},
    );
    if (resp.statusCode != 200) {
      throw Exception(_client.extractError(resp.body) ?? 'Deprecate failed');
    }
    return EditionSummary.fromJson(
      jsonDecode(resp.body) as Map<String, dynamic>,
    );
  }

  Future<List<EditionVersionRow>> history(String id) async {
    final resp = await _client.get('/api/v1/platform/editions/$id/history');
    if (resp.statusCode != 200) {
      throw Exception(_client.extractError(resp.body) ?? 'History failed');
    }
    final list = (jsonDecode(resp.body) as List<dynamic>)
        .cast<Map<String, dynamic>>();
    return list.map(EditionVersionRow.fromJson).toList();
  }
}
