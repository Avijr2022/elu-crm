import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/routing/crm_routes.dart';
import '../../../core/theme/crm_theme.dart';
import '../../../core/widgets/crm_status_chip.dart';
import '../data/quotation_service.dart';

class QuotationsPage extends StatefulWidget {
  const QuotationsPage({super.key});

  @override
  State<QuotationsPage> createState() => _QuotationsPageState();
}

class _QuotationsPageState extends State<QuotationsPage> {
  final _service = QuotationService();
  bool _loading = true;
  String? _error;
  List<Quotation> _items = [];

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
      final r = await _service.list();
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
    if (_loading && _items.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_error != null && _items.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
            TextButton(onPressed: _load, child: const Text('Retry')),
          ],
        ),
      );
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(CrmSpacing.page, CrmSpacing.page, CrmSpacing.page, 0),
          child: Align(
            alignment: Alignment.centerRight,
            child: FilledButton.icon(
              onPressed: () async {
                await context.push(CrmRoutes.quotationsNew);
                if (mounted) _load();
              },
              icon: const Icon(Icons.add),
              label: const Text('New'),
            ),
          ),
        ),
        Expanded(
          child: RefreshIndicator(
      onRefresh: _load,
      child: _items.isEmpty
          ? ListView(children: const [SizedBox(height: 120), Center(child: Text('No quotations'))])
          : ListView.separated(
              padding: const EdgeInsets.all(CrmSpacing.page),
              itemCount: _items.length,
              separatorBuilder: (_, __) => const SizedBox(height: CrmSpacing.sm),
              itemBuilder: (_, i) {
                final q = _items[i];
                return Card(
                  child: ListTile(
                    title: Text(q.quotationNumber),
                    subtitle: Text('${q.currencyCode} ${q.grandTotal}'),
                    trailing: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        if (q.soNumber != null) ...[
                          Chip(
                            label: Text(q.soNumber!, style: const TextStyle(fontSize: 11)),
                            visualDensity: VisualDensity.compact,
                            padding: EdgeInsets.zero,
                          ),
                          const SizedBox(width: CrmSpacing.xs),
                        ],
                        CrmStatusChip(status: q.status),
                      ],
                    ),
                    onTap: () => context.push(CrmRoutes.quotationDetail(q.quotationId)),
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
