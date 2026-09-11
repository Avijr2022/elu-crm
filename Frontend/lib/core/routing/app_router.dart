import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../auth/auth_controller.dart';
import '../auth/crm_rbac.dart';
import '../edition/crm_features.dart';
import '../edition/edition_controller.dart';
import '../../features/crm/presentation/pipeline_kanban_page.dart';
import '../../features/crm/presentation/activity_outcomes_page.dart';
import '../../features/crm/presentation/activity_types_page.dart';
import '../../features/crm/presentation/activity_timeline_page.dart';
import '../../features/crm/presentation/crm_dashboard_view.dart';
import '../../features/crm/presentation/customer_detail_page.dart';
import '../../features/crm/presentation/customer_form_page.dart';
import '../../features/crm/presentation/customers_page.dart';
import '../../features/crm/presentation/l2c_demo_journey_page.dart';
import '../../features/crm/presentation/lead_detail_page.dart';
import '../../features/crm/presentation/lead_form_page.dart';
import '../../features/crm/presentation/leads_page.dart';
import '../../features/crm/presentation/opportunities_page.dart';
import '../../features/crm/presentation/opportunity_detail_page.dart';
import '../../features/crm/presentation/opportunity_form_page.dart';
import '../../features/crm/presentation/opportunity_stages_page.dart';
import '../../features/crm/presentation/payment_receipt_detail_page.dart';
import '../../features/crm/presentation/payment_receipts_page.dart';
import '../../features/crm/presentation/invoice_detail_page.dart';
import '../../features/crm/presentation/invoices_page.dart';
import '../../features/crm/presentation/quotation_form_page.dart';
import '../../features/crm/presentation/quotation_detail_page.dart';
import '../../features/crm/presentation/quotations_page.dart';
import '../../features/crm/presentation/sales_order_detail_page.dart';
import '../../features/crm/presentation/sales_orders_page.dart';
import '../../features/crm/presentation/work_order_detail_page.dart';
import '../../features/crm/presentation/work_orders_page.dart';
import '../../features/crm/presentation/upgrade_required_page.dart';
import '../../features/platform/presentation/app_shell.dart';
import '../../features/platform/presentation/editions_page.dart';
import '../../features/platform/presentation/login_page.dart';
import '../../features/platform/presentation/organizations_page.dart';
import '../../features/platform/presentation/subscriptions_page.dart';
import '../../features/platform/presentation/tenant_branding_page.dart';
import '../../features/platform/presentation/tenants_page.dart';
import 'crm_routes.dart';

bool _isL2cDemoPath(String path) => path.startsWith(CrmRoutes.l2cDemo);

bool _isOppPath(String path) =>
    path.startsWith(CrmRoutes.opportunities) ||
    path.contains('/crm/opportunities/');

bool _isCustomerPath(String path) =>
    path.startsWith(CrmRoutes.customers) || path.contains('/crm/customers/');

bool _isLeadPath(String path) =>
    path.startsWith(CrmRoutes.leads) || path.contains('/crm/leads/');

bool _isQuotationPath(String path) =>
    path.startsWith(CrmRoutes.quotations) || path.contains('/crm/quotations/');

bool _isSalesOrderPath(String path) =>
    path.startsWith(CrmRoutes.salesOrders) ||
    path.contains('/crm/sales-orders/');

bool _isWorkOrderPath(String path) =>
    path.startsWith(CrmRoutes.workOrders) || path.contains('/crm/work-orders/');

bool _isActivityPath(String path) =>
    path.startsWith(CrmRoutes.activityTimeline);

