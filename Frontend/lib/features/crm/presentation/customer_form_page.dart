import 'package:flutter/material.dart';

import '../../../core/theme/crm_theme.dart';
import '../data/customer_service.dart';

class CustomerFormPage extends StatefulWidget {
  const CustomerFormPage({super.key});

  @override
  State<CustomerFormPage> createState() => _CustomerFormPageState();
}

class _CustomerFormPageState extends State<CustomerFormPage> {
  final _service = CustomerService();
  final _formKey = GlobalKey<FormState>();
  final _legalCtrl = TextEditingController();
  final _tradeCtrl = TextEditingController();
  final _notesCtrl = TextEditingController();
  bool _saving = false;

  @override
  void dispose() {
    _legalCtrl.dispose();
    _tradeCtrl.dispose();
    _notesCtrl.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _saving = true);
    try {
      await _service.create(
        legalName: _legalCtrl.text.trim(),
        tradeName: _tradeCtrl.text.trim().isEmpty ? null : _tradeCtrl.text.trim(),
        notes: _notesCtrl.text.trim().isEmpty ? null : _notesCtrl.text.trim(),
      );
      if (!mounted) return;
      Navigator.pop(context, true);
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
      appBar: AppBar(title: const Text('New Customer')),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(CrmSpacing.page),
          children: [
            TextFormField(
              controller: _legalCtrl,
              decoration: const InputDecoration(labelText: 'Legal name *'),
              validator: (v) =>
                  v == null || v.trim().isEmpty ? 'Required' : null,
            ),
            const SizedBox(height: CrmSpacing.sm),
            TextFormField(
              controller: _tradeCtrl,
              decoration: const InputDecoration(labelText: 'Trade name'),
            ),
            const SizedBox(height: CrmSpacing.sm),
            TextFormField(
              controller: _notesCtrl,
              decoration: const InputDecoration(labelText: 'Notes'),
              maxLines: 3,
            ),
            const SizedBox(height: CrmSpacing.lg),
            FilledButton(
              onPressed: _saving ? null : _save,
              child: _saving
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text('Create customer'),
            ),
          ],
        ),
      ),
    );
  }
}
