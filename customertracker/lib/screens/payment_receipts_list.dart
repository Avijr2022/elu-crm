import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class PaymentReceiptsList extends StatefulWidget {
  const PaymentReceiptsList({super.key});

  @override
  State<PaymentReceiptsList> createState() => _PaymentReceiptsListState();
}

class _PaymentReceiptsListState extends State<PaymentReceiptsList> {
  List<Map<String, dynamic>> _items = [];
  bool _loading = true;

  Future<String?> _getSavedToken() async {
    final sp = await SharedPreferences.getInstance();
    return sp.getString('access_token');
  }

  @override
  void initState() {
    super.initState();
    _fetchReceipts();
  }

  Future<void> _fetchReceipts() async {
    setState(() => _loading = true);
    try {
      final token = await _getSavedToken();
      final url = Uri.parse('http://localhost:8000/fin/payment-receipts');
      final resp = await http.get(url,
          headers: token != null ? {'Authorization': 'Bearer $token'} : {});
      if (resp.statusCode == 200) {
        final body = json.decode(resp.body) as Map<String, dynamic>;
        final items = (body['items'] as List<dynamic>?) ?? [];
        setState(() => _items = items.cast<Map<String, dynamic>>());
      } else {
        // ignore errors for now
      }
    } catch (e) {
      // ignore for now
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Payment Receipts'),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : ListView.separated(
              padding: const EdgeInsets.all(12),
              itemCount: _items.length,
              separatorBuilder: (_, __) => const Divider(),
              itemBuilder: (context, index) {
                final item = _items[index];
                final receiptNum =
                    item['receipt_number'] ?? item['receipt'] ?? 'Receipt';
                final customer =
                    item['customer_name'] ?? item['customer'] ?? 'Customer';
                final amount =
                    item['amount'] != null ? '₹ ${item['amount']}' : '';
                final date = item['received_on']?.toString() ?? '';
                return ListTile(
                  leading: const Icon(Icons.receipt_long),
                  title: Text('$receiptNum — $customer'),
                  subtitle: Text('$date • $amount'),
                  trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (_) => PaymentReceiptDetail(
                                paymentReceiptId: item['payment_receipt_id'],
                                salesOrderId: item['sales_order_id'],
                              )),
                    );
                  },
                );
              },
            ),
    );
  }
}

class PaymentReceiptDetail extends StatelessWidget {
  final String paymentReceiptId;
  final String salesOrderId;

  const PaymentReceiptDetail(
      {super.key, required this.paymentReceiptId, required this.salesOrderId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Receipt Detail')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Receipt: RC-1001',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            const Text('Customer: Acme Ltd.'),
            const SizedBox(height: 8),
            const Text('Sales Order: SO-2026-001'),
            const SizedBox(height: 8),
            const Text('Amount: ₹ 10,000'),
            const SizedBox(height: 8),
            const Text('Allocations:'),
            const SizedBox(height: 4),
            const Text('- Invoice INV-2026-0001 (₹ 10,000)'),
            const SizedBox(height: 16),
            _InvoiceButtonRow(
                paymentReceiptId: paymentReceiptId, salesOrderId: salesOrderId),
          ],
        ),
      ),
    );
  }
}

class _InvoiceButtonRow extends StatefulWidget {
  final String paymentReceiptId;
  final String salesOrderId;

  const _InvoiceButtonRow(
      {super.key, required this.paymentReceiptId, required this.salesOrderId});

  @override
  State<_InvoiceButtonRow> createState() => _InvoiceButtonRowState();
}

class _InvoiceButtonRowState extends State<_InvoiceButtonRow> {
  bool _loading = false;

  Future<String?> _getSavedToken() async {
    final sp = await SharedPreferences.getInstance();
    return sp.getString('access_token');
  }

  Future<void> _saveToken(String token) async {
    final sp = await SharedPreferences.getInstance();
    await sp.setString('access_token', token);
  }

  Future<void> _generateInvoice() async {
    final token = await _getSavedToken();
    String? finalToken = token;
    if (finalToken == null) {
      final ctrl = TextEditingController();
      final res = await showDialog<bool?>(
        context: context,
        builder: (_) => AlertDialog(
          title: const Text('Enter Access Token'),
          content: TextField(
            controller: ctrl,
            decoration: const InputDecoration(hintText: 'Bearer token'),
            obscureText: true,
          ),
          actions: [
            TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: const Text('Cancel')),
            TextButton(
                onPressed: () => Navigator.pop(context, true),
                child: const Text('Save')),
          ],
        ),
      );
      if (res == true && ctrl.text.trim().isNotEmpty) {
        finalToken = ctrl.text.trim();
        await _saveToken(finalToken);
      } else {
        return;
      }
    }

