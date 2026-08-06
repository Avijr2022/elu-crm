import 'package:flutter/material.dart';

import '../data/edition_service.dart';

/// Edition List / Search / Create / Edit / View / Publish / History (ELU-UI-PF / BFS §11)
class EditionsPage extends StatefulWidget {
  const EditionsPage({super.key});

  @override
  State<EditionsPage> createState() => _EditionsPageState();
}

class _EditionsPageState extends State<EditionsPage> {
  final _service = EditionService();
  final _searchCtrl = TextEditingController();
  bool _loading = true;
  String? _error;
  List<EditionSummary> _items = [];
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
      final items = await _service.listEditions(
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

  Future<void> _createDraft() async {
    final codeCtrl = TextEditingController();
    final nameCtrl = TextEditingController();
    final descCtrl = TextEditingController();
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Create edition draft'),
        content: SizedBox(
          width: 420,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: codeCtrl,
                decoration: const InputDecoration(
                  labelText: 'Code (uppercase)',
                ),
                textCapitalization: TextCapitalization.characters,
              ),
              TextField(
                controller: nameCtrl,
                decoration: const InputDecoration(labelText: 'Name'),
              ),
              TextField(
                controller: descCtrl,
                decoration: const InputDecoration(labelText: 'Description'),
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
            child: const Text('Create'),
          ),
        ],
      ),
    );
    if (ok != true) return;
    try {
      await _service.createDraft(
        code: codeCtrl.text.trim(),
        name: nameCtrl.text.trim(),
        description: descCtrl.text.trim().isEmpty ? null : descCtrl.text.trim(),
      );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Draft created')),
      );
      await _load();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  Future<void> _edit(EditionSummary item) async {
    if (item.status != 'DRAFT' && item.status != 'ACTIVE') {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Cannot edit status ${item.status}')),
      );
      return;
    }
    final detail = await _service.getEdition(item.id);
    if (!mounted) return;
    final nameCtrl = TextEditingController(text: detail.name);
    final descCtrl = TextEditingController(text: detail.description ?? '');
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text('Edit ${detail.code}'),
        content: SizedBox(
          width: 420,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nameCtrl,
                decoration: const InputDecoration(labelText: 'Name'),
              ),
              TextField(
                controller: descCtrl,
                decoration: const InputDecoration(labelText: 'Description'),
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
      await _service.updateDraft(
        id: detail.id,
        versionNo: detail.versionNo,
        name: nameCtrl.text.trim(),
        description: descCtrl.text.trim(),
      );
      await _load();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  Future<void> _publish(EditionSummary item) async {
    final detail = await _service.getEdition(item.id);
    if (!mounted) return;
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Publish edition'),
        content: Text(
          'Publish ${detail.code} (${detail.name}) to ACTIVE?\n'
          'Requires feature and limit rows (BR-PF-008).',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Publish'),
          ),
        ],
      ),
    );
    if (ok != true) return;
    try {
      await _service.publish(detail.id, detail.versionNo);
      await _load();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  Future<void> _showHistory(EditionSummary item) async {
    try {
      final rows = await _service.history(item.id);
      if (!mounted) return;
      await showDialog<void>(
        context: context,
        builder: (ctx) => AlertDialog(
          title: Text('History · ${item.code}'),
          content: SizedBox(
            width: 420,
            height: 320,
            child: ListView.builder(
              itemCount: rows.length,
              itemBuilder: (_, i) {
                final r = rows[i];
                return ListTile(
                  dense: true,
                  title: Text('v${r.versionNo}'),
                  subtitle: Text('${r.changeSummary ?? ''}\n${r.createdOn}'),
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

  Future<void> _openDetail(EditionSummary item) async {
    try {
      final detail = await _service.getEdition(item.id);
      if (!mounted) return;
      await showDialog<void>(
        context: context,
        builder: (ctx) => AlertDialog(
          title: Text('${detail.code} · ${detail.name}'),
          content: SizedBox(
            width: 420,
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Status: ${detail.status}'),
                  Text('Version: ${detail.versionNo}'),
                  if (detail.description != null) ...[
                    const SizedBox(height: 8),
                    Text(detail.description!),
                  ],
                  const SizedBox(height: 16),
                  Text('Features', style: Theme.of(ctx).textTheme.titleSmall),
                  ...detail.features.map(
                    (f) => Text(
                      '• ${f['feature_code']} '
                      '(${f['is_enabled'] == true ? 'on' : 'off'})',
                    ),
                  ),
                  const SizedBox(height: 12),
                  Text('Limits', style: Theme.of(ctx).textTheme.titleSmall),
                  ...detail.limits.map(
                    (l) => Text(
                      '• ${l['limit_code']}: ${l['limit_value']} '
                      '${l['limit_unit'] ?? ''}',
                    ),
                  ),
                ],
              ),
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(ctx).pop(),
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

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
          child: Wrap(
            spacing: 8,
            runSpacing: 8,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: [
              Text(
                'Edition Management (PF-001)',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              SizedBox(
                width: 200,
                child: TextField(
                  controller: _searchCtrl,
                  decoration: const InputDecoration(
                    labelText: 'Search',
                    isDense: true,
                    prefixIcon: Icon(Icons.search, size: 18),
                  ),
                  onSubmitted: (_) => _load(),
                ),
              ),
              DropdownButton<String?>(
                value: _statusFilter,
                hint: const Text('Status'),
                items: const [
                  DropdownMenuItem(value: null, child: Text('All')),
                  DropdownMenuItem(value: 'ACTIVE', child: Text('ACTIVE')),
                  DropdownMenuItem(value: 'DRAFT', child: Text('DRAFT')),
                  DropdownMenuItem(
                    value: 'DEPRECATED',
                    child: Text('DEPRECATED'),
                  ),
                ],
                onChanged: (v) {
                  setState(() => _statusFilter = v);
                  _load();
                },
              ),
              FilledButton.icon(
                onPressed: _createDraft,
                icon: const Icon(Icons.add),
                label: const Text('Create'),
              ),
              IconButton(
                tooltip: 'Refresh',
                onPressed: _load,
                icon: const Icon(Icons.refresh),
              ),
            ],
          ),
        ),
        if (_loading) const LinearProgressIndicator(),
        if (_error != null)
          Padding(
            padding: const EdgeInsets.all(16),
            child: Text(
              _error!,
              style: TextStyle(color: Theme.of(context).colorScheme.error),
            ),
          ),
        Expanded(
          child: ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: _items.length,
            separatorBuilder: (_, __) => const Divider(height: 1),
            itemBuilder: (context, index) {
              final e = _items[index];
              return ListTile(
                title: Text('${e.code} — ${e.name}'),
                subtitle: Text('Status ${e.status} · v${e.versionNo}'),
                onTap: () => _openDetail(e),
                trailing: Wrap(
                  spacing: 4,
                  children: [
                    IconButton(
                      tooltip: 'Edit',
                      icon: const Icon(Icons.edit_outlined),
                      onPressed: () => _edit(e),
                    ),
                    if (e.status == 'DRAFT')
                      IconButton(
                        tooltip: 'Publish',
                        icon: const Icon(Icons.publish_outlined),
                        onPressed: () => _publish(e),
                      ),
                    IconButton(
                      tooltip: 'History',
                      icon: const Icon(Icons.history),
                      onPressed: () => _showHistory(e),
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
