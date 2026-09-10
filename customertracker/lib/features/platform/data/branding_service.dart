import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class TenantBranding {
  TenantBranding({required this.tenantId, this.logoUrl, this.primaryColor});

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
  static const _accessKey = 'access_token';

  Future<Map<String, String>> _headers({bool jsonBody = false}) async {
    final sp = await SharedPreferences.getInstance();
    final token = sp.getString(_accessKey);
    return {
      if (jsonBody) 'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  Uri _uri(String path, [Map<String, String>? query]) =>
      Uri.parse('http://localhost:8000$path').replace(queryParameters: query);

  Future<TenantBranding> getBranding() async {
    final resp = await http.get(_uri('/api/v1/tenant/branding'),
        headers: await _headers());
    if (resp.statusCode != 200) throw Exception('Failed to load branding');
    return TenantBranding.fromJson(
        jsonDecode(resp.body) as Map<String, dynamic>);
  }

  Future<TenantBranding> updatePrimaryColor(String primaryColor) async {
    final resp = await http.put(_uri('/api/v1/tenant/branding/primary-color'),
        headers: await _headers(jsonBody: true),
        body: jsonEncode({'primary_color': primaryColor}));
    if (resp.statusCode != 200) throw Exception('Failed to update color');
    return TenantBranding.fromJson(
        jsonDecode(resp.body) as Map<String, dynamic>);
  }
}
