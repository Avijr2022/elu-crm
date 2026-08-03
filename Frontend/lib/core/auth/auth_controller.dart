import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import '../auth/auth_service.dart';

class AuthController extends ChangeNotifier {
  final AuthService _auth = AuthService();

  bool booting = true;
  bool busy = false;
  bool isAuthenticated = false;
  String? error;
  Map<String, dynamic>? profile;

  Future<void> bootstrap() async {
    booting = true;
    notifyListeners();
    try {
      if (await _auth.hasSession()) {
        profile = await _auth.me();
        isAuthenticated = true;
      }
    } catch (e) {
      isAuthenticated = false;
      profile = null;
      await _auth.logout();
      if (kDebugMode) {
        debugPrint('Bootstrap session cleared: $e');
      }
    } finally {
      booting = false;
      notifyListeners();
    }
  }

  Future<bool> login({
    required String email,
    required String password,
    String tenantCode = 'EIIP001',
  }) async {
    busy = true;
    error = null;
    notifyListeners();
    try {
      await _auth.login(
        email: email,
        password: password,
        tenantCode: tenantCode,
      );
      profile = await _auth.me();
      isAuthenticated = true;
      return true;
    } catch (e) {
      error = e.toString().replaceFirst('Exception: ', '');
      isAuthenticated = false;
      return false;
    } finally {
      busy = false;
      notifyListeners();
    }
  }

  Future<void> logout() async {
    await _auth.logout();
    isAuthenticated = false;
    profile = null;
    notifyListeners();
  }
}
