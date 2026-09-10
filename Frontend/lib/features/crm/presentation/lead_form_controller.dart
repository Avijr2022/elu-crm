import 'package:flutter/material.dart';

import '../data/lead_model.dart';
import '../data/lead_service.dart';

class LeadFormController extends ChangeNotifier {
  LeadFormController({
    this.leadId,
    LeadService? service,
  }) : _service = service ?? LeadService();

  final String? leadId;
  final LeadService _service;

  bool loading = false;
  bool saving = false;
  String? error;
  Lead? existing;

  bool get isEditMode => leadId != null;
  bool get isTerminal => existing?.isTerminal ?? false;

  Future<void> loadExisting() async {
    if (leadId == null) return;
    loading = true;
    error = null;
    notifyListeners();
    try {
      existing = await _service.getById(leadId!);
    } catch (e) {
      error = e.toString().replaceFirst('Exception: ', '');
      existing = null;
    } finally {
      loading = false;
      notifyListeners();
    }
  }

  Future<Lead?> create({
    required String fullName,
    String? companyName,
    String? email,
    String? phone,
    String status = 'NEW',
    double estimatedValue = 0,
    String? notes,
  }) async {
    saving = true;
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
      return lead;
    } catch (e) {
      error = e.toString().replaceFirst('Exception: ', '');
      notifyListeners();
      return null;
    } finally {
      saving = false;
      notifyListeners();
    }
  }

  Future<Lead?> update({
    required String fullName,
    String? companyName,
    String? email,
    String? phone,
    String? status,
    double? estimatedValue,
    String? notes,
  }) async {
    if (leadId == null) return null;
    saving = true;
    error = null;
    notifyListeners();
    try {
      final lead = await _service.update(
        leadId!,
        fullName: fullName,
        companyName: companyName,
        email: email,
        phone: phone,
        status: status,
        estimatedValue: estimatedValue,
        notes: notes,
      );
      existing = lead;
      return lead;
    } catch (e) {
      error = e.toString().replaceFirst('Exception: ', '');
      notifyListeners();
      return null;
    } finally {
      saving = false;
      notifyListeners();
    }
  }
}
