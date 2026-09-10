import 'package:flutter/material.dart';

import '../data/activity_service.dart';
import '../data/customer_service.dart';
import '../data/lead_model.dart';
import '../data/lead_service.dart';
import '../data/opportunity_model.dart';
import '../data/opportunity_service.dart';
import '../data/quotation_service.dart';
import '../data/sales_order_service.dart';
import 'l2c_demo_storage.dart';

typedef L2cStep = (String title, String description, String hint);

/// Tracks UAT progress for the CRM portion of Lead-to-Cash (TC-L2C-CRM-01).
class L2cDemoController extends ChangeNotifier {
  L2cDemoController({
    LeadService? leads,
    OpportunityService? opportunities,
    CustomerService? customers,
    ActivityService? activities,
    QuotationService? quotations,
    SalesOrderService? salesOrders,
    this.hasOpportunityEdition = true,
    this.hasSalQuote = false,
  })  : _leads = leads ?? LeadService(),
        _opportunities = opportunities ?? OpportunityService(),
        _customers = customers ?? CustomerService(),
        _activities = activities ?? ActivityService(),
        _quotations = quotations ?? QuotationService(),
        _salesOrders = salesOrders ?? SalesOrderService();

  final LeadService _leads;
  final OpportunityService _opportunities;
  final CustomerService _customers;
  final ActivityService _activities;
  final QuotationService _quotations;
  final SalesOrderService _salesOrders;

  /// Professional tenants convert to opportunity; Community converts to customer only.
  final bool hasOpportunityEdition;
  final bool hasSalQuote;

  String? _tenantCode;
  String? leadId;
  String? opportunityId;
  String? customerId;
  String? quotationId;
  String? salesOrderId;
  final Set<int> completedSteps = {};
  bool syncing = false;
  String? error;

  static const professionalSteps = <L2cStep>[
    (
      'Create lead',
      'Capture a new prospect with company and estimated value.',
      'Use Add Lead and save a new record.',
    ),
    (
      'Qualify lead',
      'Move the lead to QUALIFIED status after initial discovery.',
      'Open the lead and tap Qualify.',
    ),
    (
      'Convert to opportunity',
      'Convert the qualified lead into an open opportunity.',
      'On lead detail, tap Convert.',
    ),
    (
      'Log call activity',
      'Record a discovery call with outcome Interested.',
      'On opportunity detail, log a CALL with outcome.',
    ),
    (
      'Close won',
      'Close the opportunity as won — customer is auto-created.',
      'Use Close Won on opportunity detail.',
    ),
    (
      'Activate customer',
      'Add primary contact + registered address, then activate.',
      'On customer detail, add contact/address and set ACTIVE.',
    ),
  ];

  static const communitySteps = <L2cStep>[
    (
      'Create lead',
      'Capture a new prospect with company and estimated value.',
      'Use Add Lead and save a new record.',
    ),
    (
      'Qualify lead',
      'Move the lead to QUALIFIED status after initial discovery.',
      'Open the lead and tap Qualify.',
    ),
    (
      'Convert to customer',
      'Convert the qualified lead directly to a customer account.',
      'On lead detail, tap Convert.',
    ),
    (
      'Log call activity',
      'Record a discovery call with outcome Interested.',
      'On customer detail, log a CALL with outcome.',
    ),
    (
      'Activate customer',
      'Add registered address if needed, then activate.',
      'On customer detail, add address and set ACTIVE.',
    ),
  ];

  static const salSteps = <L2cStep>[
    (
      'Accept quotation',
      'Mark customer acceptance on the opportunity quotation.',
      'On quotation detail, tap Accept when status is SENT.',
    ),
    (
      'Convert to sales order',
      'Convert an accepted quotation into a draft sales order.',
      'On quotation detail, tap Convert to sales order.',
    ),
    (
      'Confirm sales order',
      'Confirm the sales order to link project work orders.',
      'On sales order detail, tap Confirm order.',
    ),
  ];

  List<L2cStep> get steps {
    if (!hasOpportunityEdition) return communitySteps;
    if (!hasSalQuote) return professionalSteps;
    return [...professionalSteps, ...salSteps];
  }

  void bindTenant(String? tenantCode) {
    _tenantCode = tenantCode?.trim().isEmpty == true ? null : tenantCode?.trim();
  }

  Future<void> loadSession(String tenantCode) async {
    bindTenant(tenantCode);
    final session = await L2cDemoStorage.load(tenantCode);
    if (session == null ||
        session.hasOpportunityEdition != hasOpportunityEdition ||
        session.hasSalQuote != hasSalQuote) {
      return;
    }
    leadId = session.leadId;
    opportunityId = hasOpportunityEdition ? session.opportunityId : null;
    customerId = session.customerId;
    quotationId = hasSalQuote ? session.quotationId : null;
    salesOrderId = hasSalQuote ? session.salesOrderId : null;
    completedSteps
      ..clear()
      ..addAll(session.completedSteps);
    notifyListeners();
  }

