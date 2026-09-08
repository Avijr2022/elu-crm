import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../../core/auth/auth_controller.dart';
import '../../../core/auth/crm_rbac.dart';
import '../../../core/routing/crm_routes.dart';
import '../../../core/theme/crm_theme.dart';
import '../../../core/widgets/crm_search_field.dart';
import '../data/customer_service.dart';

class CustomersPage extends StatefulWidget {
  const CustomersPage({super.key});

  @override
  State<CustomersPage> createState() => _CustomersPageState();
}

class _CustomersPageState extends State<CustomersPage> {
  final _service = CustomerService();
  final _searchCtrl = TextEditingController();
  bool _loading = true;
  String? _error;
  List<Customer> _items = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _searchCtrl.dispose();
    super.dispose();
  }

  Future<void> _load({String? search}) async {
    setState(() { _loading = true; _error = null; });
    try {
      final r = await _service.list(search: search);
      if (!mounted) return;
      setState(() { _items = r.items; _loading = false; });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString().replaceFirst('Exception: ', '');
        _loading = false;
      });
    }
  }

  Future<void> _openCreate() async {
    final created = await context.push<bool>(CrmRoutes.customersNew);
    if (!mounted || created != true) return;
    await _load();
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Customer created')),
    );
  }

  @override
  Widget build(BuildContext context) {
    final canCreate = CrmRbac.canCreateCustomer(
      context.watch<AuthController>().profile,
    );
    if (_loading && _items.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_error != null && _items.isEmpty) {
      return Center(child: Column(mainAxisSize: MainAxisSize.min, children: [
        Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
        TextButton(onPressed: () => _load(), child: const Text('Retry')),
      ]));
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(
            CrmSpacing.page, CrmSpacing.page, CrmSpacing.page, 0,
          ),
          child: Row(
            children: [
              Expanded(
                child: CrmSearchField(
                  controller: _searchCtrl,
                  hintText: 'Search name or number',
                  onSearch: () => _load(search: _searchCtrl.text.trim()),
                ),
              ),
              if (canCreate) ...[
                const SizedBox(width: CrmSpacing.sm),
                FilledButton.icon(
                  onPressed: _openCreate,
                  icon: const Icon(Icons.add),
                  label: const Text('New'),
                ),
              ],
            ],
          ),
        ),
        Expanded(
          child: _items.isEmpty
              ? const Center(child: Text('No customers found'))
              : RefreshIndicator(
                  onRefresh: () => _load(search: _searchCtrl.text.trim()),
                  child: ListView.separated(
                    padding: const EdgeInsets.all(CrmSpacing.page),
                    itemCount: _items.length,
                    separatorBuilder: (_, __) => const SizedBox(height: CrmSpacing.sm),
                    itemBuilder: (_, i) {
                      final c = _items[i];
                      return Card(
                        child: ListTile(
                          title: Text(c.legalName),
                          subtitle: Text('${c.customerNumber} · ${c.status}'),
                          onTap: () => context.push(CrmRoutes.customerDetail(c.customerId)),
                        ),
                      );
                    },
                  ),
                ),
        ),
      ],
    );
  }
}
