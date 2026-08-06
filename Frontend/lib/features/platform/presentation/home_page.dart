import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/auth/auth_controller.dart';
import '../../crm/presentation/leads_page.dart';
import '../../crm/presentation/opportunities_page.dart';
import '../data/edition_service.dart';
import 'editions_page.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int _index = 0;

  static const _titles = [
    'E-LinkUp',
    'Editions',
    'CRM Leads',
    'Opportunities',
  ];

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthController>();
    final p = auth.profile ?? {};
    final wide = MediaQuery.sizeOf(context).width >= 900;
    final isPlatformAdmin = p['role_code'] == 'PLATFORM_ADMIN';

    final pages = <Widget>[
      _DashboardView(profile: p),
      if (isPlatformAdmin) const EditionsPage() else const _TenantEditionView(),
      const LeadsPage(),
      const OpportunitiesPage(),
    ];

    const destinations = [
      NavigationDestination(
        icon: Icon(Icons.dashboard_outlined),
        label: 'Dashboard',
      ),
      NavigationDestination(
        icon: Icon(Icons.layers_outlined),
        label: 'Editions',
      ),
      NavigationDestination(
        icon: Icon(Icons.people_outline),
        label: 'Leads',
      ),
      NavigationDestination(
        icon: Icon(Icons.trending_up_outlined),
        label: 'Pipeline',
      ),
    ];

    return Scaffold(
      appBar: AppBar(
        title: Text(_titles[_index.clamp(0, _titles.length - 1)]),
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
                  selectedIndex: _index,
                  onDestinationSelected: (i) => setState(() => _index = i),
                  labelType: NavigationRailLabelType.all,
                  destinations: const [
                    NavigationRailDestination(
                      icon: Icon(Icons.dashboard_outlined),
                      selectedIcon: Icon(Icons.dashboard),
                      label: Text('Dashboard'),
                    ),
                    NavigationRailDestination(
                      icon: Icon(Icons.layers_outlined),
                      selectedIcon: Icon(Icons.layers),
                      label: Text('Editions'),
                    ),
                    NavigationRailDestination(
                      icon: Icon(Icons.people_outline),
                      selectedIcon: Icon(Icons.people),
                      label: Text('Leads'),
                    ),
                    NavigationRailDestination(
                      icon: Icon(Icons.trending_up_outlined),
                      selectedIcon: Icon(Icons.trending_up),
                      label: Text('Pipeline'),
                    ),
                  ],
                ),
                const VerticalDivider(width: 1),
                Expanded(child: pages[_index]),
              ],
            )
          : pages[_index],
      bottomNavigationBar: wide
          ? null
          : NavigationBar(
              selectedIndex: _index,
              onDestinationSelected: (i) => setState(() => _index = i),
              destinations: destinations,
            ),
    );
  }
}

class _DashboardView extends StatelessWidget {
  const _DashboardView({required this.profile});

  final Map<String, dynamic> profile;

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
        const Text(
          'PF-001 Edition Management is available from the Editions tab.',
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
