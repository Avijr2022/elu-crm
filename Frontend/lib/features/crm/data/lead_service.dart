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
}
