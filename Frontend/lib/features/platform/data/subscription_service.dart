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
    this.tenantCode,
    this.billingCycle,
    this.endDate,
  });

  final String id;
  final String subscriptionNumber;
  final String status;
  final String editionCode;
  final int seatCount;
  final int seatCountUsed;
  final int versionNo;
  final String? tenantCode;
  final String? billingCycle;
  final String? endDate;

  factory SubscriptionSummary.fromJson(Map<String, dynamic> json) {
    return SubscriptionSummary(
      id: json['id'] as String,
      subscriptionNumber: json['subscription_number'] as String,
      status: json['status'] as String,
      editionCode: json['edition_code'] as String,
      seatCount: json['seat_count'] as int,
      seatCountUsed: json['seat_count_used'] as int? ?? 0,
      versionNo: json['version_no'] as int,
      tenantCode: json['tenant_code'] as String?,
      billingCycle: json['billing_cycle'] as String?,
      endDate: json['end_date'] as String?,
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
