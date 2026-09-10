import 'dart:convert';

import '../../../core/network/api_client.dart';

class OrganizationSummary {
  OrganizationSummary({
    required this.id,
    required this.code,
    required this.name,
    required this.isRoot,
    required this.status,
    required this.versionNo,
    this.legalName,
    this.gstin,
    this.pan,
    this.fiscalYearStartMonth,
    this.defaultCurrencyCode,
    this.organizationType,
    this.parentOrganizationId,
    this.email,
    this.phone,
    this.website,
    this.addressId,
    this.level,
  });

  final String id;
  final String code;
  final String name;
  final String? legalName;
  final bool isRoot;
  final String status;
  final int versionNo;
  final String? gstin;
  final String? pan;
  final int? fiscalYearStartMonth;
  final String? defaultCurrencyCode;
  final String? organizationType;
  final String? parentOrganizationId;
  final String? email;
  final String? phone;
  final String? website;
  final String? addressId;
  final int? level;

  factory OrganizationSummary.fromJson(Map<String, dynamic> json) {
    return OrganizationSummary(
      id: json['id'] as String,
      code: json['code'] as String,
      name: json['name'] as String,
      legalName: json['legal_name'] as String?,
      isRoot: json['is_root'] as bool? ?? false,
      status: json['status'] as String,
      versionNo: json['version_no'] as int,
      gstin: json['gstin'] as String?,
      pan: json['pan'] as String?,
      fiscalYearStartMonth: json['fiscal_year_start_month'] as int?,
      defaultCurrencyCode: json['default_currency_code'] as String?,
      organizationType: json['organization_type'] as String?,
      parentOrganizationId: json['parent_organization_id'] as String?,
      email: json['email'] as String?,
      phone: json['phone'] as String?,
      website: json['website'] as String?,
      addressId: json['address_id'] as String?,
      level: json['level'] as int?,
    );
  }
}

class OrganizationHistoryItem {
  OrganizationHistoryItem({
    required this.id,
    required this.eventType,
    required this.eventCategory,
    required this.createdOn,
    this.actorEmail,
    this.payloadJson,
  });

  final String id;
  final String eventType;
  final String eventCategory;
  final String? actorEmail;
  final String? payloadJson;
  final String createdOn;

  factory OrganizationHistoryItem.fromJson(Map<String, dynamic> json) {
    return OrganizationHistoryItem(
      id: json['id'] as String,
      eventType: json['event_type'] as String,
      eventCategory: json['event_category'] as String,
      actorEmail: json['actor_email'] as String?,
      payloadJson: json['payload_json'] as String?,
      createdOn: json['created_on'] as String,
    );
  }
}

class OrganizationService {
  final _client = ApiClient();

  Future<List<OrganizationSummary>> list({String? search}) async {
    final resp = search != null && search.trim().isNotEmpty
        ? await _client.get(
            '/api/v1/org/organizations/search',
            query: {'q': search.trim()},
          )
        : await _client.get('/api/v1/org/organizations');
    if (resp.statusCode != 200) {
      throw Exception(_client.extractError(resp.body) ?? 'List organizations failed');
    }
    final items = (jsonDecode(resp.body) as Map<String, dynamic>)['items'] as List;
    return items
        .map((e) => OrganizationSummary.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<OrganizationSummary> get(String id) async {
    final resp = await _client.get('/api/v1/org/organizations/$id');
    if (resp.statusCode != 200) {
      throw Exception(_client.extractError(resp.body) ?? 'Get organization failed');
    }
    return OrganizationSummary.fromJson(
      jsonDecode(resp.body) as Map<String, dynamic>,
    );
  }

  Future<OrganizationSummary> getRoot() async {
    final resp = await _client.get('/api/v1/org/organizations/root');
    if (resp.statusCode != 200) {
      throw Exception(_client.extractError(resp.body) ?? 'Get root failed');
    }
    return OrganizationSummary.fromJson(
      jsonDecode(resp.body) as Map<String, dynamic>,
    );
  }

  Future<OrganizationSummary> create({
    required String code,
    required String name,
    required String parentOrganizationId,
    String organizationType = 'Branch',
    String? legalName,
    String? gstin,
    String? pan,
  }) async {
    final body = <String, dynamic>{
      'code': code,
      'name': name,
      'parent_organization_id': parentOrganizationId,
      'organization_type': organizationType,
    };
    if (legalName != null && legalName.isNotEmpty) body['legal_name'] = legalName;
    if (gstin != null && gstin.isNotEmpty) body['gstin'] = gstin;
    if (pan != null && pan.isNotEmpty) body['pan'] = pan;
    final resp = await _client.post('/api/v1/org/organizations', body: body);
    if (resp.statusCode != 201) {
      throw Exception(_client.extractError(resp.body) ?? 'Create organization failed');
    }
    return OrganizationSummary.fromJson(
      jsonDecode(resp.body) as Map<String, dynamic>,
    );
  }

  Future<OrganizationSummary> update({
    required String id,
    required int versionNo,
    String? name,
    String? legalName,
    String? gstin,
    String? pan,
    int? fiscalYearStartMonth,
  }) async {
    final body = <String, dynamic>{'version_no': versionNo};
    if (name != null) body['name'] = name;
    if (legalName != null) body['legal_name'] = legalName;
    if (gstin != null) body['gstin'] = gstin;
    if (pan != null) body['pan'] = pan;
    if (fiscalYearStartMonth != null) {
      body['fiscal_year_start_month'] = fiscalYearStartMonth;
    }
    final resp = await _client.patch(
      '/api/v1/org/organizations/$id',
      body: body,
    );
    if (resp.statusCode != 200) {
      throw Exception(_client.extractError(resp.body) ?? 'Update organization failed');
    }
    return OrganizationSummary.fromJson(
      jsonDecode(resp.body) as Map<String, dynamic>,
    );
  }

  Future<Map<String, dynamic>> hierarchy(String id) async {
    final resp = await _client.get('/api/v1/org/organizations/$id/hierarchy');
    if (resp.statusCode != 200) {
      throw Exception(_client.extractError(resp.body) ?? 'Hierarchy failed');
    }
    return jsonDecode(resp.body) as Map<String, dynamic>;
  }

  Future<List<OrganizationHistoryItem>> history(String id) async {
    final resp = await _client.get('/api/v1/org/organizations/$id/history');
    if (resp.statusCode != 200) {
      throw Exception(_client.extractError(resp.body) ?? 'History failed');
    }
    final items = (jsonDecode(resp.body) as Map<String, dynamic>)['items'] as List;
    return items
        .map((e) => OrganizationHistoryItem.fromJson(e as Map<String, dynamic>))
        .toList();
  }
}
