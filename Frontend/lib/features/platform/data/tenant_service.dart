import 'dart:convert';

import '../../../core/network/api_client.dart';

class TenantSummary {
  TenantSummary({
    required this.id,
    required this.code,
    required this.legalName,
    required this.status,
    required this.editionCode,
    required this.versionNo,
    this.tradeName,
    this.email,
    this.mobile,
  });

  final String id;
  final String code;
  final String legalName;
  final String? tradeName;
  final String status;
  final String editionCode;
  final int versionNo;
  final String? email;
  final String? mobile;

  factory TenantSummary.fromJson(Map<String, dynamic> json) {
    return TenantSummary(
      id: json['id'] as String,
      code: json['code'] as String,
      legalName: json['legal_name'] as String,
      tradeName: json['trade_name'] as String?,
      status: json['status'] as String,
      editionCode: json['edition_code'] as String,
      versionNo: json['version_no'] as int,
      email: json['email'] as String?,
      mobile: json['mobile'] as String?,
    );
  }
}

class TenantService {
  final _client = ApiClient();

  Future<List<TenantSummary>> listTenants({
    String? status,
    String? search,
  }) async {
    if (search != null && search.trim().isNotEmpty) {
      final resp = await _client.get(
        '/api/v1/platform/tenants/search',
        query: {'q': search.trim()},
      );
      if (resp.statusCode != 200) {
        throw Exception(
          _client.extractError(resp.body) ?? 'Search tenants failed',
        );
      }
      final items =
          (jsonDecode(resp.body) as Map<String, dynamic>)['items'] as List;
      return items
          .map((e) => TenantSummary.fromJson(e as Map<String, dynamic>))
          .toList();
    }
    final query = <String, String>{};
    if (status != null && status.isNotEmpty) query['status'] = status;
    final resp = await _client.get('/api/v1/platform/tenants', query: query);
    if (resp.statusCode != 200) {
      throw Exception(
        _client.extractError(resp.body) ?? 'Failed to list tenants',
      );
    }
    final items =
        (jsonDecode(resp.body) as Map<String, dynamic>)['items'] as List;
    return items
        .map((e) => TenantSummary.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<TenantSummary> getTenant(String id) async {
    final resp = await _client.get('/api/v1/platform/tenants/$id');
    if (resp.statusCode != 200) {
      throw Exception(
        _client.extractError(resp.body) ?? 'Failed to load tenant',
      );
    }
    return TenantSummary.fromJson(
      jsonDecode(resp.body) as Map<String, dynamic>,
    );
  }

  Future<TenantSummary> register({
    required String code,
    required String legalName,
    String? tradeName,
    required String editionCode,
    required String email,
    required String mobile,
    required String contactName,
    required String contactEmail,
    required String addressLine1,
    required String city,
    String country = 'India',
  }) async {
    final resp = await _client.post(
      '/api/v1/platform/tenants',
      body: {
        'code': code,
        'legal_name': legalName,
        if (tradeName != null && tradeName.isNotEmpty) 'trade_name': tradeName,
        'edition_code': editionCode,
        'email': email,
        'mobile': mobile,
        'primary_contact': {
          'contact_type': 'PRIMARY',
          'name': contactName,
          'email': contactEmail,
          'is_primary': true,
        },
        'registered_address': {
          'address_type': 'REGISTERED',
          'line1': addressLine1,
          'city': city,
          'country': country,
        },
      },
    );
    if (resp.statusCode != 201) {
      throw Exception(
        _client.extractError(resp.body) ?? 'Register tenant failed',
      );
    }
    return TenantSummary.fromJson(
      jsonDecode(resp.body) as Map<String, dynamic>,
    );
  }

  Future<TenantSummary> approve(String id, int versionNo) async {
    final resp = await _client.post(
      '/api/v1/platform/tenants/$id/approve',
      body: {'version_no': versionNo},
    );
    if (resp.statusCode != 200) {
      throw Exception(_client.extractError(resp.body) ?? 'Approve failed');
    }
    return TenantSummary.fromJson(
      jsonDecode(resp.body) as Map<String, dynamic>,
    );
  }

  Future<TenantSummary> suspend(String id, int versionNo, String reason) async {
    final resp = await _client.post(
      '/api/v1/platform/tenants/$id/suspend',
      body: {'version_no': versionNo, 'reason': reason},
    );
    if (resp.statusCode != 200) {
      throw Exception(_client.extractError(resp.body) ?? 'Suspend failed');
    }
    return TenantSummary.fromJson(
      jsonDecode(resp.body) as Map<String, dynamic>,
    );
  }

  Future<TenantSummary> reactivate(String id, int versionNo) async {
    final resp = await _client.post(
      '/api/v1/platform/tenants/$id/reactivate',
      body: {'version_no': versionNo},
    );
    if (resp.statusCode != 200) {
      throw Exception(_client.extractError(resp.body) ?? 'Reactivate failed');
    }
    return TenantSummary.fromJson(
      jsonDecode(resp.body) as Map<String, dynamic>,
    );
  }
}
