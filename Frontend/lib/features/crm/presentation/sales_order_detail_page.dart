import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../../core/edition/edition_controller.dart';
import '../../../core/routing/crm_routes.dart';
import '../../../core/theme/crm_theme.dart';
import '../../../core/widgets/crm_section_card.dart';
import '../../../core/widgets/crm_status_chip.dart';
import '../data/sales_order_service.dart';

class SalesOrderDetailPage extends StatefulWidget {
  const SalesOrderDetailPage({super.key, required this.salesOrderId});

  final String salesOrderId;

  @override
  State<SalesOrderDetailPage> createState() => _SalesOrderDetailPageState();
}

class _SalesOrderDetailPageState extends State<SalesOrderDetailPage> {
  final _service = SalesOrderService();
  bool _loading = true;
  bool _acting = false;
  String? _error;
  SalesOrder? _order;

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
      final o = await _service.getById(widget.salesOrderId);
      if (!mounted) return;
      setState(() {
        _order = o;
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

  Future<void> _confirm() async {
    setState(() => _acting = true);
    try {
      final msg = await _service.confirm(widget.salesOrderId);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
      await _load();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    } finally {
      if (mounted) setState(() => _acting = false);
    }
  }

  Future<void> _recordPaymentStub() async {
    setState(() => _acting = true);
    try {
      final msg = await _service.recordPaymentStub(widget.salesOrderId);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
      await _load();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    } finally {
      if (mounted) setState(() => _acting = false);
    }
  }

  Future<void> _generateInvoice() async {
    setState(() => _acting = true);
    try {
      final msg = await _service.generateInvoiceStub(widget.salesOrderId);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    } finally {
      if (mounted) setState(() => _acting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final hasFinInvoice = context.watch<EditionController>().hasFinInvoice;
    return Scaffold(
      appBar: AppBar(title: Text(_order?.soNumber ?? 'Sales Order')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!))
              : ListView(
                  padding: const EdgeInsets.all(CrmSpacing.page),
                  children: [
                    Row(
                      children: [
                        Text(_order!.soNumber, style: Theme.of(context).textTheme.headlineSmall),
                        const SizedBox(width: CrmSpacing.sm),
                        CrmStatusChip(status: _order!.status),
                      ],
                    ),
                    const SizedBox(height: CrmSpacing.md),
                    if (_order!.status == 'DRAFT')
                      Align(
                        alignment: Alignment.centerRight,
                        child: FilledButton(
                          onPressed: _acting ? null : _confirm,
                          child: _acting
                              ? const SizedBox(
                                  width: 18,
                                  height: 18,
                                  child: CircularProgressIndicator(strokeWidth: 2),
                                )
                              : const Text('Confirm order'),
                        ),
                      ),
                    if (_order!.status == 'CONFIRMED')
                      Align(
                        alignment: Alignment.centerRight,
                        child: Wrap(
                          spacing: CrmSpacing.sm,
                          children: [
                            OutlinedButton(
                              onPressed: _acting ? null : _recordPaymentStub,
                              child: const Text('Record payment (stub)'),
                            ),
                            if (hasFinInvoice)
                              FilledButton(
                                onPressed: _acting ? null : _generateInvoice,
                                child: const Text('Generate invoice (stub)'),
                              ),
                          ],
                        ),
                      ),
                    const SizedBox(height: CrmSpacing.md),
                    CrmSectionCard(
                      title: 'Totals',
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Grand total: ${_order!.currencyCode} ${_order!.grandTotal}'),
                          TextButton(
                            onPressed: () => context.push(
                              CrmRoutes.quotationDetail(_order!.quotationId),
                            ),
                            child: const Text('View source quotation'),
                          ),
                        ],
                      ),
                    ),
                    if (_order!.workOrders.isNotEmpty)
                      CrmSectionCard(
                        title: 'Linked work orders',
                        child: Column(
                          children: _order!.workOrders
                              .map(
                                (wo) => ListTile(
                                  dense: true,
                                  title: Text(wo.woNumber),
                                  trailing: CrmStatusChip(status: wo.status),
                                  onTap: () => context.push(
                                    CrmRoutes.workOrderDetail(wo.workOrderId),
                                  ),
                                ),
                              )
                              .toList(),
                        ),
                      ),
                    if (_order!.paymentStubs.isNotEmpty)
                      CrmSectionCard(
                        title: 'Payment stubs',
                        child: Column(
                          children: _order!.paymentStubs
                              .map(
                                (p) => ListTile(
                                  dense: true,
                                  title: Text(p.receiptNumber ?? p.paymentStatus),
                                  subtitle: Text(p.recordedOn),
                                  trailing: Text('${p.currencyCode} ${p.amount}'),
                                ),
                              )
                              .toList(),
                        ),
                      ),
                    if (_order!.lines.isNotEmpty)
                      CrmSectionCard(
                        title: 'Lines',
                        child: Column(
                          children: _order!.lines
                              .map(
                                (l) => ListTile(
                                  dense: true,
                                  title: Text(l.description),
                                  subtitle: Text('Qty ${l.qty}'),
                                  trailing: Text(l.lineTotal),
                                ),
                              )
                              .toList(),
                        ),
                      ),
                  ],
                ),
    );
  }
}
