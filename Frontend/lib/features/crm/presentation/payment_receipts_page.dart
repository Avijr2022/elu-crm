import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/routing/crm_routes.dart';
import '../../../core/theme/crm_theme.dart';
import '../data/payment_receipt_service.dart';

class PaymentReceiptsPage extends StatefulWidget {
  const PaymentReceiptsPage({super.key});

  @override
  State<PaymentReceiptsPage> createState() => _PaymentReceiptsPageState();
}

class _PaymentReceiptsPageState extends State<PaymentReceiptsPage> {
  final _service = PaymentReceiptService();
  bool _loading = true;
  String? _error;
  List<PaymentReceipt> _items = [];

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
      return Center(child: Text(_error!));
    }
    return RefreshIndicator(
      onRefresh: _load,
      child: _items.isEmpty
          ? ListView(children: const [
              SizedBox(height: 120),
              Center(child: Text('No payment receipts')),
            ])
          : ListView.separated(
              padding: const EdgeInsets.all(CrmSpacing.page),
              itemCount: _items.length,
              separatorBuilder: (_, __) => const SizedBox(height: CrmSpacing.sm),
              itemBuilder: (_, i) {
                final r = _items[i];
                return Card(
                  child: ListTile(
                    title: Text(r.receiptNumber),
                    subtitle: Text(
                      [
                        if (r.soNumber != null) r.soNumber,
                        if (r.customerName != null) r.customerName,
                      ].whereType<String>().join(' · '),
                    ),
                    trailing: Text('${r.currencyCode} ${r.amount}'),
                    onTap: () => context.push(CrmRoutes.paymentReceiptDetail(r.paymentReceiptId)),
                  ),
                );
              },
            ),
    );
  }
}
