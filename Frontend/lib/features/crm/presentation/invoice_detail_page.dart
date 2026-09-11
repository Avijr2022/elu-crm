import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/auth/auth_controller.dart';
import '../../../core/theme/crm_theme.dart';
import '../data/invoice_service.dart';

class InvoiceDetailPage extends StatefulWidget {
  const InvoiceDetailPage({super.key, required this.invoiceId});

  final String invoiceId;

  @override
  State<InvoiceDetailPage> createState() => _InvoiceDetailPageState();
}

class _InvoiceDetailPageState extends State<InvoiceDetailPage> {
  final _service = InvoiceService();
  bool _loading = true;
  bool _issuing = false;
  String? _error;
  Invoice? _invoice;

  bool get _canIssue {
    final perms = context.read<AuthController>().profile?['permissions'];
    return perms is List && perms.contains('quotation.update');
  }

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
      final invoice = await _service.getById(widget.invoiceId);
      if (!mounted) return;
      setState(() {
        _invoice = invoice;
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

  Future<void> _issue() async {
    setState(() => _issuing = true);
    try {
      final updated = await _service.issue(widget.invoiceId);
      if (!mounted) return;
      setState(() => _invoice = updated);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Invoice ${updated.invoiceNumber} issued')),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    } finally {
      if (mounted) setState(() => _issuing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Center(child: CircularProgressIndicator());
    if (_error != null) return Center(child: Text(_error!));
    final invoice = _invoice!;
    return RefreshIndicator(
      onRefresh: _load,
      child: ListView(
        padding: const EdgeInsets.all(CrmSpacing.page),
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  invoice.invoiceNumber,
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ),
              Chip(label: Text(invoice.status)),
            ],
          ),
          const SizedBox(height: CrmSpacing.sm),
          Card(
            child: Column(
              children: [
                _row('Customer', invoice.customerName ?? '—'),
                _row('Sales order', invoice.soNumber ?? '—'),
                _row('Invoice date', invoice.invoiceDate),
                if (invoice.issuedOn != null)
                  _row('Issued on', invoice.issuedOn!),
                _row('Subtotal', '${invoice.currencyCode} ${invoice.subtotal}'),
                _row('Tax', '${invoice.currencyCode} ${invoice.taxTotal}'),
                _row('Grand total',
                    '${invoice.currencyCode} ${invoice.grandTotal}'),
                _row('Allocated',
                    '${invoice.currencyCode} ${invoice.allocatedTotal}'),
                _row('Balance due',
                    '${invoice.currencyCode} ${invoice.balanceDue}'),
              ],
            ),
          ),
          const SizedBox(height: CrmSpacing.md),
          Text('Allocations', style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: CrmSpacing.sm),
          if (invoice.allocations.isEmpty)
            const Card(
                child: ListTile(title: Text('No payment allocations yet')))
          else
            Card(
              child: Column(
                children: [
                  for (final a in invoice.allocations)
                    ListTile(
                      dense: true,
                      title: Text(a.receiptNumber ?? a.paymentReceiptId),
                      trailing:
                          Text('${invoice.currencyCode} ${a.allocatedAmount}'),
                    ),
                ],
              ),
            ),
          const SizedBox(height: CrmSpacing.md),
          if (_canIssue && invoice.isDraft)
            FilledButton.icon(
              onPressed: _issuing ? null : _issue,
              icon: const Icon(Icons.check_circle_outline),
              label: Text(_issuing ? 'Issuing…' : 'Issue invoice'),
            ),
        ],
      ),
    );
  }

  Widget _row(String label, String value) => ListTile(
        dense: true,
        title: Text(label),
        trailing: Text(value),
      );
}
