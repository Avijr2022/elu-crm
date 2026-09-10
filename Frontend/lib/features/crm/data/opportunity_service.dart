import 'dart:convert';

import '../../../core/network/api_client.dart';
import 'opportunity_model.dart';

class OpportunityService {
  OpportunityService({ApiClient? client}) : _client = client ?? ApiClient();

  final ApiClient _client;

  Future<OpportunityListResult> list({
    int page = 1,
    int pageSize = 25,
    String? stage,
    String? status,
    String? search,
    String? customerId,
  }) async {
    final query = <String, String>{
      'page': '$page',
      'page_size': '$pageSize',
      if (stage != null && stage.isNotEmpty) 'stage': stage,
      if (status != null && status.isNotEmpty) 'status': status,
      if (search != null && search.isNotEmpty) 'search': search,
      if (customerId != null && customerId.isNotEmpty) 'customer_id': customerId,
    };
    final response =
        await _client.get('/api/v1/crm/opportunities', query: query);
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to load opportunities (${response.statusCode})',
      );
    }
    return OpportunityListResult.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  Future<OpportunityListResult> listForCustomer(String customerId) async {
    final response = await _client.get(
      '/api/v1/crm/customers/$customerId/opportunities',
    );
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to load customer opportunities (${response.statusCode})',
      );
    }
    return OpportunityListResult.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  Future<Opportunity> getById(String id) async {
    final response = await _client.get('/api/v1/crm/opportunities/$id');
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to load opportunity (${response.statusCode})',
      );
    }
    return Opportunity.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  Future<PipelineResult> pipeline() async {
    final response = await _client.get('/api/v1/crm/opportunities/pipeline');
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to load pipeline (${response.statusCode})',
      );
    }
    return PipelineResult.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  Future<Opportunity> create({
    required String name,
    String? companyName,
    String stage = 'QUALIFICATION',
    double opportunityValue = 0,
    String? notes,
    String? sourceLeadId,
  }) async {
    final response = await _client.post('/api/v1/crm/opportunities', body: {
      'name': name,
      if (companyName != null && companyName.isNotEmpty)
        'company_name': companyName,
      'stage': stage,
      'status': 'OPEN',
      'opportunity_value': opportunityValue,
      'currency_code': 'INR',
      if (notes != null && notes.isNotEmpty) 'notes': notes,
      if (sourceLeadId != null && sourceLeadId.isNotEmpty)
        'source_lead_id': sourceLeadId,
    });
    if (response.statusCode != 201 && response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to create opportunity (${response.statusCode})',
      );
    }
    return Opportunity.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  Future<Opportunity> update(
    String id, {
    String? name,
    String? companyName,
    double? opportunityValue,
    String? notes,
    String? status,
    String? lossReason,
  }) async {
    final body = <String, dynamic>{
      if (name != null) 'name': name,
      if (companyName != null) 'company_name': companyName,
      if (opportunityValue != null) 'opportunity_value': opportunityValue,
      if (notes != null) 'notes': notes,
      if (status != null) 'status': status,
      if (lossReason != null) 'loss_reason': lossReason,
    };
    final response =
        await _client.patch('/api/v1/crm/opportunities/$id', body: body);
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to update opportunity (${response.statusCode})',
      );
    }
    return Opportunity.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  Future<Opportunity> advanceStage({
    required String opportunityId,
    required String stage,
  }) async {
    final response = await _client.patch(
      '/api/v1/crm/opportunities/$opportunityId/stage',
      body: {'stage': stage},
    );
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to advance stage (${response.statusCode})',
      );
    }
    return Opportunity.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  Future<Opportunity> convertLead(String leadId) async {
    final response =
        await _client.post('/api/v1/crm/leads/$leadId/convert');
    if (response.statusCode != 201 && response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to convert lead (${response.statusCode})',
      );
    }
    return Opportunity.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }
}
