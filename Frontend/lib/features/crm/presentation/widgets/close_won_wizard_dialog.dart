import 'package:flutter/material.dart';

import '../../../../core/theme/crm_theme.dart';
import '../../data/opportunity_model.dart';

typedef CloseWonConfirm = Future<bool> Function({String? closingNotes});

class CloseWonWizardDialog extends StatefulWidget {
  const CloseWonWizardDialog({
    super.key,
    required this.opportunity,
    required this.onConfirm,
    required this.formatValue,
  });

  final Opportunity opportunity;
  final CloseWonConfirm onConfirm;
  final String Function(Opportunity) formatValue;

  static Future<bool?> show(
    BuildContext context, {
    required Opportunity opportunity,
    required CloseWonConfirm onConfirm,
    required String Function(Opportunity) formatValue,
  }) {
    return showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (_) => CloseWonWizardDialog(
        opportunity: opportunity,
        onConfirm: onConfirm,
        formatValue: formatValue,
      ),
    );
  }

  @override
  State<CloseWonWizardDialog> createState() => _CloseWonWizardDialogState();
}

class _CloseWonWizardDialogState extends State<CloseWonWizardDialog> {
  int _step = 0;
  bool _submitting = false;
  bool _acknowledged = false;
  final _notesCtrl = TextEditingController();

  @override
  void dispose() {
    _notesCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    setState(() => _submitting = true);
    final ok = await widget.onConfirm(
      closingNotes: _notesCtrl.text.trim().isEmpty ? null : _notesCtrl.text.trim(),
    );
    if (!mounted) return;
    setState(() => _submitting = false);
    if (ok) {
      setState(() => _step = 2);
    }
  }

  @override
  Widget build(BuildContext context) {
    final opp = widget.opportunity;
    return AlertDialog(
      title: Text(_step == 2 ? 'Closed Won' : 'Close Won — Step ${_step + 1} of 2'),
      content: SizedBox(
        width: 420,
        child: _step == 0
            ? _ReviewStep(opportunity: opp, formatValue: widget.formatValue)
            : _step == 1
                ? _ConfirmStep(
                    acknowledged: _acknowledged,
                    notesCtrl: _notesCtrl,
                    onAckChanged: (v) => setState(() => _acknowledged = v),
                  )
                : const Text(
                    'Opportunity closed won. A customer record and activity log entry were created.',
                  ),
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
            onPressed: (!_acknowledged || _submitting) ? null : _submit,
            child: _submitting
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Text('Close Won'),
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

class _ReviewStep extends StatelessWidget {
  const _ReviewStep({
    required this.opportunity,
    required this.formatValue,
  });

  final Opportunity opportunity;
  final String Function(Opportunity) formatValue;

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(opportunity.name, style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: CrmSpacing.sm),
        _row('Number', opportunity.opportunityNumber),
        _row('Stage', opportunity.stage.replaceAll('_', ' ')),
        _row('Value', formatValue(opportunity)),
        _row('Probability', '${opportunity.probability}%'),
        if (opportunity.companyName != null)
          _row('Company', opportunity.companyName!),
      ],
    );
  }

  Widget _row(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: CrmSpacing.xs),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(label, style: const TextStyle(fontWeight: FontWeight.w600)),
          ),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }
}

class _ConfirmStep extends StatelessWidget {
  const _ConfirmStep({
    required this.acknowledged,
    required this.notesCtrl,
    required this.onAckChanged,
  });

  final bool acknowledged;
  final TextEditingController notesCtrl;
  final ValueChanged<bool> onAckChanged;

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Closing won will:',
          style: TextStyle(fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: CrmSpacing.xs),
        const Text('• Mark this opportunity as CLOSED WON'),
        const Text('• Create a customer account (if not already linked)'),
        const Text('• Log a system activity on the opportunity'),
        const Text('• Queue PRJ delivery handoff when Projects edition is enabled'),
        const SizedBox(height: CrmSpacing.md),
        TextField(
          controller: notesCtrl,
          decoration: const InputDecoration(
            labelText: 'Closing notes (optional)',
            hintText: 'Add context for the win',
          ),
          maxLines: 2,
        ),
        const SizedBox(height: CrmSpacing.sm),
        CheckboxListTile(
          contentPadding: EdgeInsets.zero,
          value: acknowledged,
          onChanged: (v) => onAckChanged(v ?? false),
          title: const Text('I confirm this deal is won'),
          controlAffinity: ListTileControlAffinity.leading,
        ),
      ],
    );
  }
}
