import 'package:flutter/material.dart';

import '../../../core/theme/crm_theme.dart';
import '../../../core/widgets/crm_section_card.dart';
import '../data/payment_receipt_service.dart';

class PaymentReceiptDetailPage extends StatefulWidget {
  const PaymentReceiptDetailPage({super.key, required this.paymentReceiptId});

  final String paymentReceiptId;

  @override
  State<PaymentReceiptDetailPage> createState() => _PaymentReceiptDetailPageState();
}

class _PaymentReceiptDetailPageState extends State<PaymentReceiptDetailPage> {
  final _service = PaymentReceiptService();
  bool _loading = true;
  String? _error;
  PaymentReceipt? _receipt;

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
      final r = await _service.getById(widget.paymentReceiptId);
      if (!mounted) return;
      setState(() {
        _receipt = r;
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
      appBar: AppBar(title: Text(_receipt?.receiptNumber ?? 'Payment receipt')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!))
              : ListView(
                  padding: const EdgeInsets.all(CrmSpacing.page),
                  children: [
                    Text(_receipt!.receiptNumber, style: Theme.of(context).textTheme.headlineSmall),
                    const SizedBox(height: CrmSpacing.md),
                    CrmSectionCard(
                      title: 'Details',
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Amount: ${_receipt!.currencyCode} ${_receipt!.amount}'),
                          Text('Status: ${_receipt!.status}'),
                          Text('Method: ${_receipt!.method}'),
                          if (_receipt!.soNumber != null) Text('Sales order: ${_receipt!.soNumber}'),
                          if (_receipt!.customerName != null) Text('Customer: ${_receipt!.customerName}'),
                        ],
                      ),
                    ),
                    if (_receipt!.allocations.isNotEmpty)
                      CrmSectionCard(
                        title: 'Allocations',
                        child: Column(
                          children: _receipt!.allocations
                              .map(
                                (a) => ListTile(
                                  dense: true,
                                  title: Text('Invoice ${a.invoiceId.substring(0, 8)}…'),
                                  trailing: Text(a.allocatedAmount),
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
