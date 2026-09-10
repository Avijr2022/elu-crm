import 'package:flutter/material.dart';

import '../data/tenant_service.dart';

/// Tenant List / Register / View / Approve / Suspend / Reactivate (ELU-BFS-PF-002 §11)
class TenantsPage extends StatefulWidget {
  const TenantsPage({super.key});

  @override
  State<TenantsPage> createState() => _TenantsPageState();
}

class _TenantsPageState extends State<TenantsPage> {
  final _service = TenantService();
  final _searchCtrl = TextEditingController();
  bool _loading = true;
  String? _error;
  List<TenantSummary> _items = [];
  String? _statusFilter;

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

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final items = await _service.listTenants(
        status: _statusFilter,
        search: _searchCtrl.text,
      );
      if (!mounted) return;
      setState(() {
        _items = items;
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

  Future<void> _register() async {
    final codeCtrl = TextEditingController();
    final legalCtrl = TextEditingController();
    final tradeCtrl = TextEditingController();
    final editionCtrl = TextEditingController(text: 'PROFESSIONAL');
    final emailCtrl = TextEditingController();
    final mobileCtrl = TextEditingController();
    final contactNameCtrl = TextEditingController();
    final contactEmailCtrl = TextEditingController();
    final line1Ctrl = TextEditingController();
    final cityCtrl = TextEditingController();
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Register tenant'),
        content: SizedBox(
          width: 480,
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: codeCtrl,
                  decoration: const InputDecoration(
                    labelText: 'Code (lowercase alphanumeric)',
                  ),
                ),
                TextField(
                  controller: legalCtrl,
                  decoration: const InputDecoration(labelText: 'Legal name'),
                ),
                TextField(
                  controller: tradeCtrl,
                  decoration: const InputDecoration(labelText: 'Trade name'),
                ),
                TextField(
                  controller: editionCtrl,
                  decoration: const InputDecoration(labelText: 'Edition code'),
                ),
                TextField(
                  controller: emailCtrl,
                  decoration: const InputDecoration(labelText: 'Tenant email'),
                ),
                TextField(
                  controller: mobileCtrl,
                  decoration: const InputDecoration(labelText: 'Mobile'),
                ),
                TextField(
                  controller: contactNameCtrl,
                  decoration:
                      const InputDecoration(labelText: 'Primary contact name'),
                ),
                TextField(
                  controller: contactEmailCtrl,
                  decoration:
                      const InputDecoration(labelText: 'Primary contact email'),
                ),
                TextField(
                  controller: line1Ctrl,
                  decoration:
                      const InputDecoration(labelText: 'Registered address'),
                ),
                TextField(
                  controller: cityCtrl,
                  decoration: const InputDecoration(labelText: 'City'),
                ),
              ],
            ),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Register'),
          ),
        ],
      ),
    );
    if (ok != true) return;
    try {
      await _service.register(
        code: codeCtrl.text.trim(),
        legalName: legalCtrl.text.trim(),
        tradeName: tradeCtrl.text.trim(),
        editionCode: editionCtrl.text.trim(),
        email: emailCtrl.text.trim(),
        mobile: mobileCtrl.text.trim(),
        contactName: contactNameCtrl.text.trim(),
        contactEmail: contactEmailCtrl.text.trim(),
        addressLine1: line1Ctrl.text.trim(),
        city: cityCtrl.text.trim(),
      );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Tenant registered (PENDING_ACTIVATION)')),
      );
      await _load();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  Future<void> _view(TenantSummary item) async {
    final detail = await _service.getTenant(item.id);
    if (!mounted) return;
    await showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(detail.legalName),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Code: ${detail.code}'),
            Text('Status: ${detail.status}'),
            Text('Edition: ${detail.editionCode}'),
            Text('Email: ${detail.email ?? '-'}'),
            Text('Mobile: ${detail.mobile ?? '-'}'),
            Text('Version: ${detail.versionNo}'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  Future<void> _approve(TenantSummary item) async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Approve tenant'),
        content: Text('Activate ${item.code}?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Approve'),
          ),
        ],
      ),
    );
    if (ok != true) return;
    try {
      await _service.approve(item.id, item.versionNo);
      if (!mounted) return;
      await _load();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  Future<void> _suspend(TenantSummary item) async {
    final reasonCtrl = TextEditingController();
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Suspend tenant'),
        content: TextField(
          controller: reasonCtrl,
          decoration: const InputDecoration(labelText: 'Reason (required)'),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Suspend'),
          ),
        ],
      ),
    );
    if (ok != true) return;
    try {
      await _service.suspend(item.id, item.versionNo, reasonCtrl.text.trim());
      if (!mounted) return;
      await _load();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  Future<void> _reactivate(TenantSummary item) async {
    try {
      await _service.reactivate(item.id, item.versionNo);
      if (!mounted) return;
      await _load();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _searchCtrl,
                  decoration: const InputDecoration(
                    hintText: 'Search code / legal name',
                    prefixIcon: Icon(Icons.search),
                  ),
                  onSubmitted: (_) => _load(),
                ),
              ),
              const SizedBox(width: 8),
              DropdownButton<String?>(
                value: _statusFilter,
                hint: const Text('Status'),
                items: const [
                  DropdownMenuItem(value: null, child: Text('All')),
                  DropdownMenuItem(
                    value: 'PENDING_ACTIVATION',
                    child: Text('Pending'),
                  ),
                  DropdownMenuItem(value: 'ACTIVE', child: Text('Active')),
                  DropdownMenuItem(
                    value: 'SUSPENDED',
                    child: Text('Suspended'),
                  ),
                ],
                onChanged: (v) {
                  setState(() => _statusFilter = v);
                  _load();
                },
              ),
              const SizedBox(width: 8),
              FilledButton.icon(
                onPressed: _register,
                icon: const Icon(Icons.add),
                label: const Text('Register'),
              ),
            ],
          ),
        ),
        if (_loading)
          const Expanded(child: Center(child: CircularProgressIndicator()))
        else if (_error != null)
          Expanded(child: Center(child: Text(_error!)))
        else
          Expanded(
            child: ListView.separated(
              itemCount: _items.length,
              separatorBuilder: (_, __) => const Divider(height: 1),
              itemBuilder: (ctx, i) {
                final t = _items[i];
                return ListTile(
                  title: Text('${t.legalName} (${t.code})'),
                  subtitle: Text('${t.status} · ${t.editionCode}'),
                  onTap: () => _view(t),
                  trailing: Wrap(
                    spacing: 4,
                    children: [
                      if (t.status == 'PENDING_ACTIVATION')
                        TextButton(
                          onPressed: () => _approve(t),
                          child: const Text('Approve'),
                        ),
                      if (t.status == 'ACTIVE' || t.status == 'TRIAL')
                        TextButton(
                          onPressed: () => _suspend(t),
                          child: const Text('Suspend'),
                        ),
                      if (t.status == 'SUSPENDED')
                        TextButton(
                          onPressed: () => _reactivate(t),
                          child: const Text('Reactivate'),
                        ),
                    ],
                  ),
                );
              },
            ),
          ),
      ],
    );
  }
}
