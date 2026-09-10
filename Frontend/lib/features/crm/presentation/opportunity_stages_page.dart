import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/auth/auth_controller.dart';
import '../../../core/auth/crm_rbac.dart';
import '../../../core/theme/crm_theme.dart';
import '../data/lookup_service.dart';

class OpportunityStagesPage extends StatefulWidget {
  const OpportunityStagesPage({super.key});

  @override
  State<OpportunityStagesPage> createState() => _OpportunityStagesPageState();
}

class _OpportunityStagesPageState extends State<OpportunityStagesPage> {
  final _service = LookupService();
  bool _loading = true;
  bool _savingOrder = false;
  String? _error;
  List<OpportunityStage> _stages = [];

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
      final items = await _service.listOpportunityStages(includeInactive: true);
      if (!mounted) return;
      setState(() {
        _stages = items;
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

  Future<void> _toggle(OpportunityStage stage, bool active) async {
    try {
      await _service.updateOpportunityStage(stage.opportunityStageId, isActive: active);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('${stage.code} ${active ? 'activated' : 'deactivated'}')),
      );
      await _load();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  Future<void> _onReorder(int oldIndex, int newIndex) async {
    if (newIndex > oldIndex) newIndex -= 1;
    final updated = List<OpportunityStage>.from(_stages);
    final item = updated.removeAt(oldIndex);
    updated.insert(newIndex, item);
    setState(() {
      _stages = updated;
      _savingOrder = true;
    });
    try {
      await _service.reorderOpportunityStages(
        updated.map((s) => s.opportunityStageId).toList(),
      );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Pipeline order updated')),
      );
      await _load();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
      await _load();
    } finally {
      if (mounted) setState(() => _savingOrder = false);
    }
  }

  Future<void> _addStage() async {
    final codeCtrl = TextEditingController();
    final nameCtrl = TextEditingController();
    final probCtrl = TextEditingController(text: '0');
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Add pipeline stage'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: codeCtrl,
              decoration: const InputDecoration(
                labelText: 'Code *',
                hintText: 'e.g. PILOT',
              ),
              textCapitalization: TextCapitalization.characters,
            ),
            TextField(
              controller: nameCtrl,
              decoration: const InputDecoration(labelText: 'Name *'),
            ),
            TextField(
              controller: probCtrl,
              decoration: const InputDecoration(
                labelText: 'Default probability %',
              ),
              keyboardType: TextInputType.number,
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          FilledButton(
            onPressed: () {
              if (codeCtrl.text.trim().isEmpty || nameCtrl.text.trim().isEmpty) return;
              Navigator.pop(ctx, true);
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
    if (ok != true) {
      codeCtrl.dispose();
      nameCtrl.dispose();
      probCtrl.dispose();
      return;
    }
    try {
      await _service.createOpportunityStage(
        code: codeCtrl.text.trim(),
        name: nameCtrl.text.trim(),
        defaultProbability: int.tryParse(probCtrl.text.trim()) ?? 0,
      );
      codeCtrl.dispose();
      nameCtrl.dispose();
      probCtrl.dispose();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Pipeline stage created')),
      );
      await _load();
    } catch (e) {
      codeCtrl.dispose();
      nameCtrl.dispose();
      probCtrl.dispose();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final profile = context.watch<AuthController>().profile;
    final canEdit = CrmRbac.isManager(profile?['role_code'] as String?);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Pipeline stages'),
        actions: [
          if (_savingOrder)
            const Padding(
              padding: EdgeInsets.all(12),
              child: SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(strokeWidth: 2),
              ),
            ),
        ],
      ),
      floatingActionButton: canEdit
          ? FloatingActionButton(
              onPressed: _addStage,
              child: const Icon(Icons.add),
            )
          : null,
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!))
              : RefreshIndicator(
                  onRefresh: _load,
                  child: canEdit
                      ? ReorderableListView.builder(
                          padding: const EdgeInsets.all(CrmSpacing.page),
                          itemCount: _stages.length,
                          onReorder: _savingOrder ? (_, __) {} : _onReorder,
                          itemBuilder: (_, i) {
                            final s = _stages[i];
                            return _StageTile(
                              key: ValueKey(s.opportunityStageId),
                              index: i,
                              stage: s,
                              canEdit: canEdit,
                              onToggle: (v) => _toggle(s, v),
                            );
                          },
                        )
                      : ListView.separated(
                          padding: const EdgeInsets.all(CrmSpacing.page),
                          itemCount: _stages.length,
                          separatorBuilder: (_, __) => const Divider(),
                          itemBuilder: (_, i) {
                            final s = _stages[i];
                            return _StageTile(
                              stage: s,
                              canEdit: false,
                              onToggle: null,
                            );
                          },
                        ),
                ),
    );
  }
}

class _StageTile extends StatelessWidget {
  const _StageTile({
    super.key,
    this.index = 0,
    required this.stage,
    required this.canEdit,
    this.onToggle,
  });

  final int index;
  final OpportunityStage stage;
  final bool canEdit;
  final ValueChanged<bool>? onToggle;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: CrmSpacing.sm),
      child: ListTile(
        leading: canEdit
            ? ReorderableDragStartListener(
                index: index,
                child: const Icon(Icons.drag_handle),
              )
            : null,
        title: Text(stage.name),
        subtitle: Text(
          '${stage.code} · ${stage.defaultProbability}% · seq ${stage.sequenceNo}',
        ),
        trailing: Switch(
          value: stage.isActive,
          onChanged: canEdit ? onToggle : null,
        ),
      ),
    );
  }
}
