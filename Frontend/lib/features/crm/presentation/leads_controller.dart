import 'package:flutter/material.dart';

import '../data/lead_model.dart';
import '../data/lead_service.dart';
import '../data/opportunity_service.dart';

class LeadsController extends ChangeNotifier {
  LeadsController({
    LeadService? service,
    OpportunityService? opportunityService,
  })  : _service = service ?? LeadService(),
        _opportunityService = opportunityService ?? OpportunityService();

  final LeadService _service;
  final OpportunityService _opportunityService;

  bool loading = false;
  String? error;
  List<Lead> items = [];
  int total = 0;
  String search = '';

  Future<void> load() async {
    loading = true;
    error = null;
    notifyListeners();
    try {
      final result =
          await _service.list(search: search.isEmpty ? null : search);
      items = result.items;
      total = result.total;
    } catch (e) {
      error = e.toString().replaceFirst('Exception: ', '');
      items = [];
      total = 0;
    } finally {
      loading = false;
      notifyListeners();
    }
  }

  Future<Lead?> createLead({
    required String fullName,
    String? companyName,
    String? email,
    String? phone,
    String status = 'NEW',
    double estimatedValue = 0,
    String? notes,
  }) async {
    error = null;
    notifyListeners();
    try {
      final lead = await _service.create(
        fullName: fullName,
        companyName: companyName,
        email: email,
        phone: phone,
        status: status,
        estimatedValue: estimatedValue,
        notes: notes,
      );
      await load();
      return lead;
    } catch (e) {
      error = e.toString().replaceFirst('Exception: ', '');
      notifyListeners();
      return null;
    }
  }

  Future<String?> convertLead(Lead lead) async {
    error = null;
    notifyListeners();
    try {
      final opp = await _opportunityService.convertLead(lead.leadId);
      await load();
      return opp.opportunityNumber;
    } catch (e) {
      error = e.toString().replaceFirst('Exception: ', '');
      notifyListeners();
      return null;
    }
  }
}
