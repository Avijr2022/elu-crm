import 'package:elinkup_app/core/auth/auth_controller.dart';
import 'package:go_router/go_router.dart';
import 'package:elinkup_app/core/edition/edition_controller.dart';
import 'package:elinkup_app/core/routing/app_router.dart';
import 'package:elinkup_app/core/routing/crm_routes.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';

Widget _app(GoRouter router, AuthController auth, EditionController edition) {
  return MultiProvider(
    providers: [
      ChangeNotifierProvider.value(value: auth),
      ChangeNotifierProvider.value(value: edition),
    ],
    child: MaterialApp.router(routerConfig: router),
  );
}

void main() {
  testWidgets('Unauthenticated user redirected to login', (tester) async {
    final auth = AuthController();
    auth.booting = false;
    final edition = EditionController();
    final router = createAppRouter(auth, edition);
    await tester.pumpWidget(_app(router, auth, edition));
    await tester.pumpAndSettle();
    expect(router.routerDelegate.currentConfiguration.uri.path, CrmRoutes.login);
  });

  testWidgets('Authenticated user lands on home', (tester) async {
    final auth = AuthController();
    auth.booting = false;
    auth.isAuthenticated = true;
    auth.profile = {
      'role_code': 'SALES_MANAGER',
      'permissions': ['lead.read', 'opportunity.read'],
    };
    final edition = EditionController();
    edition.loaded = true;
    final router = createAppRouter(auth, edition);
    await tester.pumpWidget(_app(router, auth, edition));
    await tester.pump();
    expect(router.routerDelegate.currentConfiguration.uri.path, CrmRoutes.home);
  });
}
