import 'package:elinkup_app/core/auth/auth_controller.dart';
import 'package:elinkup_app/core/edition/crm_features.dart';
import 'package:elinkup_app/core/edition/edition_controller.dart';
import 'package:elinkup_app/core/routing/app_router.dart';
import 'package:elinkup_app/core/routing/crm_routes.dart';
import 'package:elinkup_app/core/widgets/crm_status_chip.dart';
import 'package:elinkup_app/features/crm/data/quotation_service.dart';
import 'package:elinkup_app/features/crm/presentation/quotation_detail_page.dart';
import 'package:elinkup_app/features/platform/data/edition_service.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

class _SalEditionService extends EditionService {
  @override
  Future<EditionSummary> tenantEdition() async => EditionSummary(
        id: 'test-edition',
        code: 'PROFESSIONAL',
        name: 'Professional',
        status: 'PUBLISHED',
        versionNo: 1,
        features: [
          {'feature_code': CrmFeatures.salQuote, 'is_enabled': true, 'is_visible': true},
        ],
      );
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

AuthController _salesAuth() {
  final auth = AuthController();
  auth.booting = false;
  auth.isAuthenticated = true;
  auth.profile = {
    'role_code': 'SALES_MANAGER',
    'permissions': [
      'quotation.read',
      'quotation.create',
      'quotation.update',
      'quotation.submit',
      'quotation.approve',
    ],
  };
  return auth;
}

class _StubQuotationService extends QuotationService {
  _StubQuotationService(this.quote);

  final Quotation quote;

  @override
  Future<Quotation> getById(String id) async => quote;

  @override
  Future<List<QuotationStatusEntry>> getHistory(String id) async => [];
}

void main() {
  test('Quotation.fromJson parses linked sales order fields', () {
    final q = Quotation.fromJson({
      'quotation_id': 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
      'quotation_number': 'QUO-2026-000001',
      'customer_id': 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22',
      'opportunity_id': null,
      'status': 'ACCEPTED',
      'currency_code': 'INR',
      'subtotal': '1000.00',
      'discount_total': '0.00',
      'tax_total': '180.00',
      'grand_total': '1180.00',
      'sales_order_id': 'c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33',
      'so_number': 'SO-2026-000001',
    });
    expect(q.salesOrderId, 'c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33');
    expect(q.soNumber, 'SO-2026-000001');
  });

  testWidgets('Accepted quotation without SO shows convert button', (tester) async {
    final service = _StubQuotationService(
      Quotation(
        quotationId: 'q1',
        quotationNumber: 'QUO-2026-000099',
        status: 'ACCEPTED',
        currencyCode: 'INR',
        subtotal: '100',
        discountTotal: '0',
        taxTotal: '18',
        grandTotal: '118',
      ),
    );
    await tester.pumpWidget(
      MaterialApp(
        home: QuotationDetailPage(quotationId: 'q1', service: service),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('convert-to-so')), findsOneWidget);
    expect(find.byKey(const Key('view-sales-order')), findsNothing);
  });

  testWidgets('Accepted quotation with linked SO shows view button', (tester) async {
    final service = _StubQuotationService(
      Quotation(
        quotationId: 'q2',
        quotationNumber: 'QUO-2026-000100',
        status: 'ACCEPTED',
        currencyCode: 'INR',
        subtotal: '100',
        discountTotal: '0',
        taxTotal: '18',
        grandTotal: '118',
        salesOrderId: 'so1',
        soNumber: 'SO-2026-000001',
      ),
    );
    await tester.pumpWidget(
      MaterialApp(
        home: QuotationDetailPage(quotationId: 'q2', service: service),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('view-sales-order')), findsOneWidget);
    expect(find.textContaining('SO-2026-000001'), findsOneWidget);
    expect(find.byKey(const Key('convert-to-so')), findsNothing);
  });

  test('Quotation.fromJson parses list payload', () {
    final q = Quotation.fromJson({
      'quotation_id': 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
      'quotation_number': 'QUO-2026-000001',
      'customer_id': 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22',
      'opportunity_id': null,
      'status': 'DRAFT',
      'currency_code': 'INR',
      'subtotal': '1000.00',
      'discount_total': '0.00',
      'tax_total': '180.00',
      'grand_total': '1180.00',
    });
    expect(q.quotationNumber, 'QUO-2026-000001');
    expect(q.status, 'DRAFT');
    expect(q.grandTotal, '1180.00');
  });

  testWidgets('CrmStatusChip renders quotation status', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: Scaffold(body: CrmStatusChip(status: 'SENT'))),
    );
    expect(find.text('SENT'), findsOneWidget);
  });

  testWidgets('Tenant without SAL_QUOTE redirected from quotations', (tester) async {
    final auth = _salesAuth();
    final edition = EditionController();
    edition.loaded = true;
    final router = createAppRouter(auth, edition);
    router.go(CrmRoutes.quotations);
    await tester.pumpWidget(_app(router, auth, edition));
    await tester.pumpAndSettle();
    final uri = router.routerDelegate.currentConfiguration.uri;
    expect(uri.path, CrmRoutes.upgrade);
    expect(uri.queryParameters['feature'], CrmFeatures.salQuote);
  });

  testWidgets('Quotations new route opens form not detail', (tester) async {
    final auth = _salesAuth();
    final edition = EditionController(service: _SalEditionService());
    await edition.load();
    final router = createAppRouter(auth, edition);
    router.go(CrmRoutes.quotationsNew);
    await tester.pumpWidget(_app(router, auth, edition));
    await tester.pump();
    expect(router.routerDelegate.currentConfiguration.uri.path, CrmRoutes.quotationsNew);
    expect(find.text('New Quotation'), findsOneWidget);
  });
}
