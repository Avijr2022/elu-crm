import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../../core/auth/auth_controller.dart';
import '../../../core/auth/crm_rbac.dart';
import '../../../core/edition/edition_controller.dart';
import '../../../core/routing/crm_routes.dart';
import '../../../core/theme/crm_theme.dart';
import '../data/edition_service.dart';

class AppShell extends StatefulWidget {
  const AppShell({super.key, required this.location, required this.child});

  final String location;
  final Widget child;

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  String _title(String path) {
    if (path == CrmRoutes.home) return 'E-LinkUp';
    if (path.startsWith(CrmRoutes.leads)) return 'Leads';
    if (path == CrmRoutes.pipeline) return 'Pipeline Kanban';
    if (path.startsWith(CrmRoutes.opportunities)) return 'Opportunities';
    if (path == CrmRoutes.customers) return 'Customers';
    if (path.startsWith(CrmRoutes.quotations)) return 'Quotations';
    if (path.startsWith(CrmRoutes.salesOrders)) return 'Sales Orders';
    if (path.startsWith(CrmRoutes.paymentReceipts)) return 'Payment Receipts';
    if (path.startsWith(CrmRoutes.invoices)) return 'Invoices';
    if (path.startsWith(CrmRoutes.workOrders)) return 'Work Orders';
    if (path == CrmRoutes.l2cDemo) return 'L2C Demo';
    if (path.contains('tenants')) return 'Tenants';
    if (path.contains('organizations')) return 'Organizations';
    if (path.contains('subscriptions')) return 'Subscriptions';
    if (path.contains('editions')) return 'Editions';
    return 'E-LinkUp';
  }

  int _selectedIndex(List<_NavItem> items, String path) {
    for (var i = 0; i < items.length; i++) {
      if (path == items[i].path ||
          (items[i].path != CrmRoutes.home && path.startsWith(items[i].path))) {
        return i;
      }
    }
    return 0;
  }

  List<_NavItem> _items(
      bool admin, EditionController edition, Map<String, dynamic>? profile) {
    return [
      const _NavItem(
          'dashboard', 'Dashboard', Icons.dashboard_outlined, CrmRoutes.home),
      if (admin)
        const _NavItem(
            'tenants', 'Tenants', Icons.apartment_outlined, '/tenants',
            section: 'Platform'),
      const _NavItem('organizations', 'Organizations',
          Icons.account_balance_outlined, '/organizations',
          section: 'Platform'),
      const _NavItem('subscriptions', 'Subscriptions',
          Icons.card_membership_outlined, '/subscriptions',
          section: 'Platform'),
      const _NavItem('editions', 'Editions', Icons.layers_outlined, '/editions',
          section: 'Platform'),
      if (edition.hasLead)
        const _NavItem(
            'l2c-demo', 'L2C Demo', Icons.route_outlined, CrmRoutes.l2cDemo,
            section: 'CRM'),
      if (edition.hasLead)
        const _NavItem('leads', 'Leads', Icons.people_outline, CrmRoutes.leads,
            section: 'CRM'),
      if (edition.hasOpportunity) ...[
        const _NavItem('opportunities', 'Opportunities',
            Icons.trending_up_outlined, CrmRoutes.opportunities,
            section: 'CRM'),
        if (CrmRbac.canViewPipeline(profile))
          const _NavItem('pipeline', 'Pipeline Kanban',
              Icons.view_kanban_outlined, CrmRoutes.pipeline,
              section: 'CRM'),
      ],
      if (edition.hasCustomer)
        const _NavItem('customers', 'Customers', Icons.business_center_outlined,
            CrmRoutes.customers,
            section: 'CRM'),
      if (edition.hasSalQuote) ...[
        const _NavItem('quotations', 'Quotations', Icons.request_quote_outlined,
            CrmRoutes.quotations,
            section: 'SAL'),
        const _NavItem('sales-orders', 'Sales Orders',
            Icons.receipt_long_outlined, CrmRoutes.salesOrders,
            section: 'SAL'),
        const _NavItem('payment-receipts', 'Payment Receipts',
            Icons.payments_outlined, CrmRoutes.paymentReceipts,
            section: 'FIN'),
      ],
      if (edition.hasFinInvoice)
        const _NavItem('invoices', 'Invoices', Icons.request_page_outlined,
            CrmRoutes.invoices,
            section: 'FIN'),
      if (edition.hasPrjWo)
        const _NavItem('work-orders', 'Work Orders', Icons.assignment_outlined,
            CrmRoutes.workOrders,
            section: 'PRJ'),
      if (edition.hasActivity)
        const _NavItem('activities', 'Activities', Icons.timeline_outlined,
            CrmRoutes.activityTimeline,
            section: 'CRM', push: true),
    ];
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthController>();
    final edition = context.watch<EditionController>();
    final p = auth.profile ?? {};
    final admin = p['role_code'] == 'PLATFORM_ADMIN';
    final wide = MediaQuery.sizeOf(context).width >= 900;
    final items = _items(admin, edition, auth.profile);
    final idx = _selectedIndex(items, widget.location);

    void go(_NavItem item) {
      if (item.push) {
        context.push(item.path);
      } else {
        context.go(item.path);
      }
      if (!wide) Navigator.of(context).maybePop();
    }

    final nav = _NavList(items: items, selected: idx, onTap: go);

    return Scaffold(
      appBar: AppBar(
        title: Text(_title(widget.location)),
        actions: [
          if (wide)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 8),
              child: Center(
                  child: Text('${p['tenant_name'] ?? ''}',
                      style: Theme.of(context).textTheme.bodySmall)),
            ),
          IconButton(
              tooltip: 'Sign out',
              onPressed: auth.logout,
              icon: const Icon(Icons.logout)),
        ],
      ),
      drawer: wide
          ? null
          : Drawer(
              child: Column(
                  children: [_ProfileCard(profile: p), Expanded(child: nav)])),
      body: wide
          ? Row(children: [
              SizedBox(
                width: 260,
                child: Material(
                  color: Theme.of(context).colorScheme.surfaceContainerLow,
                  child: Column(children: [
                    _ProfileCard(profile: p),
                    Expanded(child: nav)
                  ]),
                ),
              ),
              const VerticalDivider(width: 1),
              Expanded(child: widget.child),
            ])
          : widget.child,
      bottomNavigationBar: wide
          ? null
          : NavigationBar(
              selectedIndex: _mobileTab(items, idx),
              onDestinationSelected: (t) {
                const tabs = [
                  CrmRoutes.home,
                  CrmRoutes.leads,
                  CrmRoutes.opportunities
                ];
                final path = t < tabs.length ? tabs[t] : CrmRoutes.home;
                final item = items.cast<_NavItem?>().firstWhere(
                      (e) => e!.path == path,
                      orElse: () => items.first,
                    );
                if (item != null) go(item);
              },
              destinations: const [
                NavigationDestination(
                    icon: Icon(Icons.dashboard_outlined), label: 'Home'),
                NavigationDestination(
                    icon: Icon(Icons.people_outline), label: 'Leads'),
                NavigationDestination(
                    icon: Icon(Icons.trending_up_outlined), label: 'Pipeline'),
              ],
            ),
    );
  }

  int _mobileTab(List<_NavItem> items, int idx) {
    const order = [CrmRoutes.home, CrmRoutes.leads, CrmRoutes.opportunities];
    final path = idx < items.length ? items[idx].path : CrmRoutes.home;
    final i = order.indexOf(path);
    return i >= 0 ? i : 0;
  }
}

