import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/routing/crm_routes.dart';
import '../../../core/theme/crm_theme.dart';
import '../data/invoice_service.dart';

class InvoicesPage extends StatefulWidget {
  const InvoicesPage({super.key});

  @override
  State<InvoicesPage> createState() => _InvoicesPageState();
}

class _InvoicesPageState extends State<InvoicesPage> {
  final _service = InvoiceService();
  bool _loading = true;
  String? _error;
  List<Invoice> _items = [];
  String _statusFilter = '';

  static const _statuses = ['', 'DRAFT', 'ISSUED', 'CANCELLED'];

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
      final r = await _service.list(status: _statusFilter);
      if (!mounted) return;
      setState(() {
        _items = r.items;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString().replaceFirst('Exception: ', '');
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(
            CrmSpacing.page,
            CrmSpacing.page,
            CrmSpacing.page,
            CrmSpacing.sm,
          ),
          child: Row(
            children: [
              DropdownButton<String>(
                value: _statusFilter,
                items: _statuses
                    .map((s) => DropdownMenuItem(
                          value: s,
                          child: Text(s.isEmpty ? 'All statuses' : s),
                        ))
                    .toList(),
                onChanged: (value) {
                  setState(() => _statusFilter = value ?? '');
                  _load();
                },
              ),
              const Spacer(),
              IconButton(
                tooltip: 'Refresh',
                onPressed: _loading ? null : _load,
                icon: const Icon(Icons.refresh),
              ),
            ],
          ),
        ),
        Expanded(child: _body()),
      ],
    );
  }

  Widget _body() {
    if (_loading && _items.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_error != null && _items.isEmpty) {
      return Center(child: Text(_error!));
    }
    return RefreshIndicator(
      onRefresh: _load,
      child: _items.isEmpty
          ? ListView(
              children: const [
                SizedBox(height: 120),
                Center(child: Text('No invoices')),
              ],
            )
          : ListView.separated(
              padding: const EdgeInsets.all(CrmSpacing.page),
              itemCount: _items.length,
              separatorBuilder: (_, __) =>
                  const SizedBox(height: CrmSpacing.sm),
              itemBuilder: (_, i) {
                final inv = _items[i];
                return Card(
                  child: ListTile(
                    title: Text(inv.invoiceNumber),
                    subtitle: Text(
                      [
                        inv.status,
                        if (inv.soNumber != null) inv.soNumber!,
                        if (inv.customerName != null) inv.customerName!,
                      ].join(' · '),
                    ),
                    trailing: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text('${inv.currencyCode} ${inv.grandTotal}'),
                        Text(
                          'Balance ${inv.balanceDue}',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                      ],
                    ),
                    onTap: () =>
                        context.push(CrmRoutes.invoiceDetail(inv.invoiceId)),
                  ),
                );
              },
            ),
    );
  }
}
