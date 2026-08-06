import 'package:flutter/material.dart';

import '../data/organization_service.dart';

/// Organization List / Create / View / Edit / Hierarchy / History (ELU-BFS-PF-004 §11)
class OrganizationsPage extends StatefulWidget {
  const OrganizationsPage({super.key});

  @override
  State<OrganizationsPage> createState() => _OrganizationsPageState();
}

class _OrganizationsPageState extends State<OrganizationsPage> {
  final _service = OrganizationService();
  final _searchCtrl = TextEditingController();
  bool _loading = true;
  String? _error;
  List<OrganizationSummary> _items = [];

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
      final items = await _service.list(search: _searchCtrl.text);
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

  void _snack(String msg) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
  }

  Future<void> _create() async {
    OrganizationSummary? root;
    try {
      root = await _service.getRoot();
    } catch (e) {
      _snack(e.toString().replaceFirst('Exception: ', ''));
      return;
    }
    if (!mounted) return;
    final codeCtrl = TextEditingController();
    final nameCtrl = TextEditingController();
    final legalCtrl = TextEditingController();
    final typeCtrl = TextEditingController(text: 'Branch');
    final gstinCtrl = TextEditingController();
    final panCtrl = TextEditingController();
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Create child organization'),
        content: SizedBox(
          width: 480,
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Parent: ${root!.code} · ${root.name}',
                  style: Theme.of(ctx).textTheme.bodySmall,
                ),
                const SizedBox(height: 8),
                TextField(
                  controller: codeCtrl,
                  decoration: const InputDecoration(labelText: 'Code *'),
                  textCapitalization: TextCapitalization.characters,
                ),
                TextField(
                  controller: nameCtrl,
                  decoration: const InputDecoration(labelText: 'Name *'),
                ),
                TextField(
                  controller: legalCtrl,
                  decoration: const InputDecoration(labelText: 'Legal name'),
                ),
                TextField(
                  controller: typeCtrl,
                  decoration: const InputDecoration(labelText: 'Type'),
                ),
                TextField(
                  controller: gstinCtrl,
                  decoration: const InputDecoration(labelText: 'GSTIN'),
                ),
                TextField(
                  controller: panCtrl,
                  decoration: const InputDecoration(labelText: 'PAN'),
                ),
              ],
            ),
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Create')),
        ],
      ),
    );
    final code = codeCtrl.text.trim();
    final name = nameCtrl.text.trim();
    final legal = legalCtrl.text.trim();
    final type = typeCtrl.text.trim().isEmpty ? 'Branch' : typeCtrl.text.trim();
    final gstin = gstinCtrl.text.trim();
    final pan = panCtrl.text.trim();
    codeCtrl.dispose();
    nameCtrl.dispose();
    legalCtrl.dispose();
    typeCtrl.dispose();
    gstinCtrl.dispose();
    panCtrl.dispose();
    if (ok != true) return;
    if (code.isEmpty || name.isEmpty) {
      _snack('Code and name are required');
      return;
    }
    try {
      await _service.create(
        code: code,
        name: name,
        parentOrganizationId: root.id,
        organizationType: type,
        legalName: legal.isEmpty ? null : legal,
        gstin: gstin.isEmpty ? null : gstin,
        pan: pan.isEmpty ? null : pan,
      );
      _snack('Organization created');
      await _load();
    } catch (e) {
      _snack(e.toString().replaceFirst('Exception: ', ''));
    }
  }

  Future<void> _view(OrganizationSummary org) async {
    try {
      final full = await _service.get(org.id);
      if (!mounted) return;
      await showDialog<void>(
        context: context,
        builder: (ctx) => AlertDialog(
          title: Text('${full.code} · ${full.name}'),
          content: SizedBox(
            width: 480,
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _kv('Status', full.status),
                  _kv('Type', full.organizationType ?? '—'),
                  _kv('Legal name', full.legalName ?? '—'),
                  _kv('ROOT', full.isRoot ? 'Yes' : 'No'),
                  _kv('Level', '${full.level ?? 0}'),
                  _kv('GSTIN', full.gstin ?? '—'),
                  _kv('PAN', full.pan ?? '—'),
                  _kv('Currency', full.defaultCurrencyCode ?? '—'),
                  _kv('FY start month', '${full.fiscalYearStartMonth ?? 4}'),
                  _kv('Email', full.email ?? '—'),
                  _kv('Phone', full.phone ?? '—'),
                  _kv('Website', full.website ?? '—'),
                  _kv('Address ID', full.addressId ?? '—'),
                  _kv('Version', '${full.versionNo}'),
                ],
              ),
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Close')),
          ],
        ),
      );
    } catch (e) {
      _snack(e.toString().replaceFirst('Exception: ', ''));
    }
  }

  Widget _kv(String k, String v) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 4),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SizedBox(
              width: 140,
              child: Text(k, style: const TextStyle(fontWeight: FontWeight.w600)),
            ),
            Expanded(child: SelectableText(v)),
          ],
        ),
      );

  Future<void> _edit(OrganizationSummary org) async {
    final nameCtrl = TextEditingController(text: org.name);
    final legalCtrl = TextEditingController(text: org.legalName ?? '');
    final gstinCtrl = TextEditingController(text: org.gstin ?? '');
    final panCtrl = TextEditingController(text: org.pan ?? '');
    final fyCtrl = TextEditingController(
      text: '${org.fiscalYearStartMonth ?? 4}',
    );
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(org.isRoot ? 'Edit root organization' : 'Edit organization'),
        content: SizedBox(
          width: 480,
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: nameCtrl,
                  decoration: const InputDecoration(labelText: 'Name'),
                ),
                TextField(
                  controller: legalCtrl,
                  decoration: const InputDecoration(labelText: 'Legal name'),
                ),
                TextField(
                  controller: gstinCtrl,
                  decoration: const InputDecoration(labelText: 'GSTIN'),
                ),
                TextField(
                  controller: panCtrl,
                  decoration: const InputDecoration(labelText: 'PAN'),
                ),
                TextField(
                  controller: fyCtrl,
                  decoration: const InputDecoration(
                    labelText: 'Fiscal year start month (1–12)',
                  ),
                  keyboardType: TextInputType.number,
                ),
              ],
            ),
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Save')),
        ],
      ),
    );
    final name = nameCtrl.text.trim();
    final legal = legalCtrl.text.trim();
    final gstin = gstinCtrl.text.trim();
    final pan = panCtrl.text.trim();
    final fy = int.tryParse(fyCtrl.text.trim());
    nameCtrl.dispose();
    legalCtrl.dispose();
    gstinCtrl.dispose();
    panCtrl.dispose();
    fyCtrl.dispose();
    if (ok != true) return;
    try {
      await _service.update(
        id: org.id,
        versionNo: org.versionNo,
        name: name,
        legalName: legal.isEmpty ? null : legal,
        gstin: gstin.isEmpty ? null : gstin,
        pan: pan.isEmpty ? null : pan,
        fiscalYearStartMonth: fy,
      );
      _snack('Organization updated');
      await _load();
    } catch (e) {
      _snack(e.toString().replaceFirst('Exception: ', ''));
    }
  }

  Future<void> _showHierarchy(OrganizationSummary org) async {
    try {
      final tree = await _service.hierarchy(org.id);
      if (!mounted) return;
      await showDialog<void>(
        context: context,
        builder: (ctx) => AlertDialog(
          title: const Text('Organization hierarchy'),
          content: SizedBox(
            width: 420,
            child: SingleChildScrollView(
              child: Text(_formatTree(tree, 0)),
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Close')),
          ],
        ),
      );
    } catch (e) {
      _snack(e.toString().replaceFirst('Exception: ', ''));
    }
  }

  Future<void> _showHistory(OrganizationSummary org) async {
    try {
      final items = await _service.history(org.id);
      if (!mounted) return;
      await showDialog<void>(
        context: context,
        builder: (ctx) => AlertDialog(
          title: Text('History · ${org.code}'),
          content: SizedBox(
            width: 520,
            height: 360,
            child: items.isEmpty
                ? const Center(child: Text('No audit events yet'))
                : ListView.separated(
                    itemCount: items.length,
                    separatorBuilder: (_, __) => const Divider(height: 1),
                    itemBuilder: (_, i) {
                      final h = items[i];
                      return ListTile(
                        dense: true,
                        title: Text(h.eventType),
                        subtitle: Text(
                          [
                            h.createdOn,
                            if (h.actorEmail != null) h.actorEmail!,
                            if (h.payloadJson != null && h.payloadJson!.isNotEmpty)
                              h.payloadJson!,
                          ].join('\n'),
                        ),
                        isThreeLine: true,
                      );
                    },
                  ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Close')),
          ],
        ),
      );
    } catch (e) {
      _snack(e.toString().replaceFirst('Exception: ', ''));
    }
  }

  String _formatTree(Map<String, dynamic> node, int depth) {
    final pad = '  ' * depth;
    final mark = (node['is_root'] as bool? ?? false) ? '◆' : '•';
    final buf = StringBuffer(
      '$pad$mark ${node['code']} — ${node['name']} (${node['status']})\n',
    );
    final children = (node['children'] as List?) ?? [];
    for (final c in children) {
      buf.write(_formatTree(c as Map<String, dynamic>, depth + 1));
    }
    return buf.toString();
  }

  @override
  Widget build(BuildContext context) {
    final narrow = MediaQuery.sizeOf(context).width < 700;
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Wrap(
            spacing: 8,
            runSpacing: 8,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: [
              SizedBox(
                width: narrow ? double.infinity : 280,
                child: TextField(
                  controller: _searchCtrl,
                  decoration: const InputDecoration(
                    labelText: 'Search',
                    prefixIcon: Icon(Icons.search),
                    isDense: true,
                  ),
                  onSubmitted: (_) => _load(),
                ),
              ),
              FilledButton.tonal(onPressed: _load, child: const Text('Search')),
              FilledButton(
                onPressed: _create,
                child: const Text('Create'),
              ),
              OutlinedButton(onPressed: _load, child: const Text('Refresh')),
            ],
          ),
          const SizedBox(height: 12),
          if (_loading)
            const Expanded(child: Center(child: CircularProgressIndicator()))
          else if (_error != null)
            Expanded(child: Center(child: Text(_error!)))
          else if (_items.isEmpty)
            const Expanded(
              child: Center(child: Text('No organizations found')),
            )
          else
            Expanded(
              child: ListView.separated(
                itemCount: _items.length,
                separatorBuilder: (_, __) => const Divider(height: 1),
                itemBuilder: (ctx, i) {
                  final o = _items[i];
                  return Semantics(
                    label: 'Organization ${o.code} ${o.name}',
                    button: true,
                    child: ListTile(
                      leading: Icon(
                        o.isRoot
                            ? Icons.account_balance
                            : Icons.business_outlined,
                      ),
                      title: Text('${o.code} · ${o.name}'),
                      subtitle: Text(
                        [
                          if (o.isRoot) 'ROOT',
                          o.status,
                          if (o.gstin != null) 'GSTIN ${o.gstin}',
                        ].join(' · '),
                      ),
                      onTap: () => _view(o),
                      trailing: Wrap(
                        spacing: 4,
                        children: [
                          IconButton(
                            tooltip: 'View',
                            onPressed: () => _view(o),
                            icon: const Icon(Icons.visibility_outlined),
                          ),
                          IconButton(
                            tooltip: 'History',
                            onPressed: () => _showHistory(o),
                            icon: const Icon(Icons.history),
                          ),
                          IconButton(
                            tooltip: 'Hierarchy',
                            onPressed: () => _showHierarchy(o),
                            icon: const Icon(Icons.account_tree_outlined),
                          ),
                          IconButton(
                            tooltip: 'Edit',
                            onPressed: () => _edit(o),
                            icon: const Icon(Icons.edit_outlined),
                          ),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),
        ],
      ),
    );
  }
}
