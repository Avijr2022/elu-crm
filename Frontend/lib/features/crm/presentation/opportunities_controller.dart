import 'package:flutter/material.dart';

import '../data/lookup_service.dart';
import '../data/opportunity_model.dart';
import '../data/opportunity_service.dart';

class OpportunitiesController extends ChangeNotifier {
  OpportunitiesController({OpportunityService? service, LookupService? lookups})
      : _service = service ?? OpportunityService(),
        _lookups = lookups ?? LookupService();

  final OpportunityService _service;
  final LookupService _lookups;

  bool loading = false;
  String? error;
  List<Opportunity> items = [];
  int total = 0;
  String search = '';
  String? stageFilter;
  PipelineResult? pipeline;
  List<String> stages = [];

  String? nextStage(String current) => nextPipelineStage(stages, current);

  Future<void> load() async {
    loading = true;
    error = null;
    notifyListeners();
    try {
      stages = await _lookups.pipelineStageCodes();
      final result = await _service.list(
        search: search.isEmpty ? null : search,
        stage: stageFilter,
      );
      items = result.items;
      total = result.total;
      pipeline = await _service.pipeline();
    } catch (e) {
      error = e.toString().replaceFirst('Exception: ', '');
      items = [];
      total = 0;
      pipeline = null;
    } finally {
      loading = false;
      notifyListeners();
    }
  }

  Future<Opportunity?> createOpportunity({
    required String name,
    String? companyName,
    double opportunityValue = 0,
    String? notes,
  }) async {
    error = null;
    notifyListeners();
    try {
      final opp = await _service.create(
        name: name,
        companyName: companyName,
        opportunityValue: opportunityValue,
        notes: notes,
      );
      await load();
      return opp;
    } catch (e) {
      error = e.toString().replaceFirst('Exception: ', '');
      notifyListeners();
      return null;
    }
  }

  Future<bool> advance(Opportunity opp) async {
    final next = nextStage(opp.stage);
    if (next == null) return false;
    error = null;
    notifyListeners();
    try {
      await _service.advanceStage(
        opportunityId: opp.opportunityId,
        stage: next,
      );
      await load();
      return true;
    } catch (e) {
      error = e.toString().replaceFirst('Exception: ', '');
      notifyListeners();
      return false;
    }
  }
}
