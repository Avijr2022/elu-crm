import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/routing/crm_routes.dart';
import '../../../core/theme/crm_theme.dart';
import '../data/customer_service.dart';
import '../data/quotation_service.dart';

class QuotationFormPage extends StatefulWidget {
  const QuotationFormPage({super.key});

  @override
  State<QuotationFormPage> createState() => _QuotationFormPageState();
}

class _QuotationFormPageState extends State<QuotationFormPage> {
  final _quoteService = QuotationService();
  final _customerService = CustomerService();
  final _notesCtrl = TextEditingController();
  bool _loading = true;
  bool _saving = false;
  String? _error;
  List<Customer> _customers = [];
  String? _customerId;
  String _currency = 'INR';

  @override
  void initState() {
    super.initState();
    _loadCustomers();
  }

  @override
  void dispose() {
    _notesCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadCustomers() async {
    try {
      final r = await _customerService.list(pageSize: 100);
      if (!mounted) return;
      setState(() {
        _customers = r.items;
        _loading = false;
        if (_customers.isNotEmpty) _customerId = _customers.first.customerId;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString().replaceFirst('Exception: ', '');
        _loading = false;
      });
    }
  }

  Future<void> _save() async {
    if (_customerId == null) return;
    setState(() => _saving = true);
    try {
      final q = await _quoteService.create(
        customerId: _customerId!,
        currencyCode: _currency,
        notes: _notesCtrl.text.trim().isEmpty ? null : _notesCtrl.text.trim(),
      );
      if (!mounted) return;
      context.go(CrmRoutes.quotationDetail(q.quotationId));
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('New Quotation')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!))
              : ListView(
                  padding: const EdgeInsets.all(CrmSpacing.page),
                  children: [
                    DropdownButtonFormField<String>(
                      value: _customerId,
                      decoration: const InputDecoration(labelText: 'Customer *'),
                      items: _customers
                          .map(
                            (c) => DropdownMenuItem(
                              value: c.customerId,
                              child: Text(c.legalName),
                            ),
                          )
                          .toList(),
                      onChanged: (v) => setState(() => _customerId = v),
                    ),
                    const SizedBox(height: CrmSpacing.sm),
                    DropdownButtonFormField<String>(
                      value: _currency,
                      decoration: const InputDecoration(labelText: 'Currency'),
                      items: const [
                        DropdownMenuItem(value: 'INR', child: Text('INR')),
                        DropdownMenuItem(value: 'USD', child: Text('USD')),
                      ],
                      onChanged: (v) => setState(() => _currency = v ?? 'INR'),
                    ),
                    const SizedBox(height: CrmSpacing.sm),
                    TextField(
                      controller: _notesCtrl,
                      decoration: const InputDecoration(labelText: 'Notes'),
                      maxLines: 3,
                    ),
                    const SizedBox(height: CrmSpacing.lg),
                    FilledButton(
                      onPressed: (_saving || _customerId == null) ? null : _save,
                      child: _saving
                          ? const SizedBox(
                              width: 18,
                              height: 18,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Text('Create draft'),
                    ),
                  ],
                ),
    );
  }
}
