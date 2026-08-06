import 'package:flutter/material.dart';

import '../data/subscription_service.dart';

/// Subscription List / Search / View / Activate / Renew / Upgrade (ELU-BFS-PF-003 §11)
class SubscriptionsPage extends StatefulWidget {
  const SubscriptionsPage({super.key});

  @override
  State<SubscriptionsPage> createState() => _SubscriptionsPageState();
}

class _SubscriptionsPageState extends State<SubscriptionsPage> {
  final _service = SubscriptionService();
  final _searchCtrl = TextEditingController();
  bool _loading = true;
  String? _error;
  List<SubscriptionSummary> _items = [];
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
      final items = await _service.list(
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

  Future<void> _view(SubscriptionSummary item) async {
    await showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(item.subscriptionNumber),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Tenant: ${item.tenantCode ?? '-'}'),
            Text('Status: ${item.status}'),
            Text('Edition: ${item.editionCode}'),
            Text('Seats: ${item.seatCountUsed}/${item.seatCount}'),
            Text('Billing: ${item.billingCycle ?? '-'}'),
            Text('End: ${item.endDate ?? '-'}'),
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

  Future<void> _activate(SubscriptionSummary item) async {
    try {
      await _service.activateTrial(item.id, item.versionNo);
      if (!mounted) return;
      await _load();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  Future<void> _renew(SubscriptionSummary item) async {
    final endCtrl = TextEditingController(
      text: DateTime.now().add(const Duration(days: 365)).toIso8601String().substring(0, 10),
    );
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Renew subscription'),
        content: TextField(
          controller: endCtrl,
          decoration: const InputDecoration(labelText: 'New end date (YYYY-MM-DD)'),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Renew'),
          ),
        ],
      ),
    );
    if (ok != true) return;
    try {
      await _service.renew(item.id, item.versionNo, endCtrl.text.trim());
      if (!mounted) return;
      await _load();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  Future<void> _upgrade(SubscriptionSummary item) async {
    final edCtrl = TextEditingController(text: 'ENTERPRISE');
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Upgrade edition'),
        content: TextField(
          controller: edCtrl,
          decoration: const InputDecoration(labelText: 'Edition code'),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Upgrade'),
          ),
        ],
      ),
    );
    if (ok != true) return;
    try {
      await _service.upgrade(item.id, item.versionNo, edCtrl.text.trim());
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
                    hintText: 'Search subscription number',
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
                  DropdownMenuItem(value: 'TRIAL', child: Text('Trial')),
                  DropdownMenuItem(value: 'ACTIVE', child: Text('Active')),
                  DropdownMenuItem(value: 'EXPIRED', child: Text('Expired')),
                ],
                onChanged: (v) {
                  setState(() => _statusFilter = v);
                  _load();
                },
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
                final s = _items[i];
                return ListTile(
                  title: Text(s.subscriptionNumber),
                  subtitle: Text(
                    '${s.status} · ${s.editionCode} · seats ${s.seatCountUsed}/${s.seatCount}',
                  ),
                  onTap: () => _view(s),
                  trailing: Wrap(
                    spacing: 4,
                    children: [
                      if (s.status == 'TRIAL')
                        TextButton(
                          onPressed: () => _activate(s),
                          child: const Text('Activate'),
                        ),
                      if (s.status == 'ACTIVE' || s.status == 'RENEWAL_PENDING')
                        TextButton(
                          onPressed: () => _renew(s),
                          child: const Text('Renew'),
                        ),
                      if (s.status == 'ACTIVE' || s.status == 'TRIAL')
                        TextButton(
                          onPressed: () => _upgrade(s),
                          child: const Text('Upgrade'),
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
