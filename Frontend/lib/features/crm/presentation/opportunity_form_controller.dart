import 'package:flutter/material.dart';

import '../data/opportunity_model.dart';
import '../data/opportunity_service.dart';

class OpportunityFormController extends ChangeNotifier {
  OpportunityFormController({
    this.opportunityId,
    OpportunityService? service,
  }) : _service = service ?? OpportunityService();

  final String? opportunityId;
  final OpportunityService _service;

  bool loading = false;
  bool saving = false;
  String? error;
  Opportunity? existing;

  bool get isEditMode => opportunityId != null;
  bool get isTerminal => existing?.isTerminal ?? false;

  Future<void> loadExisting() async {
    if (opportunityId == null) return;
    loading = true;
    error = null;
    notifyListeners();
    try {
      existing = await _service.getById(opportunityId!);
    } catch (e) {
      error = e.toString().replaceFirst('Exception: ', '');
      existing = null;
    } finally {
      loading = false;
      notifyListeners();
    }
  }

  Future<Opportunity?> create({
    required String name,
    String? companyName,
    double opportunityValue = 0,
    String? notes,
  }) async {
    saving = true;
    error = null;
    notifyListeners();
    try {
      return await _service.create(
        name: name,
        companyName: companyName,
        opportunityValue: opportunityValue,
        notes: notes,
      );
    } catch (e) {
      error = e.toString().replaceFirst('Exception: ', '');
      notifyListeners();
      return null;
    } finally {
      saving = false;
      notifyListeners();
    }
  }

  Future<Opportunity?> saveEdit({
    required String name,
    String? companyName,
    double? opportunityValue,
    String? notes,
  }) async {
    if (opportunityId == null) return null;
    saving = true;
    error = null;
    notifyListeners();
    try {
      existing = await _service.update(
        opportunityId!,
        name: name,
        companyName: companyName,
        opportunityValue: opportunityValue,
        notes: notes,
      );
      return existing;
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
