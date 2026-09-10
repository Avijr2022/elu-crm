import 'dart:convert';

import '../../../core/network/api_client.dart';
import 'lead_model.dart';

class LeadService {
  LeadService({ApiClient? client}) : _client = client ?? ApiClient();

  final ApiClient _client;

  Future<LeadListResult> list({
    int page = 1,
    int pageSize = 25,
    String? status,
    String? search,
  }) async {
    final query = <String, String>{
      'page': '$page',
      'page_size': '$pageSize',
      if (status != null && status.isNotEmpty) 'status': status,
      if (search != null && search.isNotEmpty) 'search': search,
    };
    final response = await _client.get('/api/v1/crm/leads', query: query);
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to load leads (${response.statusCode})',
      );
    }
    return LeadListResult.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  Future<Lead> create({
    required String fullName,
    String? companyName,
    String? email,
    String? phone,
    String status = 'NEW',
    double estimatedValue = 0,
    String? notes,
  }) async {
    final response = await _client.post('/api/v1/crm/leads', body: {
      'full_name': fullName,
      if (companyName != null && companyName.isNotEmpty)
        'company_name': companyName,
      if (email != null && email.isNotEmpty) 'email': email,
      if (phone != null && phone.isNotEmpty) 'phone': phone,
      'status': status,
      'estimated_value': estimatedValue,
      'currency_code': 'INR',
      if (notes != null && notes.isNotEmpty) 'notes': notes,
    });
    if (response.statusCode != 201 && response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to create lead (${response.statusCode})',
      );
    }
    return Lead.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  Future<Lead> getById(String id) async {
    final response = await _client.get('/api/v1/crm/leads/$id');
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to load lead (${response.statusCode})',
      );
    }
    return Lead.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  Future<Lead> update(
    String id, {
    String? fullName,
    String? companyName,
    String? email,
    String? phone,
    String? status,
    double? estimatedValue,
    String? notes,
  }) async {
    final body = <String, dynamic>{};
    if (fullName != null) body['full_name'] = fullName;
    if (companyName != null) body['company_name'] = companyName;
    if (email != null) body['email'] = email;
    if (phone != null) body['phone'] = phone;
    if (status != null) body['status'] = status;
    if (estimatedValue != null) body['estimated_value'] = estimatedValue;
    if (notes != null) body['notes'] = notes;

    final response = await _client.patch('/api/v1/crm/leads/$id', body: body);
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to update lead (${response.statusCode})',
      );
    }
    return Lead.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  Future<LeadConvertResult> convert(String leadId) async {
    final response = await _client.post('/api/v1/crm/leads/$leadId/convert');
    if (response.statusCode != 201 && response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to convert lead (${response.statusCode})',
      );
    }
    final data = jsonDecode(response.body) as Map<String, dynamic>;
    final type = data['convert_type'] as String;
    if (type == 'CUSTOMER') {
      final c = data['customer'] as Map<String, dynamic>;
      return LeadConvertResult(
        convertType: type,
        referenceNumber: c['customer_number'] as String,
      );
    }
    final o = data['opportunity'] as Map<String, dynamic>;
    return LeadConvertResult(
      convertType: type,
      referenceNumber: o['opportunity_number'] as String,
    );
  }

  Future<Lead> qualify(String leadId) async {
    final response = await _client.post('/api/v1/crm/leads/$leadId/qualify');
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to qualify lead (${response.statusCode})',
      );
    }
    return Lead.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  Future<Lead> disqualify(String leadId, String reason) async {
    final response = await _client.post(
      '/api/v1/crm/leads/$leadId/disqualify',
      body: {'reason': reason},
    );
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to disqualify lead (${response.statusCode})',
      );
    }
    return Lead.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }
}

class LeadConvertResult {
  LeadConvertResult({required this.convertType, this.referenceNumber});
  final String convertType;
  final String? referenceNumber;
}
