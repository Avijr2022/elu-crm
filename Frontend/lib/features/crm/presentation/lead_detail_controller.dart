import 'package:flutter/material.dart';

import '../data/lead_model.dart';
import '../data/lead_service.dart';

class LeadDetailController extends ChangeNotifier {
  LeadDetailController({
    required this.leadId,
    LeadService? service,
  }) : _service = service ?? LeadService();

  final String leadId;
  final LeadService _service;

  bool loading = false;
  bool converting = false;
  bool qualifying = false;
  bool disqualifying = false;
  String? error;
  Lead? lead;

  Future<void> load() async {
    loading = true;
    error = null;
    notifyListeners();
    try {
      lead = await _service.getById(leadId);
    } catch (e) {
      error = e.toString().replaceFirst('Exception: ', '');
      lead = null;
    } finally {
      loading = false;
      notifyListeners();
    }
  }

  Future<String?> convert() async {
    if (lead == null || lead!.isTerminal) return null;
    converting = true;
    error = null;
    notifyListeners();
    try {
      final result = await _service.convert(leadId);
      await load();
      return result.referenceNumber;
    } catch (e) {
      error = e.toString().replaceFirst('Exception: ', '');
      notifyListeners();
      return null;
    } finally {
      converting = false;
      notifyListeners();
    }
  }

  Future<bool> qualify() async {
    if (lead == null || !lead!.canQualify) return false;
    qualifying = true;
    error = null;
    notifyListeners();
    try {
      await _service.qualify(leadId);
      await load();
      return true;
    } catch (e) {
      error = e.toString().replaceFirst('Exception: ', '');
      notifyListeners();
      return false;
    } finally {
      qualifying = false;
      notifyListeners();
    }
  }

  Future<bool> disqualify(String reason) async {
    if (lead == null || !lead!.canDisqualify) return false;
    disqualifying = true;
    error = null;
    notifyListeners();
    try {
      await _service.disqualify(leadId, reason);
      await load();
      return true;
    } catch (e) {
      error = e.toString().replaceFirst('Exception: ', '');
      notifyListeners();
      return false;
    } finally {
      disqualifying = false;
      notifyListeners();
    }
  }
}
