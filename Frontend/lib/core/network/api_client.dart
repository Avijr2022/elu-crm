import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import 'api_config.dart';

class ApiClient {
  static const _accessKey = 'access_token';

  Future<Map<String, String>> _headers({bool jsonBody = false}) async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString(_accessKey);
    return {
      if (jsonBody) 'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  Uri _uri(String path, [Map<String, String>? query]) {
    return Uri.parse('${ApiConfig.baseUrl}$path').replace(queryParameters: query);
  }

  String? extractError(String body) {
    try {
      final map = jsonDecode(body) as Map<String, dynamic>;
      final err = map['detail'] ?? map['error'];
      if (err is Map && err['error'] is Map) {
        return err['error']['message'] as String?;
      }
      if (err is Map && err['message'] is String) {
        return err['message'] as String;
      }
    } catch (_) {}
    return null;
  }

  Future<http.Response> get(String path, {Map<String, String>? query}) async {
    return http.get(_uri(path, query), headers: await _headers());
  }

  Future<http.Response> post(String path, {Object? body}) async {
    return http.post(
      _uri(path),
      headers: await _headers(jsonBody: true),
      body: body == null ? null : jsonEncode(body),
    );
  }

  Future<http.Response> put(String path, {Object? body}) async {
    return http.put(
      _uri(path),
      headers: await _headers(jsonBody: true),
      body: body == null ? null : jsonEncode(body),
    );
  }

  Future<http.Response> patch(String path, {Object? body}) async {
    return http.patch(
      _uri(path),
      headers: await _headers(jsonBody: true),
      body: body == null ? null : jsonEncode(body),
    );
  }

  Future<http.Response> delete(String path) async {
    return http.delete(_uri(path), headers: await _headers());
  }
}