    setState(() => _loading = true);
    try {
      final salesOrderId =
          widget.salesOrderId; // real sales order id passed from list
      final url = Uri.parse(
          'http://localhost:8000/sal/sales-orders/$salesOrderId/generate-invoice-stub');
      final resp = await http.post(url, headers: {
        'Authorization': 'Bearer $finalToken',
        'Content-Type': 'application/json',
      });
      if (resp.statusCode == 200) {
        final body = json.decode(resp.body);
        // show compact summary and then allocate receipt
        final invoice = body['invoice'] ?? {};
        final invoiceId = invoice['invoice_id'];
        final invoiceNumber = invoice['invoice_number'];
        final allocationsCreated = body['allocations_created'] ?? 0;
        await showDialog<void>(
            context: context,
            builder: (_) => AlertDialog(
                    title: const Text('Invoice Created'),
                    content: Text(
                        'Invoice: $invoiceNumber\nAllocations created: $allocationsCreated'),
                    actions: [
                      TextButton(
                          onPressed: () => Navigator.pop(context),
                          child: const Text('OK'))
                    ]));

        // Now allocate this receipt to the invoice (ask user for full/partial)
        if (invoiceId != null) {
          final choice = await showDialog<String?>(
              context: context,
              builder: (_) => AlertDialog(
                    title: const Text('Allocate Receipt'),
                    content:
                        const Text('Allocate full receipt amount or partial?'),
                    actions: [
                      TextButton(
                          onPressed: () => Navigator.pop(context, 'full'),
                          child: const Text('Full')),
                      TextButton(
                          onPressed: () => Navigator.pop(context, 'partial'),
                          child: const Text('Partial')),
                      TextButton(
                          onPressed: () => Navigator.pop(context, null),
                          child: const Text('Cancel')),
                    ],
                  ));

          double? amount;
          if (choice == 'partial') {
            final ctrl = TextEditingController();
            final got = await showDialog<bool?>(
                context: context,
                builder: (_) => AlertDialog(
                      title: const Text('Enter amount to allocate'),
                      content: TextField(
                        controller: ctrl,
                        keyboardType:
                            TextInputType.numberWithOptions(decimal: true),
                        decoration: const InputDecoration(
                            hintText: 'Amount (e.g. 1000.00)'),
                      ),
                      actions: [
                        TextButton(
                            onPressed: () => Navigator.pop(context, false),
                            child: const Text('Cancel')),
                        TextButton(
                            onPressed: () => Navigator.pop(context, true),
                            child: const Text('OK')),
                      ],
                    ));
            if (got == true) {
              amount = double.tryParse(ctrl.text.trim());
            } else {
              amount = null;
            }
          }

          final allocUrl = Uri.parse(
              'http://localhost:8000/fin/payment-receipts/${widget.paymentReceiptId}/allocate');
          final bodyMap = <String, dynamic>{'invoice_id': invoiceId};
          if (amount != null) bodyMap['allocated_amount'] = amount;
          final allocResp = await http.post(allocUrl,
              headers: {
                'Authorization': 'Bearer $finalToken',
                'Content-Type': 'application/json',
              },
              body: json.encode(bodyMap));
          if (allocResp.statusCode == 200) {
            await showDialog<void>(
                context: context,
                builder: (_) => AlertDialog(
                      title: const Text('Allocation Successful'),
                      content: const Text('Receipt allocated to invoice.'),
                      actions: [
                        TextButton(
                            onPressed: () => Navigator.pop(context),
                            child: const Text('OK'))
                      ],
                    ));
          } else {
            // show allocation error
            await showDialog<void>(
                context: context,
                builder: (_) => AlertDialog(
                        title: const Text('Allocation Error'),
                        content: Text(
                            'Status ${allocResp.statusCode}: ${allocResp.body}'),
                        actions: [
                          TextButton(
                              onPressed: () => Navigator.pop(context),
                              child: const Text('OK'))
                        ]));
          }
        }
      } else {
        await showDialog<void>(
            context: context,
            builder: (_) => AlertDialog(
                    title: const Text('Error'),
                    content: Text('Status ${resp.statusCode}: ${resp.body}'),
                    actions: [
                      TextButton(
                          onPressed: () => Navigator.pop(context),
                          child: const Text('OK'))
                    ]));
      }
    } catch (e) {
      await showDialog<void>(
          context: context,
          builder: (_) => AlertDialog(
                  title: const Text('Error'),
                  content: Text(e.toString()),
                  actions: [
                    TextButton(
                        onPressed: () => Navigator.pop(context),
                        child: const Text('OK'))
                  ]));
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        ElevatedButton.icon(
          onPressed: _loading ? null : _generateInvoice,
          icon: const Icon(Icons.receipt_long),
          label: Text(_loading ? 'Generating...' : 'Generate Invoice Stub'),
        ),
      ],
    );
  }
}
