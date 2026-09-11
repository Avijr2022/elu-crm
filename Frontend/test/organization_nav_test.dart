import 'package:elinkup_app/core/auth/auth_controller.dart';
import 'package:elinkup_app/core/auth/crm_rbac.dart';
import 'package:elinkup_app/core/edition/edition_controller.dart';
import 'package:elinkup_app/core/routing/app_router.dart';
import 'package:elinkup_app/core/routing/crm_routes.dart';
import 'package:elinkup_app/features/platform/presentation/organizations_page.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

const _tenantAdmin = {
  'role_code': 'TENANT_ADMIN',
  'permissions': ['organization.read', 'organization.update'],
};
const _financeUser = {
  'role_code': 'FINANCE_USER',
  'permissions': ['organization.read', 'organization.export'],
};
const _salesManager = {
  'role_code': 'SALES_MANAGER',
  'permissions': ['organization.read'],
};
const _platformAdmin = {
  'role_code': 'PLATFORM_ADMIN',
  'permissions': <String>[],
};
const _projectManager = {
  'role_code': 'PROJECT_MANAGER',
  'permissions': <String>[],
};

AuthController _auth(Map<String, dynamic> profile) {
  final auth = AuthController();
  auth.booting = false;
  auth.isAuthenticated = true;
  auth.profile = profile;
  return auth;
}

EditionController _edition() {
  final edition = EditionController();
  edition.loaded = true;
  return edition;
}

Widget _app(GoRouter router, AuthController auth, EditionController edition) {
  return MultiProvider(
    providers: [
      ChangeNotifierProvider.value(value: auth),
      ChangeNotifierProvider.value(value: edition),
    ],
    child: MaterialApp.router(routerConfig: router),
  );
}

/// The shell renders the full navigation only on wide layouts (>= 900px).
void _useWideLayout(WidgetTester tester) {
  tester.view.physicalSize = const Size(1400, 900);
  tester.view.devicePixelRatio = 1.0;
  addTearDown(tester.view.reset);
}

void main() {
  group('CrmRbac.canManageOrganizations', () {
    test('true for Tenant Admin only', () {
      expect(CrmRbac.canManageOrganizations(_tenantAdmin), isTrue);
      expect(CrmRbac.canManageOrganizations(_financeUser), isFalse);
      expect(CrmRbac.canManageOrganizations(_salesManager), isFalse);
      expect(CrmRbac.canManageOrganizations(_platformAdmin), isFalse);
      expect(CrmRbac.canManageOrganizations(_projectManager), isFalse);
      expect(CrmRbac.canManageOrganizations(null), isFalse);
    });
  });

  group('Organization navigation visibility (BFS-PF-004 §12)', () {
    testWidgets('Tenant Admin sees the Organizations nav item', (tester) async {
      _useWideLayout(tester);
      final auth = _auth(_tenantAdmin);
      final edition = _edition();
      final router = createAppRouter(auth, edition);
      await tester.pumpWidget(_app(router, auth, edition));
      await tester.pump();

      expect(find.text('Organizations'), findsOneWidget);
    });

    testWidgets('Platform Admin does not see the Organizations nav item',
        (tester) async {
      _useWideLayout(tester);
      final auth = _auth(_platformAdmin);
      final edition = _edition();
      final router = createAppRouter(auth, edition);
      await tester.pumpWidget(_app(router, auth, edition));
      await tester.pump();

      expect(find.text('Organizations'), findsNothing);
    });

    testWidgets('Sales Manager does not see the Organizations nav item',
        (tester) async {
      _useWideLayout(tester);
      final auth = _auth(_salesManager);
      final edition = _edition();
      final router = createAppRouter(auth, edition);
      await tester.pumpWidget(_app(router, auth, edition));
      await tester.pump();

      expect(find.text('Organizations'), findsNothing);
    });
  });

  group('Organization route authorization', () {
    testWidgets('Tenant Admin can open /organizations', (tester) async {
      final auth = _auth(_tenantAdmin);
      final edition = _edition();
      final router = createAppRouter(auth, edition);
      await tester.pumpWidget(_app(router, auth, edition));
      await tester.pump();

      router.go(CrmRoutes.organizations);
      await tester.pump();
      await tester.pump();

      expect(
        router.routerDelegate.currentConfiguration.uri.path,
        CrmRoutes.organizations,
      );
      expect(find.byType(OrganizationsPage), findsOneWidget);
    });

    testWidgets('Non-Tenant-Admin is redirected away from /organizations',
        (tester) async {
      final auth = _auth(_salesManager);
      final edition = _edition();
      final router = createAppRouter(auth, edition);
      await tester.pumpWidget(_app(router, auth, edition));
      await tester.pump();

      router.go(CrmRoutes.organizations);
      await tester.pump();
      await tester.pump();

      expect(
          router.routerDelegate.currentConfiguration.uri.path, CrmRoutes.home);
      expect(find.byType(OrganizationsPage), findsNothing);
    });
  });
}
