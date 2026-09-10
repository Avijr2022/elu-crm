import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/routing/crm_routes.dart';
import '../../../core/theme/crm_theme.dart';
import '../../../core/widgets/crm_section_card.dart';
import '../../../core/widgets/crm_status_chip.dart';
import '../data/quotation_service.dart';
import 'widgets/quotation_line_dialog.dart';

class QuotationDetailPage extends StatefulWidget {
  const QuotationDetailPage({super.key, required this.quotationId, this.service});

  final String quotationId;
  final QuotationService? service;

  @override
  State<QuotationDetailPage> createState() => _QuotationDetailPageState();
}

class _QuotationDetailPageState extends State<QuotationDetailPage> {
  late final QuotationService _service = widget.service ?? QuotationService();
  bool _loading = true;
  bool _acting = false;
  String? _error;
  Quotation? _quote;
  List<QuotationStatusEntry> _history = [];

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
      final q = await _service.getById(widget.quotationId);
      final h = await _service.getHistory(widget.quotationId);
      if (!mounted) return;
      setState(() {
        _quote = q;
        _history = h;
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

  Future<void> _run(Future<void> Function() action, String success) async {
    setState(() => _acting = true);
    try {
      await action();
      await _load();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(success)));
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    } finally {
      if (mounted) setState(() => _acting = false);
    }
  }

  Future<void> _addLine() async {
    await _run(() async {
      await addQuotationLine(context, _service, widget.quotationId);
    }, 'Line added');
  }

  Future<void> _editLine(QuotationLine line) async {
    await _run(() async {
      await editQuotationLine(context, _service, widget.quotationId, line);
    }, 'Line updated');
  }

  Future<void> _deleteLine(QuotationLine line) async {
    await _run(() async {
      await _service.deleteLine(widget.quotationId, line.quotationLineId);
    }, 'Line removed');
  }

  List<Widget> _statusActions() {
    final q = _quote!;
    final busy = _acting;
    switch (q.status) {
      case 'DRAFT':
        return [
          OutlinedButton(onPressed: busy ? null : _addLine, child: const Text('Add line')),
          if (q.lines.isNotEmpty)
            FilledButton(
              onPressed: busy
                  ? null
                  : () => _run(
                        () => _service.updateStatus(widget.quotationId, 'SUBMITTED'),
                        'Submitted',
                      ),
              child: const Text('Submit'),
            ),
        ];
      case 'SUBMITTED':
        return [
          FilledButton(
            onPressed: busy
                ? null
                : () => _run(
                      () => _service.updateStatus(widget.quotationId, 'APPROVED'),
                      'Approved',
                    ),
            child: const Text('Approve'),
          ),
          OutlinedButton(
            onPressed: busy
                ? null
                : () => _run(
                      () => _service.updateStatus(widget.quotationId, 'REJECTED'),
                      'Rejected',
                    ),
            child: const Text('Reject'),
          ),
        ];
      case 'APPROVED':
        return [
          FilledButton(
            onPressed: busy
                ? null
                : () => _run(
                      () => _service.updateStatus(widget.quotationId, 'SENT'),
                      'Marked sent',
                    ),
            child: const Text('Send'),
          ),
        ];
      case 'SENT':
        return [
          FilledButton(
            onPressed: busy
                ? null
                : () => _run(
                      () => _service.recordCustomerResponse(widget.quotationId, 'ACCEPTED'),
                      'Customer accepted',
                    ),
            child: const Text('Accept'),
          ),
          OutlinedButton(
            onPressed: busy
                ? null
                : () => _run(
                      () => _service.recordCustomerResponse(widget.quotationId, 'REJECTED'),
                      'Customer rejected',
                    ),
            child: const Text('Reject'),
          ),
        ];
      case 'ACCEPTED':
        if (q.salesOrderId != null) {
          return [
            FilledButton(
              key: const Key('view-sales-order'),
              onPressed: busy
                  ? null
                  : () => context.push(CrmRoutes.salesOrderDetail(q.salesOrderId!)),
              child: Text('View sales order${q.soNumber != null ? ' (${q.soNumber})' : ''}'),
            ),
          ];
        }
        return [
          FilledButton(
            key: const Key('convert-to-so'),
            onPressed: busy ? null : _convertToSalesOrder,
            child: const Text('Convert to sales order'),
          ),
        ];
      default:
        return [];
    }
  }

