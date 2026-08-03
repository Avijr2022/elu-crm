import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/auth/auth_controller.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthController>();
    final p = auth.profile ?? {};

    return Scaffold(
      appBar: AppBar(
        title: const Text('E-LinkUp'),
        actions: [
          IconButton(
            tooltip: 'Sign out',
            onPressed: () => auth.logout(),
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          Text(
            'Welcome, ${p['display_name'] ?? ''}',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 8),
          Text('Step 2 complete — Platform Foundation + Auth'),
          const SizedBox(height: 24),
          _infoTile('Tenant', '${p['tenant_name']} (${p['tenant_code']})'),
          _infoTile('Role', '${p['role_name']} (${p['role_code']})'),
          _infoTile('Organization', '${p['organization_name']}'),
          _infoTile('Currency', '${p['currency_code']}'),
          _infoTile('Timezone', '${p['time_zone']}'),
          _infoTile('FY start', '${p['financial_year_start']}'),
          const SizedBox(height: 24),
          Card(
            child: ListTile(
              leading: const Icon(Icons.construction),
              title: const Text('Next: CRM Lead module'),
              subtitle: const Text('REQ-CRM-001 — Step 3'),
              onTap: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Lead module comes in Step 3')),
                );
              },
            ),
          ),
        ],
      ),
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