  void setLeadId(String? value) {
    leadId = value?.trim().isEmpty == true ? null : value?.trim();
    _persist();
    notifyListeners();
  }

  void setOpportunityId(String? value) {
    opportunityId = value?.trim().isEmpty == true ? null : value?.trim();
    _persist();
    notifyListeners();
  }

  void setCustomerId(String? value) {
    customerId = value?.trim().isEmpty == true ? null : value?.trim();
    _persist();
    notifyListeners();
  }

  void setQuotationId(String? value) {
    quotationId = value?.trim().isEmpty == true ? null : value?.trim();
    _persist();
    notifyListeners();
  }

  void setSalesOrderId(String? value) {
    salesOrderId = value?.trim().isEmpty == true ? null : value?.trim();
    _persist();
    notifyListeners();
  }

  void toggleStep(int index) {
    if (completedSteps.contains(index)) {
      completedSteps.remove(index);
    } else {
      completedSteps.add(index);
    }
    _persist();
    notifyListeners();
  }

  Future<void> reset() async {
    leadId = null;
    opportunityId = null;
    customerId = null;
    quotationId = null;
    salesOrderId = null;
    completedSteps.clear();
    error = null;
    if (_tenantCode != null) {
      await L2cDemoStorage.clear(_tenantCode!);
    }
    notifyListeners();
  }

  void _persist() {
    final tenant = _tenantCode;
    if (tenant == null) return;
    L2cDemoStorage.save(
      tenantCode: tenant,
      leadId: leadId,
      opportunityId: opportunityId,
      customerId: customerId,
      quotationId: quotationId,
      salesOrderId: salesOrderId,
      completedSteps: completedSteps,
      hasOpportunityEdition: hasOpportunityEdition,
      hasSalQuote: hasSalQuote,
    );
  }

  Future<void> syncLatest() async {
    syncing = true;
    error = null;
    notifyListeners();
    try {
      await _resolveIds();
    } catch (e) {
      error = e.toString().replaceFirst('Exception: ', '');
    } finally {
      syncing = false;
      _persist();
      notifyListeners();
    }
  }

  /// Polls CRM APIs and auto-ticks steps when TC-L2C-CRM-01 criteria are met.
  Future<void> detectProgress() async {
    syncing = true;
    error = null;
    notifyListeners();
    try {
      await _resolveIds();
      final detected = hasOpportunityEdition
          ? await _detectProfessional()
          : await _detectCommunity();
      completedSteps
        ..clear()
        ..addAll(detected);
    } catch (e) {
      error = e.toString().replaceFirst('Exception: ', '');
    } finally {
      syncing = false;
      _persist();
      notifyListeners();
    }
  }

  Future<Set<int>> _detectProfessional() async {
    final detected = <int>{};
    Lead? lead;
    if (leadId != null) {
      try {
        lead = await _leads.getById(leadId!);
      } catch (_) {
        lead = null;
      }
    }
    if (lead != null) {
      detected.add(0);
      if (lead.status == 'QUALIFIED' || lead.status == 'CONVERTED') {
        detected.add(1);
      }
      if (lead.status == 'CONVERTED') {
        detected.add(2);
      }
    }

    Opportunity? opp;
    if (opportunityId != null) {
      try {
        opp = await _opportunities.getById(opportunityId!);
      } catch (_) {
        opp = null;
      }
    }
    if (opp == null && leadId != null) {
      final opps = await _opportunities.list(pageSize: 50);
      for (final o in opps.items) {
        if (o.sourceLeadId == leadId) {
          opp = o;
          opportunityId = o.opportunityId;
          break;
        }
      }
    }
    if (opp != null) {
      if (lead?.status == 'CONVERTED' || opp.sourceLeadId == leadId) {
        detected.add(2);
      }
      final activities = await _activities.timeline(
        entityType: 'OPPORTUNITY',
        entityId: opp.opportunityId,
      );
      if (activities.any(
        (a) => a.activityTypeCode == 'CALL' && a.outcomeCode != null,
      )) {
        detected.add(3);
      }
      if (opp.status == 'CLOSED_WON') {
        detected.add(4);
        customerId = opp.customerId ?? customerId;
      }
    }

    if (customerId != null) {
      try {
        final cust = await _customers.getById(customerId!);
        final hasContact = cust.contacts.any((c) => c.isPrimary);
        final hasAddress = cust.addresses.isNotEmpty;
        if (cust.status == 'ACTIVE' && hasContact && hasAddress) {
          detected.add(5);
        }
      } catch (_) {}
    }

    if (hasSalQuote && opp != null) {
      final quotes = await _quotations.list(page: 1);
      Quotation? quote;
      for (final q in quotes.items) {
        if (q.opportunityId == opp.opportunityId) {
          quote = q;
          quotationId = q.quotationId;
          break;
        }
      }
      if (quote != null) {
        if (quote.status == 'ACCEPTED' || quote.salesOrderId != null) {
          detected.add(professionalSteps.length);
        }
        if (quote.salesOrderId != null) {
          salesOrderId = quote.salesOrderId;
          detected.add(professionalSteps.length + 1);
          try {
            final so = await _salesOrders.getById(quote.salesOrderId!);
            salesOrderId = so.salesOrderId;
            if (so.status == 'CONFIRMED') {
              detected.add(professionalSteps.length + 2);
            }
          } catch (_) {}
        }
      }
    }
    return detected;
  }

