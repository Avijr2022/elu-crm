import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/routing/crm_routes.dart';
import '../../../core/theme/crm_theme.dart';
import '../../../core/widgets/crm_status_chip.dart';
import '../data/work_order_service.dart';

class WorkOrdersPage extends StatefulWidget {
  const WorkOrdersPage({super.key});

  @override
  State<WorkOrdersPage> createState() => _WorkOrdersPageState();
}

class _WorkOrdersPageState extends State<WorkOrdersPage> {
  final _service = WorkOrderService();
  bool _loading = true;
  String? _error;
  List<WorkOrder> _items = [];

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
    return RefreshIndicator(
      onRefresh: _load,
      child: _items.isEmpty
          ? ListView(children: const [
              SizedBox(height: 120),
              Center(child: Text('No work orders queued')),
            ])
          : ListView.separated(
              padding: const EdgeInsets.all(CrmSpacing.page),
              itemCount: _items.length,
              separatorBuilder: (_, __) => const SizedBox(height: CrmSpacing.sm),
              itemBuilder: (_, i) {
                final wo = _items[i];
                final subtitle = wo.soNumber != null
                    ? 'SO ${wo.soNumber} · Created ${wo.createdOn.split('T').first}'
                    : 'Created ${wo.createdOn.split('T').first}';
                return Card(
                  child: ListTile(
                    title: Text(wo.woNumber),
                    subtitle: Text(subtitle),
                    trailing: CrmStatusChip(status: wo.status),
                    onTap: () => context.push(CrmRoutes.workOrderDetail(wo.workOrderId)),
                  ),
                );
              },
            ),
    );
  }
}
