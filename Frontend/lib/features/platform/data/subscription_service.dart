import 'dart:convert';

import '../../../core/network/api_client.dart';

class SubscriptionSummary {
  SubscriptionSummary({
    required this.id,
    required this.subscriptionNumber,
    required this.status,
    required this.editionCode,
    required this.seatCount,
    required this.seatCountUsed,
    required this.versionNo,
    this.tenantId,
    this.tenantCode,
    this.billingCycle,
    this.endDate,
    this.startDate,
  });

  final String id;
  final String subscriptionNumber;
  final String status;
  final String editionCode;
  final int seatCount;
  final int seatCountUsed;
  final int versionNo;
  final String? tenantId;
  final String? tenantCode;
  final String? billingCycle;
  final String? endDate;
  final String? startDate;

  factory SubscriptionSummary.fromJson(Map<String, dynamic> json) {
    return SubscriptionSummary(
      id: json['id'] as String,
      subscriptionNumber: json['subscription_number'] as String,
      status: json['status'] as String,
      editionCode: json['edition_code'] as String,
      seatCount: json['seat_count'] as int,
      seatCountUsed: json['seat_count_used'] as int? ?? 0,
      versionNo: json['version_no'] as int,
      tenantId: json['tenant_id'] as String?,
      tenantCode: json['tenant_code'] as String?,
      billingCycle: json['billing_cycle'] as String?,
      endDate: json['end_date'] as String?,
      startDate: json['start_date'] as String?,
    );
  }
}

class SubscriptionHistoryRow {
  SubscriptionHistoryRow({
    required this.changeType,
    required this.changedOn,
    this.fromStatus,
    this.toStatus,
    this.reason,
  });

  final String changeType;
  final String changedOn;
  final String? fromStatus;
  final String? toStatus;
  final String? reason;

  factory SubscriptionHistoryRow.fromJson(Map<String, dynamic> json) {
    return SubscriptionHistoryRow(
      changeType: json['change_type'] as String,
      changedOn: json['changed_on'] as String,
      fromStatus: json['from_status'] as String?,
      toStatus: json['to_status'] as String?,
      reason: json['reason'] as String?,
    );
  }
}

class SubscriptionService {
  final _client = ApiClient();

