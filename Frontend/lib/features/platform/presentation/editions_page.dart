import 'package:flutter/material.dart';

import '../data/edition_service.dart';

class EditionsPage extends StatefulWidget {
  const EditionsPage({super.key});

  @override
  State<EditionsPage> createState() => _EditionsPageState();
}

class _EditionsPageState extends State<EditionsPage> {
  final _service = EditionService();
  bool _loading = true;
  String? _error;
  List<EditionSummary> _items = [];
  String? _statusFilter;

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
      final items = await _service.listEditions(status: _statusFilter);
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
          child: Row(
            children: [
              Text(
                'Edition Management (PF-001)',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const Spacer(),
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
            child: Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
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
                trailing: const Icon(Icons.chevron_right),
                onTap: () => _openDetail(e),
              );
            },
          ),
        ),
      ],
    );
  }
}
