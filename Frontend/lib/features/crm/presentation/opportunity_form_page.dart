import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/crm_theme.dart';
import '../data/opportunity_model.dart';
import 'opportunity_form_controller.dart';

class OpportunityFormPage extends StatefulWidget {
  const OpportunityFormPage({super.key, this.opportunityId});

  final String? opportunityId;

  @override
  State<OpportunityFormPage> createState() => _OpportunityFormPageState();
}

class _OpportunityFormPageState extends State<OpportunityFormPage>
    with SingleTickerProviderStateMixin {
  late final OpportunityFormController _controller;
  late final TabController _tabs;
  final _formKey = GlobalKey<FormState>();
  final _nameCtrl = TextEditingController();
  final _companyCtrl = TextEditingController();
  final _valueCtrl = TextEditingController(text: '0');
  final _notesCtrl = TextEditingController();
  bool _populated = false;

  @override
  void initState() {
    super.initState();
    _controller = OpportunityFormController(opportunityId: widget.opportunityId);
    _tabs = TabController(length: 3, vsync: this);
    if (widget.opportunityId != null) _controller.loadExisting();
  }

  @override
  void dispose() {
    _tabs.dispose();
    _controller.dispose();
    _nameCtrl.dispose();
    _companyCtrl.dispose();
    _valueCtrl.dispose();
    _notesCtrl.dispose();
    super.dispose();
  }

  void _populate(Opportunity o) {
    if (_populated) return;
    _populated = true;
    _nameCtrl.text = o.name;
    _companyCtrl.text = o.companyName ?? '';
    _valueCtrl.text = o.opportunityValue.toString();
    _notesCtrl.text = o.notes ?? '';
  }

  Future<void> _submit() async {
    if (_controller.isTerminal) return;
    if (!_formKey.currentState!.validate()) return;
    final name = _nameCtrl.text.trim();
    final company = _companyCtrl.text.trim();
    final value = double.tryParse(_valueCtrl.text.trim()) ?? 0;
    final notes = _notesCtrl.text.trim();
    final result = _controller.isEditMode
        ? await _controller.saveEdit(
            name: name,
            companyName: company,
            opportunityValue: value,
            notes: notes,
          )
        : await _controller.create(
            name: name,
            companyName: company,
            opportunityValue: value,
            notes: notes,
          );
    if (!mounted) return;
    if (result != null) context.pop(true);
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, _) {
        if (_controller.existing != null) _populate(_controller.existing!);
        if (_controller.loading) {
          return const Scaffold(body: Center(child: CircularProgressIndicator()));
        }
        return Scaffold(
          appBar: AppBar(
            title: Text(_controller.isEditMode ? 'Edit Opportunity' : 'New Opportunity'),
            bottom: TabBar(
              controller: _tabs,
              tabs: const [
                Tab(text: 'Deal'),
                Tab(text: 'Qualifiers'),
                Tab(text: 'Follow-up'),
              ],
            ),
          ),
          body: TabBarView(
            controller: _tabs,
            children: [
              _DealTab(
                formKey: _formKey,
                nameCtrl: _nameCtrl,
                companyCtrl: _companyCtrl,
                valueCtrl: _valueCtrl,
                notesCtrl: _notesCtrl,
                error: _controller.error,
                readOnly: _controller.isTerminal,
              ),
              _stub('Qualification criteria — future release.'),
              _stub('Follow-up scheduling — future release.'),
            ],
          ),
          bottomNavigationBar: _controller.isTerminal
              ? null
              : SafeArea(
                  child: Padding(
                    padding: const EdgeInsets.all(CrmSpacing.md),
                    child: Row(
                      children: [
                        TextButton(
                          onPressed: _controller.saving ? null : () => context.pop(),
                          child: const Text('Cancel'),
                        ),
                        const Spacer(),
                        FilledButton(
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
                  ),
                ),
        );
      },
    );
  }

  Widget _stub(String msg) => Center(child: Text(msg, textAlign: TextAlign.center));
}

class _DealTab extends StatelessWidget {
  const _DealTab({
    required this.formKey,
    required this.nameCtrl,
    required this.companyCtrl,
    required this.valueCtrl,
    required this.notesCtrl,
    this.error,
    this.readOnly = false,
  });

  final GlobalKey<FormState> formKey;
  final TextEditingController nameCtrl;
  final TextEditingController companyCtrl;
  final TextEditingController valueCtrl;
  final TextEditingController notesCtrl;
  final String? error;
  final bool readOnly;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(CrmSpacing.page),
      children: [
        if (error != null) ...[
          Text(error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
          const SizedBox(height: CrmSpacing.sm),
        ],
        Form(
          key: formKey,
          child: Column(
            children: [
              TextFormField(
                controller: nameCtrl,
                readOnly: readOnly,
                decoration: const InputDecoration(labelText: 'Opportunity Name *'),
                validator: (v) =>
                    (v == null || v.trim().isEmpty) ? 'Required' : null,
              ),
              const SizedBox(height: CrmSpacing.sm),
              TextFormField(
                controller: companyCtrl,
                readOnly: readOnly,
                decoration: const InputDecoration(labelText: 'Company'),
              ),
              const SizedBox(height: CrmSpacing.sm),
              TextFormField(
                controller: valueCtrl,
                readOnly: readOnly,
                decoration: const InputDecoration(
                  labelText: 'Opportunity Value (INR)',
                  prefixText: '₹ ',
                ),
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
              ),
              const SizedBox(height: CrmSpacing.sm),
              TextFormField(
                controller: notesCtrl,
                readOnly: readOnly,
                decoration: const InputDecoration(labelText: 'Notes'),
                maxLines: 3,
              ),
            ],
          ),
        ),
      ],
    );
  }
}
