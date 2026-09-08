import 'package:flutter/material.dart';

import '../data/customer_service.dart';
import '../data/lookup_service.dart';
import '../data/opportunity_model.dart';
import '../data/opportunity_service.dart';

class OpportunityDetailController extends ChangeNotifier {
  OpportunityDetailController({
    required this.opportunityId,
    OpportunityService? service,
    LookupService? lookups,
  })  : _service = service ?? OpportunityService(),
        _lookups = lookups ?? LookupService();

  final String opportunityId;
  final OpportunityService _service;
  final LookupService _lookups;

  bool loading = false;
  bool advancing = false;
  bool closing = false;
  String? error;
  Opportunity? opportunity;
  String? customerLabel;
  List<String> stages = [];
  Map<String, String> stageNames = {};

  String? nextStage(String current) => nextPipelineStage(stages, current);

  Future<void> load() async {
    loading = true;
    error = null;
    notifyListeners();
    try {
      stages = await _lookups.pipelineStageCodes();
      final stageRows = await _lookups.listOpportunityStages(includeInactive: false);
      stageNames = {for (final s in stageRows) s.code: s.name};
      opportunity = await _service.getById(opportunityId);
      customerLabel = null;
      final cid = opportunity?.customerId;
      if (cid != null) {
        try {
          customerLabel = (await CustomerService().getById(cid)).customerNumber;
        } catch (_) {
          customerLabel = cid;
        }
      }
    } catch (e) {
      error = e.toString().replaceFirst('Exception: ', '');
      opportunity = null;
    } finally {
      loading = false;
      notifyListeners();
    }
  }

  Future<bool> advance() async {
    final opp = opportunity;
    if (opp == null || opp.isTerminal || opp.status == 'ON_HOLD') {
      return false;
    }
    final next = nextStage(opp.stage);
    if (next == null) return false;
    advancing = true;
    error = null;
    notifyListeners();
    try {
      opportunity = await _service.advanceStage(
        opportunityId: opp.opportunityId,
        stage: next,
      );
      return true;
    } catch (e) {
      error = e.toString().replaceFirst('Exception: ', '');
      notifyListeners();
      return false;
    } finally {
      advancing = false;
      notifyListeners();
    }
  }

  Future<bool> closeWon({String? closingNotes}) async {
    final opp = opportunity;
    if (opp == null || opp.isTerminal) return false;
    closing = true;
    error = null;
    notifyListeners();
    try {
      final mergedNotes = closingNotes != null && closingNotes.isNotEmpty
          ? [if (opp.notes != null && opp.notes!.isNotEmpty) opp.notes, '[Close won] $closingNotes']
              .join('\n')
          : opp.notes;
      opportunity = await _service.update(
        opp.opportunityId,
        status: 'CLOSED_WON',
        notes: mergedNotes,
      );
      return true;
    } catch (e) {
      error = e.toString().replaceFirst('Exception: ', '');
      notifyListeners();
      return false;
    } finally {
      closing = false;
      notifyListeners();
    }
  }

  Future<bool> closeLost(String lossReason) async {
    final opp = opportunity;
    if (opp == null || opp.isTerminal) return false;
    closing = true;
    error = null;
    notifyListeners();
    try {
      opportunity = await _service.update(
        opp.opportunityId,
        status: 'CLOSED_LOST',
        lossReason: lossReason.trim(),
      );
      return true;
    } catch (e) {
      error = e.toString().replaceFirst('Exception: ', '');
      notifyListeners();
      return false;
    } finally {
      closing = false;
      notifyListeners();
    }
  }
}
