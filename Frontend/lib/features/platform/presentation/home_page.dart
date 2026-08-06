import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/auth/auth_controller.dart';
import '../../crm/presentation/leads_page.dart';
import '../../crm/presentation/opportunities_page.dart';
import '../data/edition_service.dart';
import 'editions_page.dart';
import 'subscriptions_page.dart';
import 'tenants_page.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int _index = 0;

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthController>();
    final p = auth.profile ?? {};
    final wide = MediaQuery.sizeOf(context).width >= 900;
    final isPlatformAdmin = p['role_code'] == 'PLATFORM_ADMIN';

    final titles = <String>[
      'E-LinkUp',
      if (isPlatformAdmin) 'Tenants',
      if (isPlatformAdmin) 'Subscriptions',
      'Editions',
      'CRM Leads',
      'Opportunities',
    ];

    final pages = <Widget>[
      _DashboardView(profile: p, isPlatformAdmin: isPlatformAdmin),
      if (isPlatformAdmin) const TenantsPage(),
      if (isPlatformAdmin) const SubscriptionsPage(),
      if (isPlatformAdmin) const EditionsPage() else const _TenantEditionView(),
      const LeadsPage(),
      const OpportunitiesPage(),
    ];

    final destinations = <NavigationDestination>[
      const NavigationDestination(
        icon: Icon(Icons.dashboard_outlined),
        label: 'Dashboard',
      ),
      if (isPlatformAdmin)
        const NavigationDestination(
          icon: Icon(Icons.apartment_outlined),
          label: 'Tenants',
        ),
      if (isPlatformAdmin)
        const NavigationDestination(
          icon: Icon(Icons.card_membership_outlined),
          label: 'Subscriptions',
        ),
      const NavigationDestination(
        icon: Icon(Icons.layers_outlined),
        label: 'Editions',
      ),
      const NavigationDestination(
        icon: Icon(Icons.people_outline),
        label: 'Leads',
      ),
      const NavigationDestination(
        icon: Icon(Icons.trending_up_outlined),
        label: 'Pipeline',
      ),
    ];

    final railDestinations = <NavigationRailDestination>[
      const NavigationRailDestination(
        icon: Icon(Icons.dashboard_outlined),
        selectedIcon: Icon(Icons.dashboard),
        label: Text('Dashboard'),
      ),
      if (isPlatformAdmin)
        const NavigationRailDestination(
          icon: Icon(Icons.apartment_outlined),
          selectedIcon: Icon(Icons.apartment),
          label: Text('Tenants'),
        ),
      if (isPlatformAdmin)
        const NavigationRailDestination(
          icon: Icon(Icons.card_membership_outlined),
          selectedIcon: Icon(Icons.card_membership),
          label: Text('Subscriptions'),
        ),
      const NavigationRailDestination(
        icon: Icon(Icons.layers_outlined),
        selectedIcon: Icon(Icons.layers),
        label: Text('Editions'),
      ),
      const NavigationRailDestination(
        icon: Icon(Icons.people_outline),
        selectedIcon: Icon(Icons.people),
        label: Text('Leads'),
      ),
      const NavigationRailDestination(
        icon: Icon(Icons.trending_up_outlined),
        selectedIcon: Icon(Icons.trending_up),
        label: Text('Pipeline'),
      ),
    ];

    final safeIndex = _index.clamp(0, pages.length - 1);

    return Scaffold(
      appBar: AppBar(
        title: Text(titles[safeIndex]),
        actions: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8),
            child: Center(
              child: Text(
                '${p['tenant_name'] ?? ''} · ${p['display_name'] ?? ''}',
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ),
          ),
          IconButton(
            tooltip: 'Sign out',
            onPressed: () => auth.logout(),
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: wide
          ? Row(
              children: [
                NavigationRail(
                  selectedIndex: safeIndex,
                  onDestinationSelected: (i) => setState(() => _index = i),
                  labelType: NavigationRailLabelType.all,
                  destinations: railDestinations,
                ),
                const VerticalDivider(width: 1),
                Expanded(child: pages[safeIndex]),
              ],
            )
          : pages[safeIndex],
      bottomNavigationBar: wide
          ? null
          : NavigationBar(
              selectedIndex: safeIndex,
              onDestinationSelected: (i) => setState(() => _index = i),
              destinations: destinations,
            ),
    );
  }
}

class _DashboardView extends StatelessWidget {
  const _DashboardView({
    required this.profile,
    required this.isPlatformAdmin,
  });

  final Map<String, dynamic> profile;
  final bool isPlatformAdmin;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(24),
      children: [
        Text(
          'Welcome, ${profile['display_name'] ?? ''}',
          style: Theme.of(context).textTheme.headlineSmall,
        ),
        const SizedBox(height: 8),
        Text(
          isPlatformAdmin
              ? 'PF-003 Subscriptions, PF-002 Tenants, and PF-001 Editions are available from the nav.'
              : 'Your edition details are available from the Editions tab.',
        ),
        const SizedBox(height: 24),
        _infoTile(
          'Tenant',
          '${profile['tenant_name']} (${profile['tenant_code']})',
        ),
        _infoTile('Role', '${profile['role_name']} (${profile['role_code']})'),
        _infoTile('Organization', '${profile['organization_name']}'),
        _infoTile('Currency', '${profile['currency_code']}'),
        _infoTile('Timezone', '${profile['time_zone']}'),
        _infoTile('FY start', '${profile['financial_year_start']}'),
      ],
    );
  }

  Widget _infoTile(String label, String value) {
    return ListTile(
      dense: true,
      title: Text(label),
      subtitle: Text(value),
    );
  }
}

class _TenantEditionView extends StatefulWidget {
  const _TenantEditionView();

  @override
  State<_TenantEditionView> createState() => _TenantEditionViewState();
}

class _TenantEditionViewState extends State<_TenantEditionView> {
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
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final e = await _service.tenantEdition();
      if (!mounted) return;
      setState(() {
        _edition = e;
        _loading = false;
      });
    } catch (err) {
      if (!mounted) return;
      setState(() {
        _error = err.toString().replaceFirst('Exception: ', '');
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_error != null) {
      return Center(child: Text(_error!));
    }
    final e = _edition!;
    return ListView(
      padding: const EdgeInsets.all(24),
      children: [
        Text('Your edition', style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 8),
        Text('${e.code} — ${e.name}'),
        Text('Status: ${e.status}'),
        const SizedBox(height: 16),
        Text('Features', style: Theme.of(context).textTheme.titleSmall),
        ...e.features.map((f) => Text('• ${f['feature_code']}')),
      ],
    );
  }
}