  Future<List<SubscriptionSummary>> list({
    String? status,
    String? search,
  }) async {
    if (search != null && search.trim().isNotEmpty) {
      final resp = await _client.get(
        '/api/v1/platform/subscriptions/search',
        query: {'q': search.trim()},
      );
      if (resp.statusCode != 200) {
        throw Exception(
          _client.extractError(resp.body) ?? 'Search subscriptions failed',
        );
      }
      final items =
          (jsonDecode(resp.body) as Map<String, dynamic>)['items'] as List;
      return items
          .map((e) => SubscriptionSummary.fromJson(e as Map<String, dynamic>))
          .toList();
    }
    final query = <String, String>{};
    if (status != null && status.isNotEmpty) query['status'] = status;
    final resp =
        await _client.get('/api/v1/platform/subscriptions', query: query);
    if (resp.statusCode != 200) {
      throw Exception(
        _client.extractError(resp.body) ?? 'Failed to list subscriptions',
      );
    }
    final items =
        (jsonDecode(resp.body) as Map<String, dynamic>)['items'] as List;
    return items
        .map((e) => SubscriptionSummary.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<SubscriptionSummary> tenantCurrent() async {
    final resp = await _client.get('/api/v1/tenant/subscription');
    if (resp.statusCode != 200) {
      throw Exception(
        _client.extractError(resp.body) ?? 'Failed to load subscription',
      );
    }
    return SubscriptionSummary.fromJson(
      jsonDecode(resp.body) as Map<String, dynamic>,
    );
  }

  Future<String?> _resolveTenantId(String tenantCode) async {
    final resp = await _client.get(
      '/api/v1/platform/tenants/search',
      query: {'q': tenantCode.trim()},
    );
    if (resp.statusCode != 200) {
      throw Exception(
        _client.extractError(resp.body) ?? 'Tenant lookup failed',
      );
    }
    final items =
        (jsonDecode(resp.body) as Map<String, dynamic>)['items'] as List;
    for (final raw in items) {
      final m = raw as Map<String, dynamic>;
      if ((m['code'] as String).toLowerCase() == tenantCode.trim().toLowerCase()) {
        return m['id'] as String;
      }
    }
    return items.isEmpty ? null : (items.first as Map<String, dynamic>)['id'] as String;
  }

  Future<SubscriptionSummary> create({
    required String tenantCode,
    required String editionCode,
    required int seatCount,
    required String startDate,
    required String endDate,
    String billingCycle = 'MONTHLY',
    String status = 'ACTIVE',
  }) async {
    final tenantId = await _resolveTenantId(tenantCode);
    if (tenantId == null) {
      throw Exception('Tenant not found: $tenantCode');
    }
    final resp = await _client.post(
      '/api/v1/platform/subscriptions',
      body: {
        'tenant_id': tenantId,
        'edition_code': editionCode,
        'seat_count': seatCount,
        'billing_cycle': billingCycle,
        'start_date': startDate,
        'end_date': endDate,
        'status': status,
      },
    );
    if (resp.statusCode != 201) {
      throw Exception(
        _client.extractError(resp.body) ?? 'Create subscription failed',
      );
    }
    return SubscriptionSummary.fromJson(
      jsonDecode(resp.body) as Map<String, dynamic>,
    );
  }

  Future<SubscriptionSummary> update({
    required String id,
    required int versionNo,
    int? seatCount,
    String? endDate,
    String? billingCycle,
  }) async {
    final body = <String, dynamic>{'version_no': versionNo};
    if (seatCount != null) body['seat_count'] = seatCount;
    if (endDate != null) body['end_date'] = endDate;
    if (billingCycle != null) body['billing_cycle'] = billingCycle;
    final resp = await _client.put(
      '/api/v1/platform/subscriptions/$id',
      body: body,
    );
    if (resp.statusCode != 200) {
      throw Exception(_client.extractError(resp.body) ?? 'Update failed');
    }
    return SubscriptionSummary.fromJson(
      jsonDecode(resp.body) as Map<String, dynamic>,
    );
  }

  Future<List<SubscriptionHistoryRow>> history(String id) async {
    final resp = await _client.get('/api/v1/platform/subscriptions/$id/history');
    if (resp.statusCode != 200) {
      throw Exception(_client.extractError(resp.body) ?? 'History failed');
    }
    final items = jsonDecode(resp.body) as List;
    return items
        .map((e) => SubscriptionHistoryRow.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<SubscriptionSummary> activateTrial(String id, int versionNo) async {
    final resp = await _client.patch(
      '/api/v1/platform/subscriptions/$id',
      body: {'version_no': versionNo},
    );
    if (resp.statusCode != 200) {
      throw Exception(_client.extractError(resp.body) ?? 'Activate failed');
    }
    return SubscriptionSummary.fromJson(
      jsonDecode(resp.body) as Map<String, dynamic>,
    );
  }

  Future<SubscriptionSummary> renew(
    String id,
    int versionNo,
    String endDate,
  ) async {
    final resp = await _client.post(
      '/api/v1/platform/subscriptions/$id/renew',
      body: {'version_no': versionNo, 'end_date': endDate},
    );
    if (resp.statusCode != 200) {
      throw Exception(_client.extractError(resp.body) ?? 'Renew failed');
    }
    return SubscriptionSummary.fromJson(
      jsonDecode(resp.body) as Map<String, dynamic>,
    );
  }

  Future<SubscriptionSummary> upgrade(
    String id,
    int versionNo,
    String editionCode,
  ) async {
    final resp = await _client.post(
      '/api/v1/platform/subscriptions/$id/upgrade',
      body: {'version_no': versionNo, 'edition_code': editionCode},
    );
    if (resp.statusCode != 200) {
      throw Exception(_client.extractError(resp.body) ?? 'Upgrade failed');
    }
    return SubscriptionSummary.fromJson(
      jsonDecode(resp.body) as Map<String, dynamic>,
    );
  }
}
