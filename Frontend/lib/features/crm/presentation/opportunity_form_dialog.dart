import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'opportunities_controller.dart';

Future<bool?> showOpportunityFormDialog(
  BuildContext context,
  OpportunitiesController controller,
) {
  return showDialog<bool>(
    context: context,
    barrierDismissible: false,
    builder: (_) => _OpportunityFormDialog(controller: controller),
  );
}

class _OpportunityFormDialog extends StatefulWidget {
  const _OpportunityFormDialog({required this.controller});

  final OpportunitiesController controller;

  @override
  State<_OpportunityFormDialog> createState() => _OpportunityFormDialogState();
}

class _OpportunityFormDialogState extends State<_OpportunityFormDialog> {
  final _formKey = GlobalKey<FormState>();
  final _nameCtrl = TextEditingController();
  final _companyCtrl = TextEditingController();
  final _valueCtrl = TextEditingController(text: '0');
  final _notesCtrl = TextEditingController();
  bool _saving = false;
  String? _error;

  @override
  void dispose() {
    _nameCtrl.dispose();
    _companyCtrl.dispose();
    _valueCtrl.dispose();
    _notesCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      _saving = true;
      _error = null;
    });
    final opp = await widget.controller.createOpportunity(
      name: _nameCtrl.text.trim(),
      companyName: _companyCtrl.text.trim(),
      opportunityValue: double.tryParse(_valueCtrl.text.trim()) ?? 0,
      notes: _notesCtrl.text.trim(),
    );
    if (!mounted) return;
    if (opp == null) {
      setState(() {
        _saving = false;
        _error = widget.controller.error ?? 'Could not create opportunity';
      });
      return;
    }
    Navigator.of(context).pop(true);
  }

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.sizeOf(context).width;
    return AlertDialog(
      title: const Text('Add Opportunity'),
      content: SizedBox(
        width: width > 720 ? 520 : width * 0.9,
        child: Form(
          key: _formKey,
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (_error != null) ...[
                  Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      _error!,
                      style: TextStyle(color: Theme.of(context).colorScheme.error),
                    ),
                  ),
                  const SizedBox(height: 8),
                ],
                TextFormField(
                  controller: _nameCtrl,
                  decoration: const InputDecoration(labelText: 'Opportunity Name *'),
                  validator: (v) =>
                      (v == null || v.trim().isEmpty) ? 'Required' : null,
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _companyCtrl,
                  decoration: const InputDecoration(labelText: 'Company'),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _valueCtrl,
                  decoration: const InputDecoration(
                    labelText: 'Opportunity Value (INR)',
                    prefixText: '₹ ',
                  ),
                  keyboardType:
                      const TextInputType.numberWithOptions(decimal: true),
                  inputFormatters: [
                    FilteringTextInputFormatter.allow(RegExp(r'[0-9.]')),
                  ],
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _notesCtrl,
                  decoration: const InputDecoration(labelText: 'Notes'),
                  maxLines: 3,
                ),
              ],
            ),
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: _saving ? null : () => Navigator.of(context).pop(false),
          child: const Text('Cancel'),
        ),
        FilledButton(
          onPressed: _saving ? null : _submit,
          child: _saving
              ? const SizedBox(
                  width: 18,
                  height: 18,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text('Save'),
        ),
      ],
    );
  }
}