class _NavItem {
  const _NavItem(this.id, this.label, this.icon, this.path,
      {this.section, this.push = false});
  final String id;
  final String label;
  final IconData icon;
  final String path;
  final String? section;
  final bool push;
}

class _NavList extends StatelessWidget {
  const _NavList(
      {required this.items, required this.selected, required this.onTap});
  final List<_NavItem> items;
  final int selected;
  final void Function(_NavItem) onTap;

  @override
  Widget build(BuildContext context) {
    final children = <Widget>[];
    String? last;
    for (var i = 0; i < items.length; i++) {
      final e = items[i];
      if (e.section != null && e.section != last) {
        last = e.section;
        children.add(Padding(
          padding: const EdgeInsets.fromLTRB(
              CrmSpacing.md, CrmSpacing.sm, CrmSpacing.md, CrmSpacing.xs),
          child:
              Text(e.section!, style: Theme.of(context).textTheme.labelSmall),
        ));
      }
      children.add(ListTile(
        leading: Icon(e.icon),
        title: Text(e.label),
        selected: i == selected,
        onTap: () => onTap(e),
      ));
    }
    return ListView(
        padding: const EdgeInsets.symmetric(vertical: CrmSpacing.xs),
        children: children);
  }
}

class _ProfileCard extends StatelessWidget {
  const _ProfileCard({required this.profile});
  final Map<String, dynamic> profile;

  @override
  Widget build(BuildContext context) {
    final name = (profile['display_name'] as String?) ?? '';
    final initials = name.isEmpty
        ? '?'
        : name
            .trim()
            .split(RegExp(r'\s+'))
            .map((p) => p[0])
            .take(2)
            .join()
            .toUpperCase();
    return Container(
      padding: const EdgeInsets.all(CrmSpacing.md),
      child: Row(children: [
        CircleAvatar(child: Text(initials)),
        const SizedBox(width: CrmSpacing.sm),
        Expanded(
            child:
                Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(name, maxLines: 1, overflow: TextOverflow.ellipsis),
          Text('${profile['tenant_name'] ?? ''}',
              style: Theme.of(context).textTheme.bodySmall),
        ])),
      ]),
    );
  }
}

// Platform edition sub-view kept for tenant users
class TenantEditionView extends StatefulWidget {
  const TenantEditionView({super.key});
  @override
  State<TenantEditionView> createState() => _TenantEditionViewState();
}

class _TenantEditionViewState extends State<TenantEditionView> {
  final _service = EditionService();
  bool _loading = true;
  String? _error;
  EditionSummary? _edition;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final e = await _service.tenantEdition();
      if (!mounted) return;
      setState(() {
        _edition = e;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = '$e';
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Center(child: CircularProgressIndicator());
    if (_error != null) return Center(child: Text(_error!));
    final e = _edition!;
    return ListView(padding: const EdgeInsets.all(CrmSpacing.lg), children: [
      Text('${e.code} — ${e.name}'),
      ...e.features.map((f) => Text('• ${f['feature_code']}')),
    ]);
  }
}
