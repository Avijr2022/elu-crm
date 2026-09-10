import 'package:flutter/material.dart';

import '../data/subscription_service.dart';

/// Subscription List / Create / Edit / View / Search / Renew / Upgrade / History
/// (ELU-BFS-PF-003 §11)
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

  Future<void> _create() async {
    final tenantCtrl = TextEditingController();
    final editionCtrl = TextEditingController(text: 'PROFESSIONAL');
    final seatsCtrl = TextEditingController(text: '10');
    final startCtrl = TextEditingController(
      text: DateTime.now().toIso8601String().substring(0, 10),
    );
    final endCtrl = TextEditingController(
      text: DateTime.now()
          .add(const Duration(days: 365))
          .toIso8601String()
          .substring(0, 10),
    );
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Create subscription'),
        content: SizedBox(
          width: 420,
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: tenantCtrl,
                  decoration: const InputDecoration(labelText: 'Tenant code'),
                ),
                TextField(
                  controller: editionCtrl,
                  decoration: const InputDecoration(labelText: 'Edition code'),
                ),
                TextField(
                  controller: seatsCtrl,
                  decoration: const InputDecoration(labelText: 'Seat count'),
                  keyboardType: TextInputType.number,
                ),
                TextField(
                  controller: startCtrl,
                  decoration:
                      const InputDecoration(labelText: 'Start date (YYYY-MM-DD)'),
                ),
                TextField(
                  controller: endCtrl,
                  decoration:
                      const InputDecoration(labelText: 'End date (YYYY-MM-DD)'),
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
            child: const Text('Create'),
          ),
        ],
      ),
    );
    if (ok != true) return;
    try {
      await _service.create(
        tenantCode: tenantCtrl.text.trim(),
        editionCode: editionCtrl.text.trim(),
        seatCount: int.parse(seatsCtrl.text.trim()),
        startDate: startCtrl.text.trim(),
        endDate: endCtrl.text.trim(),
      );
      if (!mounted) return;
      await _load();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  Future<void> _edit(SubscriptionSummary item) async {
    final seatsCtrl = TextEditingController(text: '${item.seatCount}');
    final endCtrl = TextEditingController(text: item.endDate ?? '');
    final cycleCtrl = TextEditingController(text: item.billingCycle ?? 'MONTHLY');
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text('Edit ${item.subscriptionNumber}'),
        content: SizedBox(
          width: 420,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: seatsCtrl,
                decoration: const InputDecoration(labelText: 'Seat count'),
                keyboardType: TextInputType.number,
              ),
              TextField(
                controller: endCtrl,
                decoration:
                    const InputDecoration(labelText: 'End date (YYYY-MM-DD)'),
              ),
              TextField(
                controller: cycleCtrl,
                decoration: const InputDecoration(
                  labelText: 'Billing cycle (MONTHLY/ANNUAL/QUARTERLY)',
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Save'),
          ),
        ],
      ),
    );
    if (ok != true) return;
    try {
      await _service.update(
        id: item.id,
        versionNo: item.versionNo,
        seatCount: int.parse(seatsCtrl.text.trim()),
        endDate: endCtrl.text.trim().isEmpty ? null : endCtrl.text.trim(),
        billingCycle: cycleCtrl.text.trim(),
      );
      if (!mounted) return;
      await _load();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  Future<void> _history(SubscriptionSummary item) async {
    try {
      final rows = await _service.history(item.id);
      if (!mounted) return;
      await showDialog<void>(
        context: context,
        builder: (ctx) => AlertDialog(
          title: Text('History — ${item.subscriptionNumber}'),
          content: SizedBox(
            width: 480,
            child: rows.isEmpty
                ? const Text('No history')
                : ListView.builder(
                    shrinkWrap: true,
                    itemCount: rows.length,
                    itemBuilder: (_, i) {
                      final h = rows[i];
                      return ListTile(
                        dense: true,
                        title: Text(h.changeType),
                        subtitle: Text(
                          '${h.fromStatus ?? '-'} → ${h.toStatus ?? '-'}'
                          '${h.reason != null ? '\n${h.reason}' : ''}',
                        ),
                        trailing: Text(
                          h.changedOn.length >= 10
                              ? h.changedOn.substring(0, 10)
                              : h.changedOn,
                          style: Theme.of(ctx).textTheme.bodySmall,
                        ),
                      );
                    },
                  ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Close'),
            ),
          ],
        ),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
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
            Text('Start: ${item.startDate ?? '-'}'),
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
      text: DateTime.now()
          .add(const Duration(days: 365))
          .toIso8601String()
          .substring(0, 10),
    );
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Renew subscription'),
        content: TextField(
          controller: endCtrl,
          decoration:
              const InputDecoration(labelText: 'New end date (YYYY-MM-DD)'),
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
          child: LayoutBuilder(
            builder: (context, constraints) {
              final narrow = constraints.maxWidth < 720;
              final filters = Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _searchCtrl,
                      decoration: const InputDecoration(
                        hintText: 'Search number / tenant',
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
                      DropdownMenuItem(
                        value: 'EXPIRED',
                        child: Text('Expired'),
                      ),
                    ],
                    onChanged: (v) {
                      setState(() => _statusFilter = v);
                      _load();
                    },
                  ),
                  const SizedBox(width: 8),
                  FilledButton.icon(
                    onPressed: _create,
                    icon: const Icon(Icons.add),
                    label: const Text('Create'),
                  ),
                ],
              );
              if (!narrow) return filters;
              return Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  TextField(
                    controller: _searchCtrl,
                    decoration: const InputDecoration(
                      hintText: 'Search number / tenant',
                      prefixIcon: Icon(Icons.search),
                    ),
                    onSubmitted: (_) => _load(),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      DropdownButton<String?>(
                        value: _statusFilter,
                        hint: const Text('Status'),
                        items: const [
                          DropdownMenuItem(value: null, child: Text('All')),
                          DropdownMenuItem(value: 'TRIAL', child: Text('Trial')),
                          DropdownMenuItem(
                            value: 'ACTIVE',
                            child: Text('Active'),
                          ),
                          DropdownMenuItem(
                            value: 'EXPIRED',
                            child: Text('Expired'),
                          ),
                        ],
                        onChanged: (v) {
                          setState(() => _statusFilter = v);
                          _load();
                        },
                      ),
                      FilledButton.icon(
                        onPressed: _create,
                        icon: const Icon(Icons.add),
                        label: const Text('Create'),
                      ),
                    ],
                  ),
                ],
              );
            },
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
                    '${s.tenantCode ?? '-'} · ${s.status} · ${s.editionCode} · '
                    'seats ${s.seatCountUsed}/${s.seatCount}',
                  ),
                  onTap: () => _view(s),
                  trailing: Wrap(
                    spacing: 0,
                    children: [
                      IconButton(
                        tooltip: 'History',
                        onPressed: () => _history(s),
                        icon: const Icon(Icons.history),
                      ),
                      if (s.status == 'TRIAL' || s.status == 'ACTIVE')
                        IconButton(
                          tooltip: 'Edit',
                          onPressed: () => _edit(s),
                          icon: const Icon(Icons.edit_outlined),
                        ),
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

/// Tenant Admin — My Subscription (BFS §11)
class MySubscriptionPage extends StatefulWidget {
  const MySubscriptionPage({super.key});

  @override
  State<MySubscriptionPage> createState() => _MySubscriptionPageState();
}

class _MySubscriptionPageState extends State<MySubscriptionPage> {
  final _service = SubscriptionService();
  bool _loading = true;
  String? _error;
  SubscriptionSummary? _sub;

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
      final s = await _service.tenantCurrent();
      if (!mounted) return;
      setState(() {
        _sub = s;
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
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_error != null) {
      return Center(child: Text(_error!));
    }
    final s = _sub!;
    final used = s.seatCountUsed;
    final max = s.seatCount == 0 ? 1 : s.seatCount;
    return ListView(
      padding: const EdgeInsets.all(24),
      children: [
        Text('My subscription', style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 12),
        Text(s.subscriptionNumber),
        Text('Status: ${s.status}'),
        Text('Edition: ${s.editionCode}'),
        Text('Billing: ${s.billingCycle ?? '-'}'),
        Text('End: ${s.endDate ?? '-'}'),
        const SizedBox(height: 16),
        Text('Seat usage', style: Theme.of(context).textTheme.titleSmall),
        const SizedBox(height: 8),
        LinearProgressIndicator(value: (used / max).clamp(0.0, 1.0)),
        const SizedBox(height: 4),
        Text('$used / ${s.seatCount} seats'),
      ],
    );
  }
}
