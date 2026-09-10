import 'package:flutter/material.dart';

import '../../../../core/theme/crm_theme.dart';
import '../../data/quotation_service.dart';

class QuotationLineDialog extends StatefulWidget {
  const QuotationLineDialog({super.key, this.line});

  final QuotationLine? line;

  static Future<Map<String, String>?> show(BuildContext context, {QuotationLine? line}) {
    return showDialog<Map<String, String>>(
      context: context,
      builder: (_) => QuotationLineDialog(line: line),
    );
  }

  @override
  State<QuotationLineDialog> createState() => _QuotationLineDialogState();
}

class _QuotationLineDialogState extends State<QuotationLineDialog> {
  late final TextEditingController _descCtrl;
  late final TextEditingController _qtyCtrl;
  late final TextEditingController _priceCtrl;
  late String _taxCode;

  @override
  void initState() {
    super.initState();
    final line = widget.line;
    _descCtrl = TextEditingController(text: line?.description ?? '');
    _qtyCtrl = TextEditingController(text: line?.qty ?? '1');
    _priceCtrl = TextEditingController(text: line?.unitPrice ?? '0');
    _taxCode = line?.taxCode ?? 'GST18';
  }

  @override
  void dispose() {
    _descCtrl.dispose();
    _qtyCtrl.dispose();
    _priceCtrl.dispose();
    super.dispose();
  }

  void _save() {
    if (_descCtrl.text.trim().isEmpty) return;
    Navigator.pop(context, {
      'description': _descCtrl.text.trim(),
      'qty': _qtyCtrl.text.trim(),
      'unit_price': _priceCtrl.text.trim(),
      'tax_code': _taxCode,
    });
  }

  @override
  Widget build(BuildContext context) {
    final editing = widget.line != null;
    return AlertDialog(
      title: Text(editing ? 'Edit line' : 'Add line'),
      content: SizedBox(
        width: 360,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: _descCtrl,
              decoration: const InputDecoration(labelText: 'Description *'),
              autofocus: true,
            ),
            const SizedBox(height: CrmSpacing.sm),
            TextField(
              controller: _qtyCtrl,
              decoration: const InputDecoration(labelText: 'Qty'),
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
            ),
            const SizedBox(height: CrmSpacing.sm),
            TextField(
              controller: _priceCtrl,
              decoration: const InputDecoration(labelText: 'Unit price'),
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
            ),
            const SizedBox(height: CrmSpacing.sm),
            DropdownButtonFormField<String>(
              value: _taxCode,
              decoration: const InputDecoration(labelText: 'Tax code'),
              items: const [
                DropdownMenuItem(value: 'GST18', child: Text('GST 18%')),
                DropdownMenuItem(value: 'GST12', child: Text('GST 12%')),
                DropdownMenuItem(value: 'GST5', child: Text('GST 5%')),
                DropdownMenuItem(value: 'EXEMPT', child: Text('Exempt')),
              ],
              onChanged: (v) => setState(() => _taxCode = v ?? 'GST18'),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
        FilledButton(onPressed: _save, child: Text(editing ? 'Save' : 'Add')),
      ],
    );
  }
}

Future<void> addQuotationLine(BuildContext context, QuotationService service, String quotationId) async {
  final data = await QuotationLineDialog.show(context);
  if (data == null) return;
  await service.addLine(
    quotationId,
    description: data['description']!,
    qty: data['qty']!,
    unitPrice: data['unit_price']!,
    taxCode: data['tax_code']!,
  );
}

Future<void> editQuotationLine(
  BuildContext context,
  QuotationService service,
  String quotationId,
  QuotationLine line,
) async {
  final data = await QuotationLineDialog.show(context, line: line);
  if (data == null) return;
  await service.updateLine(
    quotationId,
    line.quotationLineId,
    description: data['description']!,
    qty: data['qty']!,
    unitPrice: data['unit_price']!,
    taxCode: data['tax_code']!,
  );
}