  Future<Set<int>> _detectCommunity() async {
    final detected = <int>{};
    Lead? lead;
    if (leadId != null) {
      try {
        lead = await _leads.getById(leadId!);
      } catch (_) {
        lead = null;
      }
    }
    if (lead != null) {
      detected.add(0);
      if (lead.status == 'QUALIFIED' || lead.status == 'CONVERTED') {
        detected.add(1);
      }
      if (lead.status == 'CONVERTED') {
        detected.add(2);
        final match = await _findCustomerForLead(lead);
        if (match != null) {
          customerId = match.customerId;
        }
      }
    }

    if (customerId != null) {
      try {
        final cust = await _customers.getById(customerId!);
        final activities = await _activities.timeline(
          entityType: 'CUSTOMER',
          entityId: cust.customerId,
        );
        if (activities.any(
          (a) => a.activityTypeCode == 'CALL' && a.outcomeCode != null,
        )) {
          detected.add(3);
        }
        final hasContact = cust.contacts.any((c) => c.isPrimary);
        final hasAddress = cust.addresses.isNotEmpty;
        if (cust.status == 'ACTIVE' && hasContact && hasAddress) {
          detected.add(4);
        }
      } catch (_) {}
    }
    return detected;
  }

  Future<Customer?> _findCustomerForLead(Lead lead) async {
    final customers = await _customers.list(page: 1);
    final legal = (lead.companyName ?? lead.fullName).trim();
    for (final c in customers.items) {
      if (c.notes?.contains('Converted from lead ${lead.leadNumber}') == true) {
        return c;
      }
      if (c.legalName.trim() == legal) {
        return c;
      }
    }
    return null;
  }

  Future<void> _resolveIds() async {
    final leadRes = await _leads.list(pageSize: 1);
    if (leadId == null && leadRes.items.isNotEmpty) {
      leadId = leadRes.items.first.leadId;
    }
    if (hasOpportunityEdition) {
      final oppRes = await _opportunities.list(pageSize: 1);
      if (oppRes.items.isNotEmpty) {
        opportunityId ??= oppRes.items.first.opportunityId;
        customerId ??= oppRes.items.first.customerId;
      }
    }
    final custRes = await _customers.list(page: 1);
    if (customerId == null && custRes.items.isNotEmpty) {
      customerId = custRes.items.first.customerId;
    }
  }

  int get completedCount => completedSteps.length;
  double get progress => steps.isEmpty ? 0 : completedCount / steps.length;

  /// Plain-text UAT summary for governance sign-off (clipboard / email).
  String buildUatReport({
    String? tenantCode,
    String? tenantName,
    String? testerName,
  }) {
    final edition = hasOpportunityEdition ? 'Professional' : 'Community';
    final lines = <String>[
      'TC-L2C-CRM-01 — CRM UAT Report',
      'Edition: $edition',
      if (tenantCode != null)
        'Tenant: ${tenantName ?? tenantCode} ($tenantCode)',
      if (testerName != null) 'Tester: $testerName',
      'Generated: ${DateTime.now().toUtc().toIso8601String()}',
      '',
      'Progress: $completedCount/${steps.length} steps complete',
      '',
      'Record IDs:',
      '  Lead: ${leadId ?? '(not set)'}',
      if (hasOpportunityEdition)
        '  Opportunity: ${opportunityId ?? '(not set)'}',
      '  Customer: ${customerId ?? '(not set)'}',
      if (hasSalQuote) ...[
        '  Quotation: ${quotationId ?? '(not set)'}',
        '  Sales order: ${salesOrderId ?? '(not set)'}',
      ],
      '',
      'Steps:',
    ];
    for (var i = 0; i < steps.length; i++) {
      final mark = completedSteps.contains(i) ? '[PASS]' : '[    ]';
      lines.add('  $mark ${i + 1}. ${steps[i].$1}');
    }
    lines.add('');
    lines.add(
      'Status: ${completedCount == steps.length ? 'COMPLETE' : 'IN PROGRESS'}',
    );
    lines.add(
      hasSalQuote
          ? 'Scope: CRM + SAL quotation/SO confirm slice'
          : 'Scope: CRM slice only (SAL/FIN out of scope)',
    );
    return lines.join('\n');
  }
}