GoRouter createAppRouter(AuthController auth, EditionController edition) {
  bool isAdmin() => auth.profile?['role_code'] == 'PLATFORM_ADMIN';

  return GoRouter(
    initialLocation: CrmRoutes.home,
    refreshListenable: Listenable.merge([auth, edition]),
    redirect: (context, state) {
      if (auth.booting) return null;
      final onLogin = state.matchedLocation == CrmRoutes.login;
      if (!auth.isAuthenticated) return onLogin ? null : CrmRoutes.login;
      if (onLogin) return CrmRoutes.home;
      if (edition.loaded &&
          !edition.hasOpportunity &&
          !isAdmin() &&
          _isOppPath(state.matchedLocation)) {
        return '${CrmRoutes.upgrade}?feature=${CrmFeatures.opportunity}';
      }
      if (edition.loaded &&
          !edition.hasCustomer &&
          !isAdmin() &&
          _isCustomerPath(state.matchedLocation)) {
        return '${CrmRoutes.upgrade}?feature=${CrmFeatures.customer}';
      }
      if (edition.loaded &&
          !edition.hasLead &&
          !isAdmin() &&
          (_isLeadPath(state.matchedLocation) ||
              _isL2cDemoPath(state.matchedLocation))) {
        return '${CrmRoutes.upgrade}?feature=${CrmFeatures.lead}';
      }
      if (edition.loaded &&
          !edition.hasActivity &&
          !isAdmin() &&
          _isActivityPath(state.matchedLocation)) {
        return '${CrmRoutes.upgrade}?feature=${CrmFeatures.activity}';
      }
      if (edition.loaded &&
          !edition.hasSalQuote &&
          !isAdmin() &&
          _isQuotationPath(state.matchedLocation)) {
        return '${CrmRoutes.upgrade}?feature=${CrmFeatures.salQuote}';
      }
      if (edition.loaded &&
          !edition.hasSalQuote &&
          !isAdmin() &&
          _isSalesOrderPath(state.matchedLocation)) {
        return '${CrmRoutes.upgrade}?feature=${CrmFeatures.salQuote}';
      }
      if (edition.loaded &&
          !edition.hasPrjWo &&
          !isAdmin() &&
          _isWorkOrderPath(state.matchedLocation)) {
        return '${CrmRoutes.upgrade}?feature=${CrmFeatures.prjWo}';
      }
      if (state.matchedLocation == CrmRoutes.pipeline &&
          !CrmRbac.canViewPipeline(auth.profile)) {
        return CrmRoutes.home;
      }
      if (state.matchedLocation == CrmRoutes.organizations &&
          !CrmRbac.canManageOrganizations(auth.profile)) {
        return CrmRoutes.home;
      }
      return null;
    },
    routes: [
      GoRoute(path: CrmRoutes.login, builder: (_, __) => const LoginPage()),
      GoRoute(
          path: CrmRoutes.upgrade,
          builder: (_, s) => UpgradeRequiredPage(
              featureCode: s.uri.queryParameters['feature'])),
      ShellRoute(
        builder: (_, state, child) =>
            AppShell(location: state.uri.path, child: child),
        routes: [
          GoRoute(
            path: CrmRoutes.home,
            builder: (c, _) {
              final p = c.read<AuthController>().profile ?? {};
              return CrmDashboardView(profile: p);
            },
          ),
          GoRoute(path: '/tenants', builder: (_, __) => const TenantsPage()),
          GoRoute(
              path: CrmRoutes.organizations,
              builder: (_, __) => const OrganizationsPage()),
          GoRoute(
            path: '/subscriptions',
            builder: (c, _) => isAdmin()
                ? const SubscriptionsPage()
                : const MySubscriptionPage(),
          ),
          GoRoute(
            path: '/editions',
            builder: (c, _) =>
                isAdmin() ? const EditionsPage() : const TenantEditionView(),
          ),
          GoRoute(path: CrmRoutes.leads, builder: (_, __) => const LeadsPage()),
          GoRoute(
              path: CrmRoutes.opportunities,
              builder: (_, __) => const OpportunitiesPage()),
          GoRoute(
              path: CrmRoutes.pipeline,
              builder: (_, __) => const PipelineKanbanPage()),
          GoRoute(
              path: CrmRoutes.customers,
              builder: (_, __) => const CustomersPage()),
          GoRoute(
              path: CrmRoutes.quotations,
              builder: (_, __) => const QuotationsPage()),
          GoRoute(
              path: CrmRoutes.salesOrders,
              builder: (_, s) => SalesOrdersPage(
                    opportunityId: s.uri.queryParameters['opportunity_id'],
                    customerId: s.uri.queryParameters['customer_id'],
                    status: s.uri.queryParameters['status'],
                  )),
          GoRoute(
              path: CrmRoutes.paymentReceipts,
              builder: (_, __) => const PaymentReceiptsPage()),
          GoRoute(
              path: CrmRoutes.invoices,
              builder: (_, __) => const InvoicesPage()),
          GoRoute(
              path: CrmRoutes.workOrders,
              builder: (_, __) => const WorkOrdersPage()),
          GoRoute(
              path: CrmRoutes.l2cDemo,
              builder: (_, __) => const L2cDemoJourneyPage()),
        ],
      ),
      GoRoute(
        path: '/crm/customers/:id',
        builder: (_, s) =>
            CustomerDetailPage(customerId: s.pathParameters['id']!),
      ),
      GoRoute(
          path: CrmRoutes.leadsNew, builder: (_, __) => const LeadFormPage()),
      GoRoute(
          path: '/crm/leads/:id/edit',
          builder: (_, s) => LeadFormPage(leadId: s.pathParameters['id'])),
      GoRoute(
          path: '/crm/leads/:id',
          builder: (_, s) => LeadDetailPage(leadId: s.pathParameters['id']!)),
      GoRoute(
          path: CrmRoutes.opportunitiesNew,
          builder: (_, __) => const OpportunityFormPage()),
      GoRoute(
          path: '/crm/opportunities/:id/edit',
          builder: (_, s) =>
              OpportunityFormPage(opportunityId: s.pathParameters['id'])),
      GoRoute(
          path: '/crm/opportunities/:id',
          builder: (_, s) =>
              OpportunityDetailPage(opportunityId: s.pathParameters['id']!)),
      GoRoute(
          path: CrmRoutes.customersNew,
          builder: (_, __) => const CustomerFormPage()),
      GoRoute(
          path: CrmRoutes.quotationsNew,
          builder: (_, __) => const QuotationFormPage()),
      GoRoute(
        path: '/crm/quotations/:id',
        builder: (_, s) =>
            QuotationDetailPage(quotationId: s.pathParameters['id']!),
      ),
      GoRoute(
        path: '/crm/sales-orders/:id',
        builder: (_, s) =>
            SalesOrderDetailPage(salesOrderId: s.pathParameters['id']!),
      ),
      GoRoute(
        path: '/crm/work-orders/:id',
        builder: (_, s) =>
            WorkOrderDetailPage(workOrderId: s.pathParameters['id']!),
      ),
      GoRoute(
          path: CrmRoutes.activityTimeline,
          builder: (_, __) => const ActivityTimelinePage()),
      GoRoute(
          path: CrmRoutes.opportunityStages,
          builder: (_, __) => const OpportunityStagesPage()),
      GoRoute(
          path: CrmRoutes.activityTypes,
          builder: (_, __) => const ActivityTypesPage()),
      GoRoute(
          path: CrmRoutes.activityOutcomes,
          builder: (_, __) => const ActivityOutcomesPage()),
      GoRoute(
        path: '/crm/payment-receipts/:id',
        builder: (_, s) => PaymentReceiptDetailPage(
          paymentReceiptId: s.pathParameters['id']!,
        ),
      ),
      GoRoute(
        path: '/crm/invoices/:id',
        builder: (_, s) => InvoiceDetailPage(
          invoiceId: s.pathParameters['id']!,
        ),
      ),
      GoRoute(
          path: CrmRoutes.tenantBranding,
          builder: (_, __) => const TenantBrandingPage()),
    ],
    errorBuilder: (_, __) =>
        const Scaffold(body: Center(child: Text('Page not found'))),
  );
}