  Future<void> _convertToSalesOrder() async {
    setState(() => _acting = true);
    try {
      final result = await _service.convertToSalesOrder(widget.quotationId);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(result.message)));
      context.push(CrmRoutes.salesOrderDetail(result.salesOrderId));
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
    final actions = _quote == null ? <Widget>[] : _statusActions();
    return Scaffold(
      appBar: AppBar(
        title: Text(_quote?.quotationNumber ?? 'Quotation'),
        actions: [
          IconButton(onPressed: _loading ? null : _load, icon: const Icon(Icons.refresh)),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!))
              : _quote == null
                  ? const SizedBox.shrink()
                  : ListView(
                      padding: const EdgeInsets.all(CrmSpacing.page),
                      children: [
                        Row(
                          children: [
                            Expanded(
                              child: Text(
                                _quote!.quotationNumber,
                                style: Theme.of(context).textTheme.headlineSmall,
                              ),
                            ),
                            CrmStatusChip(status: _quote!.status),
                          ],
                        ),
                        if (actions.isNotEmpty) ...[
                          const SizedBox(height: CrmSpacing.sm),
                          Wrap(spacing: CrmSpacing.sm, runSpacing: CrmSpacing.sm, children: actions),
                        ],
                        const SizedBox(height: CrmSpacing.md),
                        CrmSectionCard(
                          title: 'Totals',
                          child: Column(
                            children: [
                              _totalRow('Subtotal', _quote!.subtotal),
                              _totalRow('Discount', _quote!.discountTotal),
                              _totalRow('Tax', _quote!.taxTotal),
                              const Divider(),
                              _totalRow('Grand total', _quote!.grandTotal, bold: true),
                            ],
                          ),
                        ),
                        const SizedBox(height: CrmSpacing.md),
                        CrmSectionCard(
                          title: 'Lines (${_quote!.lines.length})',
                          child: _quote!.lines.isEmpty
                              ? const Text('No line items — add lines while in Draft')
                              : Column(
                                  children: _quote!.lines
                                      .map(
                                        (line) => ListTile(
                                          dense: true,
                                          contentPadding: EdgeInsets.zero,
                                          title: Text(line.description),
                                          subtitle: Text(
                                            'Qty ${line.qty} × ${line.unitPrice} ${line.taxCode ?? ''}',
                                          ),
                                          trailing: _quote!.status == 'DRAFT'
                                              ? Row(
                                                  mainAxisSize: MainAxisSize.min,
                                                  children: [
                                                    Text(line.lineTotal),
                                                    IconButton(
                                                      icon: const Icon(Icons.edit_outlined, size: 20),
                                                      onPressed: _acting ? null : () => _editLine(line),
                                                    ),
                                                    IconButton(
                                                      icon: const Icon(Icons.delete_outline, size: 20),
                                                      onPressed: _acting ? null : () => _deleteLine(line),
                                                    ),
                                                  ],
                                                )
                                              : Text(line.lineTotal),
                                        ),
                                      )
                                      .toList(),
                                ),
                        ),
                        if (_history.isNotEmpty) ...[
                          const SizedBox(height: CrmSpacing.md),
                          CrmSectionCard(
                            title: 'Status history',
                            child: Column(
                              children: _history
                                  .map(
                                    (h) => ListTile(
                                      dense: true,
                                      contentPadding: EdgeInsets.zero,
                                      title: Text('${h.fromStatus} → ${h.toStatus}'),
                                      subtitle: h.reason == null ? null : Text(h.reason!),
                                    ),
                                  )
                                  .toList(),
                            ),
                          ),
                        ],
                      ],
                    ),
    );
  }

  Widget _totalRow(String label, String value, {bool bold = false}) {
    final style = bold ? const TextStyle(fontWeight: FontWeight.bold) : null;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: style),
          Text('${_quote!.currencyCode} $value', style: style),
        ],
      ),
    );
  }
}
