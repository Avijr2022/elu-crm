import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

class L2cDemoSession {
  const L2cDemoSession({
    this.leadId,
    this.opportunityId,
    this.customerId,
    this.quotationId,
    this.salesOrderId,
    this.completedSteps = const {},
    required this.hasOpportunityEdition,
    this.hasSalQuote = false,
  });

  final String? leadId;
  final String? opportunityId;
  final String? customerId;
  final String? quotationId;
  final String? salesOrderId;
  final Set<int> completedSteps;
  final bool hasOpportunityEdition;
  final bool hasSalQuote;
}

abstract final class L2cDemoStorage {
  static String _key(String tenantCode) => 'l2c_demo_session_$tenantCode';

  static Future<L2cDemoSession?> load(String tenantCode) async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_key(tenantCode));
    if (raw == null) return null;
    try {
      final data = jsonDecode(raw) as Map<String, dynamic>;
      final steps = (data['completed_steps'] as List<dynamic>? ?? [])
          .map((e) => e as int)
          .toSet();
      return L2cDemoSession(
        leadId: data['lead_id'] as String?,
        opportunityId: data['opportunity_id'] as String?,
        customerId: data['customer_id'] as String?,
        quotationId: data['quotation_id'] as String?,
        salesOrderId: data['sales_order_id'] as String?,
        completedSteps: steps,
        hasOpportunityEdition: data['has_opportunity_edition'] as bool? ?? true,
        hasSalQuote: data['has_sal_quote'] as bool? ?? false,
      );
    } catch (_) {
      return null;
    }
  }

  static Future<void> save({
    required String tenantCode,
    String? leadId,
    String? opportunityId,
    String? customerId,
    String? quotationId,
    String? salesOrderId,
    required Set<int> completedSteps,
    required bool hasOpportunityEdition,
    bool hasSalQuote = false,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(
      _key(tenantCode),
      jsonEncode({
        'lead_id': leadId,
        'opportunity_id': opportunityId,
        'customer_id': customerId,
        'quotation_id': quotationId,
        'sales_order_id': salesOrderId,
        'completed_steps': completedSteps.toList()..sort(),
        'has_opportunity_edition': hasOpportunityEdition,
        'has_sal_quote': hasSalQuote,
      }),
    );
  }

  static Future<void> clear(String tenantCode) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_key(tenantCode));
  }
}
