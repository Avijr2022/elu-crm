import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import '../network/api_config.dart';

class AuthService {
  static const _accessKey = 'access_token';
  static const _refreshKey = 'refresh_token';

  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
    String tenantCode = 'EIIP001',
  }) async {
    final uri = Uri.parse('${ApiConfig.baseUrl}/api/v1/auth/login');
    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email,
        'password': password,
        'tenant_code': tenantCode,
      }),
    );

    if (response.statusCode != 200) {
      throw Exception(_extractError(response.body) ?? 'Login failed (${response.statusCode})');
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_accessKey, data['access_token'] as String);
    await prefs.setString(_refreshKey, data['refresh_token'] as String);
    return data;
  }

  Future<Map<String, dynamic>> me() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString(_accessKey);
    if (token == null) {
      throw Exception('Not authenticated');
    }
    final uri = Uri.parse('${ApiConfig.baseUrl}/api/v1/auth/me');
    final response = await http.get(
      uri,
      headers: {'Authorization': 'Bearer $token'},
    );
    if (response.statusCode != 200) {
      throw Exception(_extractError(response.body) ?? 'Session expired');
    }
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_accessKey);
    await prefs.remove(_refreshKey);
  }

  Future<bool> hasSession() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_accessKey) != null;
  }

  String? _extractError(String body) {
    try {
      final map = jsonDecode(body) as Map<String, dynamic>;
      final err = map['detail'] ?? map['error'];
      if (err is Map && err['error'] is Map) {
        return err['error']['message'] as String?;
      }
      if (err is Map && err['message'] is String) {
        return err['message'] as String;
      }
      if (err is Map && err['error'] is Map) {
        return (err['error'] as Map)['message'] as String?;
      }
    } catch (_) {}
    return null;
  }
}
