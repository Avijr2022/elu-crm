import 'dart:convert';

import '../../../core/network/api_client.dart';

class TenantBranding {
  TenantBranding({
    required this.tenantId,
    this.logoUrl,
    this.primaryColor,
  });

  final String tenantId;
  final String? logoUrl;
  final String? primaryColor;

  factory TenantBranding.fromJson(Map<String, dynamic> json) => TenantBranding(
        tenantId: json['tenant_id'] as String,
        logoUrl: json['logo_url'] as String?,
        primaryColor: json['primary_color'] as String?,
      );
}

class BrandingService {
  BrandingService({ApiClient? client}) : _client = client ?? ApiClient();

  final ApiClient _client;

  Future<TenantBranding> getBranding() async {
    final response = await _client.get('/api/v1/tenant/branding');
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to load branding (${response.statusCode})',
      );
    }
    return TenantBranding.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  Future<TenantBranding> uploadLogo(String logoDataUrl) async {
    final response = await _client.put(
      '/api/v1/tenant/branding/logo',
      body: {'logo_data_url': logoDataUrl},
    );
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to upload logo (${response.statusCode})',
      );
    }
    return TenantBranding.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  Future<TenantBranding> updatePrimaryColor(String primaryColor) async {
    final response = await _client.put(
      '/api/v1/tenant/branding/primary-color',
      body: {'primary_color': primaryColor},
    );
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to update color (${response.statusCode})',
      );
    }
    return TenantBranding.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }
}
