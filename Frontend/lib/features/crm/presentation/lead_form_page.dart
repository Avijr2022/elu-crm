import 'package:flutter/material.dart';

import '../../../core/theme/crm_theme.dart';
import '../data/lead_model.dart';
import 'lead_form_controller.dart';
import 'widgets/lead_form_fields.dart';

class LeadFormPage extends StatefulWidget {
  const LeadFormPage({super.key, this.leadId});

  final String? leadId;

  @override
  State<LeadFormPage> createState() => _LeadFormPageState();
}

class _LeadFormPageState extends State<LeadFormPage>
    with SingleTickerProviderStateMixin {
  late final LeadFormController _controller;
  late final TabController _tabs;
  final _formKey = GlobalKey<FormState>();
  final _nameCtrl = TextEditingController();
  final _companyCtrl = TextEditingController();
  final _emailCtrl = TextEditingController();
  final _phoneCtrl = TextEditingController();
  final _valueCtrl = TextEditingController(text: '0');
  final _notesCtrl = TextEditingController();
  String _status = 'NEW';
  bool _populated = false;

  @override
  void initState() {
    super.initState();
    _controller = LeadFormController(leadId: widget.leadId);
    _tabs = TabController(length: 3, vsync: this);
    if (widget.leadId != null) {
      _controller.loadExisting();
    }
  }

  @override
  void dispose() {
    _tabs.dispose();
    _controller.dispose();
    _nameCtrl.dispose();
    _companyCtrl.dispose();
    _emailCtrl.dispose();
    _phoneCtrl.dispose();
    _valueCtrl.dispose();
    _notesCtrl.dispose();
    super.dispose();
  }

  void _populateFromLead(Lead lead) {
    if (_populated) return;
    _populated = true;
    _nameCtrl.text = lead.fullName;
    _companyCtrl.text = lead.companyName ?? '';
    _emailCtrl.text = lead.email ?? '';
    _phoneCtrl.text = lead.phone ?? '';
    _valueCtrl.text = lead.estimatedValue.toString();
    _notesCtrl.text = lead.notes ?? '';
    _status = lead.status;
  }

  Future<void> _submit() async {
    if (_controller.isTerminal) return;
    if (!_formKey.currentState!.validate()) return;

    final fullName = _nameCtrl.text.trim();
    final company = _companyCtrl.text.trim();
    final email = _emailCtrl.text.trim();
    final phone = _phoneCtrl.text.trim();
    final notes = _notesCtrl.text.trim();
    final value = double.tryParse(_valueCtrl.text.trim()) ?? 0;

    final Lead? result;
    if (_controller.isEditMode) {
      result = await _controller.update(
        fullName: fullName,
        companyName: company,
        email: email,
        phone: phone,
        status: _status,
        estimatedValue: value,
        notes: notes,
      );
    } else {
      result = await _controller.create(
        fullName: fullName,
        companyName: company,
        email: email,
        phone: phone,
        status: _status,
        estimatedValue: value,
        notes: notes,
      );
    }

    if (!mounted) return;
    if (result != null) {
      Navigator.of(context).pop(true);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, _) {
        if (_controller.existing != null) {
          _populateFromLead(_controller.existing!);
        }

        if (_controller.isEditMode &&
            _controller.loading &&
            _controller.existing == null) {
          return Scaffold(
            appBar: AppBar(title: const Text('Edit Lead')),
            body: const Center(child: CircularProgressIndicator()),
          );
        }

        if (_controller.isEditMode &&
            _controller.error != null &&
            _controller.existing == null) {
          return Scaffold(
            appBar: AppBar(title: const Text('Edit Lead')),
            body: Center(
              child: Padding(
                padding: const EdgeInsets.all(CrmSpacing.lg),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      _controller.error!,
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: Theme.of(context).colorScheme.error,
                      ),
                    ),
                    const SizedBox(height: CrmSpacing.md),
                    FilledButton(
                      onPressed: _controller.loadExisting,
                      child: const Text('Retry'),
                    ),
                  ],
                ),
              ),
            ),
          );
        }

        final title =
            _controller.isEditMode ? 'Edit Lead' : 'Add Lead';
        final readOnly = _controller.isTerminal;

        return Scaffold(
          appBar: AppBar(
            title: Text(title),
            bottom: TabBar(
              controller: _tabs,
              tabs: const [
                Tab(text: 'Profile'),
                Tab(text: 'Qualifiers'),
                Tab(text: 'Follow-up'),
              ],
            ),
            actions: [
              if (!readOnly)
                TextButton(
                  onPressed: _controller.saving ? null : _submit,
                  child: _controller.saving
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Save'),
                ),
            ],
          ),
          body: TabBarView(
            controller: _tabs,
            children: [
              _ProfileTab(
                formKey: _formKey,
                error: _controller.error,
                readOnly: readOnly,
                nameCtrl: _nameCtrl,
                companyCtrl: _companyCtrl,
                emailCtrl: _emailCtrl,
                phoneCtrl: _phoneCtrl,
                valueCtrl: _valueCtrl,
                notesCtrl: _notesCtrl,
                status: _status,
                onStatusChanged: (v) => setState(() => _status = v),
              ),
              const _StubTab(
                title: 'Qualifiers',
                message:
                    'Qualification details will be available when the qualification API is ready.',
              ),
              const _StubTab(
                title: 'Follow-up',
                message:
                    'Follow-up scheduling will be available when the activity API is ready.',
              ),
            ],
          ),
        );
      },
    );
  }
}

class _ProfileTab extends StatelessWidget {
  const _ProfileTab({
    required this.formKey,
    required this.error,
    required this.readOnly,
    required this.nameCtrl,
    required this.companyCtrl,
    required this.emailCtrl,
    required this.phoneCtrl,
    required this.valueCtrl,
    required this.notesCtrl,
    required this.status,
    required this.onStatusChanged,
  });

  final GlobalKey<FormState> formKey;
  final String? error;
  final bool readOnly;
  final TextEditingController nameCtrl;
  final TextEditingController companyCtrl;
  final TextEditingController emailCtrl;
  final TextEditingController phoneCtrl;
  final TextEditingController valueCtrl;
  final TextEditingController notesCtrl;
  final String status;
  final ValueChanged<String> onStatusChanged;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(CrmSpacing.page),
      children: [
        if (readOnly)
          Padding(
            padding: const EdgeInsets.only(bottom: CrmSpacing.sm),
            child: Row(
              children: [
                Icon(Icons.info_outline,
                    color: Theme.of(context).colorScheme.outline),
                const SizedBox(width: CrmSpacing.xs),
                Expanded(
                  child: Text(
                    'This lead is in a terminal state and cannot be edited.',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ),
              ],
            ),
          ),
        if (error != null) ...[
          Text(
            error!,
            style: TextStyle(color: Theme.of(context).colorScheme.error),
          ),
          const SizedBox(height: CrmSpacing.sm),
        ],
        Form(
          key: formKey,
          child: LeadFormFields(
            nameCtrl: nameCtrl,
            companyCtrl: companyCtrl,
            emailCtrl: emailCtrl,
            phoneCtrl: phoneCtrl,
            valueCtrl: valueCtrl,
            notesCtrl: notesCtrl,
            status: status,
            onStatusChanged: onStatusChanged,
            readOnly: readOnly,
          ),
        ),
      ],
    );
  }
}

class _StubTab extends StatelessWidget {
  const _StubTab({required this.title, required this.message});

  final String title;
  final String message;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(CrmSpacing.lg),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(title, style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: CrmSpacing.sm),
            Text(
              message,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }
}
