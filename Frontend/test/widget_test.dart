import 'package:elinkup_app/core/auth/crm_rbac.dart';
import 'package:elinkup_app/core/edition/edition_controller.dart';
import 'package:elinkup_app/core/widgets/crm_search_field.dart';
import 'package:elinkup_app/features/crm/data/opportunity_model.dart';
import 'package:elinkup_app/features/crm/presentation/activity_types_page.dart';
import 'package:elinkup_app/features/crm/presentation/crm_dashboard_view.dart';
import 'package:elinkup_app/features/crm/presentation/l2c_demo_controller.dart';
import 'package:elinkup_app/features/crm/presentation/l2c_demo_journey_page.dart';
import 'package:elinkup_app/features/crm/presentation/widgets/close_won_wizard_dialog.dart';
import 'package:elinkup_app/features/crm/data/lookup_service.dart';
import 'package:elinkup_app/features/crm/presentation/widgets/log_activity_dialog.dart';
import 'package:elinkup_app/features/platform/presentation/login_page.dart';
import 'package:elinkup_app/features/platform/presentation/tenant_branding_page.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';

import 'package:elinkup_app/core/auth/auth_controller.dart';

void main() {
  test('CrmRbac canCloseWon with approve permission', () {
    expect(
      CrmRbac.canCloseWon({
        'role_code': 'SALES_MANAGER',
        'permissions': ['opportunity.approve'],
      }),
      isTrue,
    );
  });

  testWidgets('LoginPage renders sign-in form', (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: ChangeNotifierProvider(
          create: (_) => AuthController(),
          child: const LoginPage(),
        ),
      ),
    );
    expect(find.text('E-LinkUp'), findsOneWidget);
    expect(find.text('Sign in'), findsOneWidget);
  });

  testWidgets('CrmSearchField renders hint text', (WidgetTester tester) async {
    final controller = TextEditingController();
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: CrmSearchField(
            controller: controller,
            hintText: 'Search leads',
            onSearch: () {},
          ),
        ),
      ),
    );
    expect(find.text('Search leads'), findsOneWidget);
    controller.dispose();
  });

  testWidgets('LogActivityDialog shows activity type dropdown',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Builder(
          builder: (ctx) => Scaffold(
            body: Center(
              child: FilledButton(
                onPressed: () => showDialog<void>(
                  context: ctx,
                  builder: (_) => const LogActivityDialog(
                    entityType: 'LEAD',
                    entityId: 'lead-1',
                    activityTypes: ['NOTE', 'CALL', 'MEETING'],
                  ),
                ),
                child: const Text('Log'),
              ),
            ),
          ),
        ),
      ),
    );
    await tester.tap(find.text('Log'));
    await tester.pumpAndSettle();
    expect(find.text('Activity type'), findsOneWidget);
    expect(find.text('NOTE'), findsOneWidget);
  });

  testWidgets('LogActivityDialog shows outcome dropdown for CALL',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Builder(
          builder: (ctx) => Scaffold(
            body: Center(
              child: FilledButton(
                onPressed: () => showDialog<void>(
                  context: ctx,
                  builder: (_) => LogActivityDialog(
                    entityType: 'LEAD',
                    entityId: 'lead-1',
                    activityTypes: const ['CALL'],
                    outcomesByType: {
                      'CALL': [
                        ActivityOutcome(
                          activityOutcomeId: '1',
                          activityTypeCode: 'CALL',
                          code: 'INTERESTED',
                          name: 'Interested',
                          isPositive: true,
                          isActive: true,
                        ),
                      ],
                    },
                  ),
                ),
                child: const Text('Log'),
              ),
            ),
          ),
        ),
      ),
    );
    await tester.tap(find.text('Log'));
    await tester.pumpAndSettle();
    expect(find.text('Outcome *'), findsOneWidget);
    expect(find.text('Interested'), findsOneWidget);
  });

  testWidgets('CloseWonWizard shows review step', (WidgetTester tester) async {
    final opp = Opportunity(
      opportunityId: 'id-1',
      opportunityNumber: 'EUP-OPP-2026-00001',
      name: 'Test Deal',
      stage: 'NEGOTIATION',
      status: 'OPEN',
      opportunityValue: 100000,
      probability: 90,
      weightedValue: 90000,
      currencyCode: 'INR',
    );
    await tester.pumpWidget(
      MaterialApp(
        home: Builder(
          builder: (ctx) => Scaffold(
            body: Center(
              child: FilledButton(
                onPressed: () => CloseWonWizardDialog.show(
                  ctx,
                  opportunity: opp,
                  formatValue: (_) => '₹ 100000',
                  onConfirm: ({closingNotes}) async => true,
                ),
                child: const Text('Open'),
              ),
            ),
          ),
        ),
      ),
    );
    await tester.tap(find.text('Open'));
    await tester.pumpAndSettle();
    expect(find.text('Test Deal'), findsOneWidget);
    expect(find.text('Close Won — Step 1 of 2'), findsOneWidget);
  });

  testWidgets('L2cDemoJourneyPage shows professional UAT steps', (WidgetTester tester) async {
    await tester.binding.setSurfaceSize(const Size(800, 2400));
    await tester.pumpWidget(
      MaterialApp(
        home: ChangeNotifierProvider(
          create: (_) => EditionController(),
          child: L2cDemoJourneyPage(
            controller: L2cDemoController(hasOpportunityEdition: true),
          ),
        ),
      ),
    );
    expect(find.text('L2C Demo Journey'), findsOneWidget);
    expect(find.text('Create lead'), findsOneWidget);
    expect(find.text('Convert to opportunity'), findsOneWidget);
    expect(find.text('Check progress'), findsOneWidget);
    expect(find.text('Copy UAT report'), findsOneWidget);
    expect(find.text('Demo record IDs'), findsOneWidget);
    await tester.binding.setSurfaceSize(null);
  });

  testWidgets('L2cDemoJourneyPage shows SAL steps when enabled', (WidgetTester tester) async {
    await tester.binding.setSurfaceSize(const Size(800, 2600));
    await tester.pumpWidget(
      MaterialApp(
        home: ChangeNotifierProvider(
          create: (_) => EditionController(),
          child: L2cDemoJourneyPage(
            controller: L2cDemoController(
              hasOpportunityEdition: true,
              hasSalQuote: true,
            ),
          ),
        ),
      ),
    );
    expect(find.text('Accept quotation'), findsOneWidget);
    expect(find.text('Confirm sales order'), findsOneWidget);
    expect(find.text('Convert to sales order'), findsOneWidget);
    await tester.binding.setSurfaceSize(null);
  });

  testWidgets('L2cDemoJourneyPage shows community UAT steps', (WidgetTester tester) async {
    await tester.binding.setSurfaceSize(const Size(800, 2000));
    await tester.pumpWidget(
      MaterialApp(
        home: ChangeNotifierProvider(
          create: (_) => EditionController(),
          child: L2cDemoJourneyPage(
            controller: L2cDemoController(hasOpportunityEdition: false),
          ),
        ),
      ),
    );
    expect(find.text('Convert to customer'), findsOneWidget);
    expect(find.text('Convert to opportunity'), findsNothing);
    expect(find.text('Close won'), findsNothing);
    expect(find.text('Opportunity ID'), findsNothing);
    await tester.binding.setSurfaceSize(null);
  });

  testWidgets('ActivityTypesPage shows title', (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: ChangeNotifierProvider(
          create: (_) => AuthController(),
          child: const ActivityTypesPage(),
        ),
      ),
    );
    expect(find.text('Activity types'), findsOneWidget);
  });

  testWidgets('CrmDashboardView shows welcome and L2C link', (WidgetTester tester) async {
    final edition = EditionController();
    edition.loaded = true;
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: ChangeNotifierProvider.value(
            value: edition,
            child: const CrmDashboardView(profile: {
              'display_name': 'Test User',
              'tenant_name': 'Demo',
              'tenant_code': 'EIIP001',
              'role_name': 'Manager',
              'organization_name': 'HQ',
            }),
          ),
        ),
      ),
    );
    expect(find.text('Welcome, Test User'), findsOneWidget);
    expect(find.text('L2C Demo Journey'), findsOneWidget);
    await tester.pump(const Duration(seconds: 1));
  });

  testWidgets('TenantBrandingPage shows title', (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: ChangeNotifierProvider(
          create: (_) => AuthController(),
          child: const TenantBrandingPage(),
        ),
      ),
    );
    expect(find.text('Tenant branding'), findsOneWidget);
  });
}
