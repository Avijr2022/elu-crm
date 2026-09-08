import 'package:flutter/material.dart';

import '../../../../core/theme/crm_theme.dart';
import '../../data/opportunity_model.dart';

typedef CloseLostConfirm = Future<bool> Function(String lossReason);

class CloseLostWizardDialog extends StatefulWidget {
  const CloseLostWizardDialog({
    super.key,
    required this.opportunity,
    required this.onConfirm,
    required this.formatValue,
  });

  final Opportunity opportunity;
  final CloseLostConfirm onConfirm;
  final String Function(Opportunity) formatValue;

  static Future<bool?> show(
    BuildContext context, {
    required Opportunity opportunity,
    required CloseLostConfirm onConfirm,
    required String Function(Opportunity) formatValue,
  }) {
    return showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (_) => CloseLostWizardDialog(
        opportunity: opportunity,
        onConfirm: onConfirm,
        formatValue: formatValue,
      ),
    );
  }

  @override
  State<CloseLostWizardDialog> createState() => _CloseLostWizardDialogState();
}

class _CloseLostWizardDialogState extends State<CloseLostWizardDialog> {
  int _step = 0;
  bool _submitting = false;
  bool _acknowledged = false;
  final _reasonCtrl = TextEditingController();

  @override
  void dispose() {
    _reasonCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final reason = _reasonCtrl.text.trim();
    if (reason.isEmpty) return;
    setState(() => _submitting = true);
    final ok = await widget.onConfirm(reason);
    if (!mounted) return;
    setState(() => _submitting = false);
    if (ok) setState(() => _step = 2);
  }

  @override
  Widget build(BuildContext context) {
    final opp = widget.opportunity;
    return AlertDialog(
      title: Text(_step == 2 ? 'Closed Lost' : 'Close Lost — Step ${_step + 1} of 2'),
      content: SizedBox(
        width: 420,
        child: _step == 0
            ? Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(opp.name, style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: CrmSpacing.sm),
                  Text('Number: ${opp.opportunityNumber}'),
                  Text('Stage: ${opp.stage.replaceAll('_', ' ')}'),
                  Text('Value: ${widget.formatValue(opp)}'),
                ],
              )
            : _step == 1
                ? Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      TextField(
                        controller: _reasonCtrl,
                        decoration: const InputDecoration(
                          labelText: 'Loss reason *',
                          hintText: 'Why was this deal lost?',
                        ),
                        maxLines: 2,
                        enabled: !_submitting,
                      ),
                      const SizedBox(height: CrmSpacing.sm),
                      CheckboxListTile(
                        contentPadding: EdgeInsets.zero,
                        value: _acknowledged,
                        onChanged: _submitting
                            ? null
                            : (v) => setState(() => _acknowledged = v ?? false),
                        title: const Text('I confirm closing this opportunity as lost'),
                        controlAffinity: ListTileControlAffinity.leading,
                      ),
                    ],
                  )
                : const Text('Opportunity marked as CLOSED LOST.'),
      ),
      actions: [
        if (_step < 2)
          TextButton(
            onPressed: _submitting ? null : () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
        if (_step == 0)
          FilledButton(
            onPressed: () => setState(() => _step = 1),
            child: const Text('Next'),
          ),
        if (_step == 1)
          FilledButton(
            onPressed: (!_acknowledged ||
                    _reasonCtrl.text.trim().isEmpty ||
                    _submitting)
                ? null
                : _submit,
            child: _submitting
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Text('Close Lost'),
          ),
        if (_step == 2)
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Done'),
          ),
      ],
    );
  }
}
