import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/auth/auth_controller.dart';
import '../../crm/presentation/leads_page.dart';

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

    final pages = [
      _DashboardView(profile: p),
      const LeadsPage(),
    ];

    const destinations = [
      NavigationDestination(icon: Icon(Icons.dashboard_outlined), label: 'Dashboard'),
      NavigationDestination(icon: Icon(Icons.people_outline), label: 'Leads'),
    ];

    return Scaffold(
      appBar: AppBar(
        title: Text(_index == 0 ? 'E-LinkUp' : 'CRM Leads'),
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
                      icon: Icon(Icons.people_outline),
                      selectedIcon: Icon(Icons.people),
                      label: Text('Leads'),
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
        const Text('Step 3 — CRM Lead module is available from the Leads tab.'),
        const SizedBox(height: 24),
        _infoTile('Tenant', '${profile['tenant_name']} (${profile['tenant_code']})'),
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
