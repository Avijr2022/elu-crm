import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/routing/crm_routes.dart';
import '../../../core/theme/crm_theme.dart';
import '../../../core/widgets/crm_section_card.dart';
import '../../../core/widgets/crm_status_chip.dart';
import '../data/work_order_service.dart';

class WorkOrderDetailPage extends StatefulWidget {
  const WorkOrderDetailPage({super.key, required this.workOrderId});

  final String workOrderId;

  @override
  State<WorkOrderDetailPage> createState() => _WorkOrderDetailPageState();
}

class _WorkOrderDetailPageState extends State<WorkOrderDetailPage> {
  final _service = WorkOrderService();
  bool _loading = true;
  String? _error;
  WorkOrder? _wo;

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
      final wo = await _service.getById(widget.workOrderId);
      if (!mounted) return;
      setState(() {
        _wo = wo;
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
    return Scaffold(
      appBar: AppBar(title: Text(_wo?.woNumber ?? 'Work Order')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
                      TextButton(onPressed: _load, child: const Text('Retry')),
                    ],
                  ),
                )
              : ListView(
                  padding: const EdgeInsets.all(CrmSpacing.page),
                  children: [
                    Row(
                      children: [
                        Text(_wo!.woNumber, style: Theme.of(context).textTheme.headlineSmall),
                        const SizedBox(width: CrmSpacing.sm),
                        CrmStatusChip(status: _wo!.status),
                      ],
                    ),
                    const SizedBox(height: CrmSpacing.md),
                    CrmSectionCard(
                      title: 'Details',
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Created: ${_wo!.createdOn.split('T').first}'),
                          if (_wo!.customerId != null)
                            Text('Customer ID: ${_wo!.customerId}'),
                          if (_wo!.opportunityId != null) ...[
                            const SizedBox(height: CrmSpacing.sm),
                            TextButton(
                              onPressed: () => context.push(
                                CrmRoutes.opportunityDetail(_wo!.opportunityId!),
                              ),
                              child: const Text('View source opportunity'),
                            ),
                          ],
                          if (_wo!.salesOrderId != null) ...[
                            const SizedBox(height: CrmSpacing.sm),
                            Text(
                              _wo!.soNumber != null
                                  ? 'Linked sales order: ${_wo!.soNumber}'
                                  : 'Linked sales order',
                            ),
                            TextButton(
                              onPressed: () => context.push(
                                CrmRoutes.salesOrderDetail(_wo!.salesOrderId!),
                              ),
                              child: const Text('View linked sales order'),
                            ),
                          ],
                        ],
                      ),
                    ),
                  ],
                ),
    );
  }
}
